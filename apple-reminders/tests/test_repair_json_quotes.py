import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "repair_json_quotes.py"


class RepairJsonQuotesTests(unittest.TestCase):
    def test_repairs_unescaped_ascii_quotes_inside_array_string(self):
        broken = '{\n  "items": [\n    "缺陷注入测试（"挖坑"）用于评估模型。"\n  ]\n}\n'

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "minutes.json"
            path.write_text(broken, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--write", "--no-backup"],
                check=True,
                capture_output=True,
                text=True,
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["items"][0], "缺陷注入测试（“挖坑”）用于评估模型。")

    def test_preserves_existing_chinese_quotes_inside_object_string(self):
        source = '{\n  "具体内容": "后续将“审阅报告”调整为批注优先。"\n}\n'

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "minutes.json"
            path.write_text(source, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--write", "--no-backup"],
                check=True,
                capture_output=True,
                text=True,
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["具体内容"], "后续将“审阅报告”调整为批注优先。")

    def test_converts_halfwidth_ascii_punctuation_inside_string_values(self):
        source = '{\n  "具体内容": "输出: high risk, low risk! (待确认)"\n}\n'

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "minutes.json"
            path.write_text(source, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--write", "--no-backup"],
                check=True,
                capture_output=True,
                text=True,
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["具体内容"], "输出： high risk， low risk！ （待确认）")

    def test_preserves_halfwidth_punctuation_in_structured_formats(self):
        source = (
            '{\n'
            '  "会议时间": "2026年6月9日 09:56",\n'
            '  "具体内容": "样本量1,000例，比例1:1，URL为https://example.com/a:b"\n'
            '}\n'
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "minutes.json"
            path.write_text(source, encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--write", "--no-backup"],
                check=True,
                capture_output=True,
                text=True,
            )

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["会议时间"], "2026年6月9日 09:56")
            self.assertEqual(data["具体内容"], "样本量1,000例，比例1:1，URL为https://example.com/a:b")


if __name__ == "__main__":
    unittest.main()
