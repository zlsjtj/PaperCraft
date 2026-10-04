"""导出确切 Word 的 PDF 和逐页 PNG；渲染成功不等于视觉审阅通过。"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def resolve_program(explicit, name):
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise ValueError(f'指定程序不存在：{explicit}')
        return str(path.resolve())
    found = shutil.which(name)
    if not found and name == 'soffice' and os.name == 'nt':
        path = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'LibreOffice/program/soffice.exe'
        found = str(path) if path.is_file() else None
    if not found and name == 'soffice':
        path = Path('/Applications/LibreOffice.app/Contents/MacOS/soffice')
        found = str(path) if path.is_file() else None
    if not found:
        raise ValueError(f'找不到 {name}，请提供程序路径或加入 PATH。')
    return found


def standalone(source, output, soffice, pdftoppm, dpi, timeout=120):
    """独立 Office profile 避免连接已运行的 LibreOffice。"""
    commands = []
    with tempfile.TemporaryDirectory(prefix='papercraft-office-') as temp:
        profile = (Path(temp) / 'profile').resolve().as_uri()
        command = [soffice, '-env:UserInstallation=' + profile, '--headless',
                   '--convert-to', 'pdf:writer_pdf_Export', '--outdir', str(output), str(source)]
        run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        commands.append({'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        pdf = output / (source.stem + '.pdf')
        if run.returncode or not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError('LibreOffice 未产生有效 PDF：' + run.stdout + run.stderr)
        command = [pdftoppm, '-r', str(dpi), '-png', str(pdf), str(output / 'page')]
        run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        commands.append({'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        if run.returncode:
            raise RuntimeError('页面渲染失败：' + run.stderr)
    pages = sorted(output.glob('page-*.png'))
    if not pages:
        raise RuntimeError('PDF 已导出，但没有产生页面 PNG。')
    return len(pages), commands


def render(source, output, *, backend='auto', documents_skill=None, soffice=None,
           pdftoppm=None, poppler_dir=None, dpi=150, timeout=120):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError('原稿不存在。')
    if output.exists():
        raise ValueError('渲染目录必须是新目录，已有内容不会覆盖。')
    if dpi < 72 or dpi > 600 or timeout <= 0:
        raise ValueError('dpi 应为 72–600，timeout 必须为正。')
    selected = ('documents' if documents_skill else 'standalone') if backend == 'auto' else backend
    if selected not in ('documents', 'standalone'):
        raise ValueError('未知渲染后端。')
    office = resolve_program(soffice, 'soffice')
    if poppler_dir:
        poppler_dir = Path(poppler_dir).resolve()
        if not poppler_dir.is_dir():
            raise ValueError('Poppler 目录不存在。')
        if not pdftoppm:
            pdftoppm = poppler_dir / ('pdftoppm.exe' if os.name == 'nt' else 'pdftoppm')
    rasterizer = resolve_program(pdftoppm, 'pdftoppm')
    script = None
    if selected == 'documents':
        script = Path(documents_skill) / 'render_docx.py' if documents_skill else None
        if script is None or not script.is_file():
            raise ValueError('documents 后端需要 --documents-skill 指向含 render_docx.py 的目录。')
    output.mkdir(parents=True)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    record = {'source': str(source), 'source_sha256': digest(source), 'backend': selected,
              'soffice': office, 'pdftoppm': rasterizer, 'dpi': dpi,
              'render_status': 'FAIL', 'visual_review': 'NOT_RUN', 'author_acceptance': False}
    try:
        if selected == 'standalone':
            pages, commands = standalone(source, output, office, rasterizer, dpi, timeout)
            record['commands'] = commands
        else:
            spec = importlib.util.spec_from_file_location('pef_documents_renderer', script)
            renderer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            if not callable(getattr(renderer, 'rasterize', None)) or not hasattr(renderer, '_resolve_soffice'):
                raise RuntimeError('documents renderer API 不匹配；请使用它自己的 CLI。未静默切换后端。')
            renderer._resolve_soffice = lambda: office
            previous = os.environ.get('PATH', '')
            try:
                os.environ['PATH'] = str(Path(rasterizer).parent) + os.pathsep + previous
                pages = len(renderer.rasterize(str(source), str(output), dpi, False, True))
            finally:
                os.environ['PATH'] = previous
            record.update(renderer=str(script.resolve()), renderer_sha256=digest(script))
        artifacts = {p.name: digest(p) for p in output.iterdir() if p.suffix.lower() in ('.png', '.pdf')}
        if not pages or not any(name.endswith('.pdf') for name in artifacts):
            raise RuntimeError('渲染器没有同时产生 PDF 和页面。')
        record.update(render_status='PASS', pages=pages, artifacts=artifacts)
    except Exception as exc:
        record['error'] = str(exc)
        (output / 'render-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        raise
    (output / 'render-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--backend', choices=['auto', 'documents', 'standalone'], default='auto')
    parser.add_argument('--documents-skill', type=Path)
    parser.add_argument('--soffice', type=Path)
    parser.add_argument('--pdftoppm', type=Path)
    parser.add_argument('--poppler-dir', type=Path)
    parser.add_argument('--dpi', type=int, default=150)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    try:
        result = render(**vars(args))
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps({k: result[k] for k in ('backend', 'render_status', 'pages', 'visual_review')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
