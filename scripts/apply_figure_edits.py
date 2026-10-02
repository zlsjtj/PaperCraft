"""Replace explicitly bound DOCX figure media without rewriting any XML.

Usage: apply_figure_edits.py source.docx manifest.json destination.docx
                           --receipt receipt.json

Manifest (SHA values are full SHA-256 hex digests):
  {"source_sha256": "...", "replacements": [
    {"drawing_index": 1, "representations": [
      {"kind": "primary", "part": "word/media/image1.png",
       "old_media_sha256": "...", "source_asset": "exports/figure.png",
       "source_asset_sha256": "..."},
      {"kind": "svg", "part": "word/media/image2.svg",
       "old_media_sha256": "...", "source_asset": "exports/figure.svg",
       "source_asset_sha256": "..."}]}]}

Indices are one-based document.xml //w:drawing order, bound to the source hash.
Each selected drawing must declare every existing representation exactly once.
Only PNG primary images, optionally with an SVG alternative, are supported.
Asset paths are relative to the manifest. New intrinsic aspect ratios must be
within 1% of the existing wp:extent; extents and all XML remain byte-identical.
VML, AlternateContent, shared media and unknown image forms are refused.
Destination and receipt must be new files. Caption/text edits use the authored
text route. A PASS receipt proves technical identity, never quality or approval.
Non-media ZIP member contents stay byte-identical; ZIP container bytes may differ.
"""

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import posixpath
import re
from urllib.parse import unquote, urlsplit
import zipfile
from xml.etree import ElementTree as E

from PIL import Image

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
SVG = 'http://schemas.microsoft.com/office/drawing/2016/SVG/main'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS = {'w': W, 'a': A, 'wp': WP}
DOCUMENT = 'word/document.xml'
DOCUMENT_RELS = 'word/_rels/document.xml.rels'
IMAGE_REL = R + '/image'
MEDIA = re.compile(r'word/media/[^/\\]+\.(png|svg)\Z', re.I)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', value):
        raise ValueError(label + ': mandatory SHA-256 digest missing or invalid')
    return value.lower()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate manifest key: ' + key)
        result[key] = value
    return result


def xml(data, label):
    # The narrow adapter does not need entity declarations or DTDs.
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('Unsupported XML declaration: ' + label)
    return E.fromstring(data)


def target_part(rels_name, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or '\\' in target:
        raise ValueError('Unsupported internal relationship target: ' + target)
    path = unquote(parsed.path)
    if '\\' in path or '\x00' in path:
        raise ValueError('Unsafe relationship target')
    base = '' if rels_name == '_rels/.rels' else posixpath.dirname(posixpath.dirname(rels_name))
    resolved = posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(base, path))
    if resolved in ('', '.', '..') or resolved.startswith('../'):
        raise ValueError('Relationship target escapes package')
    return resolved


def relationships(parts):
    result = {}
    for name, data in parts.items():
        if not name.endswith('.rels'):
            continue
        root = xml(data, name)
        if root.tag != '{' + REL + '}Relationships':
            raise ValueError('Unsupported relationship namespace: ' + name)
        rows = {}
        for node in root:
            rid = node.get('Id')
            if node.tag != '{' + REL + '}Relationship' or not rid or rid in rows:
                raise ValueError('Invalid or duplicate relationship: ' + name)
            mode = node.get('TargetMode', 'Internal')
            if mode not in ('Internal', 'External') or not node.get('Target'):
                raise ValueError('Invalid relationship mode or target: ' + name)
            rows[rid] = (node, None if mode == 'External' else target_part(name, node.get('Target')))
        result[name] = rows
    return result


def svg_ratio(root):
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Asset is not an SVG image')
    viewbox = root.get('viewBox')
    if viewbox:
        values = [float(v) for v in re.split(r'[\s,]+', viewbox.strip())]
        if len(values) != 4 or min(values[2:]) <= 0:
            raise ValueError('Invalid SVG viewBox')
        ratio = values[2] / values[3]
    else:
        ratio = None
    # Explicit physical dimensions control the SVG viewport when both exist.
    def length(value):
        m = re.fullmatch(r'\s*([\d.]+)\s*(px|mm|cm|in|pt|pc)?\s*', value or '')
        if not m:
            raise ValueError('SVG needs a numeric viewBox or absolute width/height')
        return float(m[1]) * {'px': 1, 'mm': 96/25.4, 'cm': 96/2.54, 'in': 96, 'pt': 96/72, 'pc': 16, None: 1}[m[2]]
    if root.get('width') and root.get('height'):
        try:
            width, height = length(root.get('width')), length(root.get('height'))
        except ValueError:
            if ratio is None:
                raise
        else:
            if min(width, height) <= 0:
                raise ValueError('Non-positive SVG dimensions')
            ratio = width / height
    if ratio is None or not 0 < ratio < float('inf'):
        raise ValueError('Invalid SVG dimensions')
    return ratio


def asset_ratio(data, suffix):
    if suffix == '.png':
        with Image.open(io.BytesIO(data)) as im:
            if im.format != 'PNG' or getattr(im, 'n_frames', 1) != 1:
                raise ValueError('Asset is not a single-frame PNG')
            im.verify()
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            return im.width / im.height
    return svg_ratio(xml(data, 'SVG asset'))


def apply(source, manifest, destination, receipt):
    source, manifest, destination, receipt = map(Path, (source, manifest, destination, receipt))
    outputs = [destination.resolve(), receipt.resolve()]
    if len(set(outputs)) != 2 or any(p in (source.resolve(), manifest.resolve()) for p in outputs):
        raise ValueError('Output cannot overwrite input or another output')
    if any(p.exists() or p.is_symlink() for p in (destination, receipt)):
        raise ValueError('Destination and receipt must be new files')
    original, manifest_bytes = source.read_bytes(), manifest.read_bytes()
    spec = json.loads(manifest_bytes.decode('utf-8-sig'), object_pairs_hook=unique_object)
    if not isinstance(spec, dict) or set(spec) != {'source_sha256', 'replacements'}:
        raise ValueError('Manifest requires source_sha256 and replacements only')
    if digest(spec['source_sha256'], 'source') != sha(original):
        raise ValueError('Source DOCX SHA-256 mismatch')
    rows = spec['replacements']
    if not isinstance(rows, list) or not rows:
        raise ValueError('At least one replacement is required')
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if len(set(names)) != len(names):
            raise ValueError('Duplicate ZIP member')
        if any(n.startswith('/') or '\\' in n or '..' in PurePosixPath(n).parts for n in names):
            raise ValueError('Unsafe ZIP member name')
        parts = {i.filename: archive.read(i) for i in infos}
        archive_comment = archive.comment
    if any(n.startswith('_xmlsignatures/') for n in parts):
        raise ValueError('Digitally signed packages require separate review')
    trees = {n: xml(b, n) for n, b in parts.items() if n.endswith(('.xml', '.vml'))}
    unsupported = {'{urn:schemas-microsoft-com:vml}imagedata',
                   '{urn:schemas-microsoft-com:vml}shape',
                   '{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent'}
    if any(node.tag in unsupported for tree in trees.values() for node in tree.iter()):
        raise ValueError('VML or AlternateContent is unsupported')
    root = trees[DOCUMENT]
    drawings = root.findall('.//w:drawing', NS)
    rels = relationships(parts)
    doc_rels = rels.get(DOCUMENT_RELS, {})
    content_types = trees['[Content_Types].xml']
    defaults = {n.get('Extension').lower(): n.get('ContentType') for n in content_types if n.tag == '{' + CT + '}Default'}
    overrides = {n.get('PartName'): n.get('ContentType') for n in content_types if n.tag == '{' + CT + '}Override'}
    replacements, allowed_refs, used_indices, reports = {}, set(), set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) - {'drawing_index', 'representations', 'id', 'reason'}:
            raise ValueError('Invalid replacement fields')
        index = row.get('drawing_index')
        if type(index) is not int or not 1 <= index <= len(drawings) or index in used_indices:
            raise ValueError('Missing, invalid or repeated drawing_index')
        used_indices.add(index)
        drawing = drawings[index - 1]
        primary = drawing.findall('.//a:blip', NS)
        alternatives = list(drawing.iter('{' + SVG + '}svgBlip'))
        extents = drawing.findall('.//wp:extent', NS)
        if len(primary) != 1 or len(alternatives) > 1 or len(extents) != 1:
            raise ValueError('Unsupported drawing structure: ' + str(index))
        cx, cy = (int(extents[0].get(k, '0')) for k in ('cx', 'cy'))
        if min(cx, cy) <= 0:
            raise ValueError('Non-positive drawing extent')
        nodes = [('primary', primary[0])] + [('svg', n) for n in alternatives]
        known_refs = {(id(n), '{' + R + '}embed') for _, n in nodes}
        for node in drawing.iter():
            for attr in node.attrib:
                if attr.startswith('{' + R + '}') and (id(node), attr) not in known_refs:
                    raise ValueError('Unsupported drawing relationship or representation')
        declared = row.get('representations')
        if not isinstance(declared, list) or not all(isinstance(r, dict) for r in declared):
            raise ValueError('Every existing representation must be declared')
        kinds = [r.get('kind') for r in declared]
        if len(kinds) != len(set(kinds)) or set(kinds) != {kind for kind, _ in nodes}:
            raise ValueError('Missing, extra or duplicate representation')
        by_kind = {r['kind']: r for r in declared}
        for kind, node in nodes:
            rep = by_kind[kind]
            if set(rep) != {'kind', 'part', 'old_media_sha256', 'source_asset', 'source_asset_sha256'}:
                raise ValueError('Representation requires exact identity and asset fields')
            rid = node.get('{' + R + '}embed')
            rel, part = doc_rels.get(rid, (None, None))
            if rel is None or part is None or rel.get('Type') != IMAGE_REL:
                raise ValueError('Missing, external or non-image relationship')
            suffix = PurePosixPath(part).suffix.lower()
            if not MEDIA.fullmatch(part) or suffix != ('.png' if kind == 'primary' else '.svg'):
                raise ValueError('Unsupported media target or extension')
            if rep['part'] != part or part not in parts:
                raise ValueError('Media part identity mismatch')
            if part in replacements:
                raise ValueError('Repeated media replacement; shared targets need separate review')
            mime = overrides.get('/' + part, defaults.get(suffix[1:]))
            if mime != {'.png': 'image/png', '.svg': 'image/svg+xml'}[suffix]:
                raise ValueError('Media extension/content type incompatibility')
            if digest(rep['old_media_sha256'], part) != sha(parts[part]):
                raise ValueError('Old media SHA-256 mismatch: ' + part)
            path_value = rep['source_asset']
            if not isinstance(path_value, str) or not path_value or Path(path_value).is_absolute() or PureWindowsPath(path_value).drive:
                raise ValueError('Asset paths must be relative to the manifest')
            asset = manifest.resolve().parent / path_value
            if asset.suffix.lower() != suffix:
                raise ValueError('Asset extension incompatibility')
            payload = asset.read_bytes()
            if digest(rep['source_asset_sha256'], str(asset)) != sha(payload):
                raise ValueError('New asset SHA-256 mismatch: ' + str(asset))
            ratio = asset_ratio(payload, suffix)
            if abs(ratio / (cx / cy) - 1) > 0.01:
                raise ValueError('New asset aspect ratio differs from existing placement by more than 1%')
            if payload == parts[part]:
                raise ValueError('Replacement still contains old media bytes: ' + part)
            replacements[part] = payload
            allowed_refs.add((id(node), '{' + R + '}embed'))
            reports.append({'drawing_index': index, 'kind': kind, 'part': part,
                            'old_media_sha256': sha(parts[part]), 'new_media_sha256': sha(payload),
                            'source_asset': path_value, 'placement_emu': [cx, cy]})
    # Every relationship to changed media must belong to exactly the selected
    # image nodes. This also catches header/footer/chart and unselected aliases.
    for name, rows_by_id in rels.items():
        for rid, (_, part) in rows_by_id.items():
            if part not in replacements:
                continue
            if name != DOCUMENT_RELS:
                raise ValueError('Shared media referenced elsewhere in package: ' + name)
            usages = [(id(node), attr) for node in root.iter() for attr, value in node.attrib.items()
                      if attr.startswith('{' + R + '}') and value == rid]
            if not usages or any(u not in allowed_refs for u in usages):
                raise ValueError('Shared media referenced by an unselected drawing or object')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as output:
        output.comment = archive_comment
        for info in infos:
            output.writestr(copy.copy(info), replacements.get(info.filename, parts[info.filename]))
    built = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(built)) as check:
        if check.namelist() != names or check.comment != archive_comment:
            raise ValueError('Package member inventory changed')
        if any(check.read(n) != replacements.get(n, parts[n]) for n in names):
            raise ValueError('Package byte preservation check failed')
    result = {'technical_status': 'PASS', 'overall_status': 'REVIEW_REQUIRED',
              'source_sha256': sha(original), 'manifest_sha256': sha(manifest_bytes),
              'destination_sha256': sha(built), 'builder_sha256': sha(Path(__file__).read_bytes()),
              'replacements': reports, 'changed_parts': sorted(replacements),
              'unchanged_members': len(parts) - len(replacements),
              'document_xml_unchanged': True, 'quality_review': 'NOT_PERFORMED',
              'author_acceptance': 'NOT_RECORDED',
              'limits': ['Technical media identity and package preservation only.',
                         'Science, matching PNG/SVG appearance and rendered page quality require separate review.']}
    receipt_bytes = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    created = []
    try:
        for path, payload in ((destination, built), (receipt, receipt_bytes)):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                created.append(path)
                handle.write(payload)
    except BaseException:
        for path in created:
            path.unlink()
        raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = apply(args.source, args.manifest, args.destination, args.receipt)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, zipfile.BadZipFile, E.ParseError) as exc:
        parser.exit(1, 'Figure replacement refused: ' + str(exc) + '\n')
    print(json.dumps({'technical_status': result['technical_status'],
                      'destination': str(args.destination), 'receipt': str(args.receipt)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
