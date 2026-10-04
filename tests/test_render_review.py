"""渲染路径、失败保留和目录保护；真实 Office 渲染另做冒烟验证。"""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('portable_renderer_test', ROOT / 'scripts/render_review.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RenderTests(unittest.TestCase):
    def test_explicit_missing_program_fails(self):
        with self.assertRaises(ValueError):
            renderer.resolve_program(Path('not-existing-executable'), 'soffice')

    def test_existing_directory_remains_untouched(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); source = root / 'input.docx'; source.write_bytes(b'fixture')
            output = root / 'output'; output.mkdir(); (output / 'keep').write_text('keep')
            with self.assertRaises(ValueError):
                renderer.render(source, output)
            self.assertEqual((output / 'keep').read_text(), 'keep')

    def test_standalone_selection_and_failure_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); source = root / 'input.docx'; source.write_bytes(b'fixture')
            with patch.object(renderer, 'resolve_program', return_value='program'), patch.object(renderer, 'standalone', side_effect=RuntimeError('conversion failed')):
                with self.assertRaises(RuntimeError):
                    renderer.render(source, root / 'output')
            receipt = json.loads((root / 'output/render-record.json').read_text())
            self.assertEqual(receipt['backend'], 'standalone')
            self.assertEqual(receipt['render_status'], 'FAIL')
            self.assertEqual(receipt['visual_review'], 'NOT_RUN')
            self.assertEqual(source.read_bytes(), b'fixture')

    def test_explicit_documents_error_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); source = root / 'input.docx'; source.write_bytes(b'fixture')
            with patch.object(renderer, 'resolve_program', return_value='program'), patch.object(renderer, 'standalone') as fallback:
                with self.assertRaises(ValueError):
                    renderer.render(source, root / 'output', documents_skill=root / 'missing')
                fallback.assert_not_called()
            self.assertFalse((root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
