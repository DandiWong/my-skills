import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_minutes_docx.py"
REFERENCE = ROOT / "assets" / "reference.docx"
SKILL_MD = ROOT / "SKILL.md"
MANIFEST = ROOT / "manifest.json"
CHECK_ENV = ROOT / "scripts" / "check_env.py"


def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("missing YAML frontmatter")
    frontmatter = {}
    for line in lines[1:]:
        if line == "---":
            return frontmatter
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"')
    raise AssertionError("unterminated YAML frontmatter")


def first_run_with_text(paragraph):
    return next(run for run in paragraph.runs if run.text.strip())


def run_generator(payload):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        json_path = tmp_path / "minutes.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--json",
                str(json_path),
                "--output-dir",
                str(tmp_path),
                "--date",
                "2026-06-11",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return Document(Path(result.stdout.strip()))


class GenerateMinutesDocxTests(unittest.TestCase):
    def sample_payload(self):
        return {
            "title": "项目沟通会会议纪要",
            "metadata": {
                "会议主题": "项目沟通会",
                "会议时间": "2026-06-11 10:00-11:00",
                "会议地点": "线上会议",
                "参会单位": "复星医药，合作方",
                "主持人": "张三",
            },
            "participants": ["张三（复星医药/项目负责人）", "李四（合作方/技术负责人）"],
            "sections": [
                {"heading": "一、会议目的", "items": ["对齐项目推进目标与后续输出。"]},
                {"heading": "二、关键决策与核心结论", "items": ["双方确认后续以纪要待办表跟踪事项。"]},
                {
                    "heading": "三、详细讨论要点",
                    "subsections": [
                        {"heading": "1. 项目范围", "items": ["需进一步补充业务范围边界。"]}
                    ],
                },
                {
                    "heading": "四、争议 / 重点异议及结论",
                    "items": [
                        {
                            "topic": "时间安排",
                            "discussion": "双方讨论交付节奏。",
                            "conclusion": "截止时间待确认。",
                        }
                    ],
                },
            ],
            "actions": [
                {
                    "编号": "1",
                    "待办事项": "补充项目范围说明",
                    "讨论背景": "会议需明确边界",
                    "下一步/输出": "范围说明文档",
                    "负责人": "张三",
                    "截止时间": "待确认",
                    "状态": "待执行",
                }
            ],
        }

    def test_generated_paragraph_styles_follow_reference_docx(self):
        reference = Document(REFERENCE)
        generated = run_generator(self.sample_payload())

        self.assertEqual([p.style.name for p in generated.paragraphs[:3]], ["Heading 1"] * 3)
        self.assertEqual(generated.paragraphs[0].text, "复星医药与合作方")
        self.assertEqual(generated.paragraphs[1].text, "项目沟通会")
        self.assertEqual(generated.paragraphs[2].text, "会议纪要")

        for generated_index, reference_index in [(0, 0), (3, 3), (4, 4)]:
            generated_para = generated.paragraphs[generated_index]
            reference_para = reference.paragraphs[reference_index]
            generated_run = first_run_with_text(generated_para)
            reference_run = first_run_with_text(reference_para)
            self.assertEqual(generated_para.style.name, reference_para.style.name)
            self.assertEqual(generated_para.alignment, reference_para.alignment)
            self.assertEqual(generated_run.font.name, reference_run.font.name)
            self.assertEqual(generated_run.font.size, reference_run.font.size)

    def test_action_table_layout_uses_reference_headers_and_legacy_mapping(self):
        reference = Document(REFERENCE)
        generated = run_generator(self.sample_payload())

        reference_headers = [cell.text for cell in reference.tables[0].rows[0].cells]
        generated_table = generated.tables[0]
        generated_headers = [cell.text for cell in generated_table.rows[0].cells]

        self.assertEqual(generated_headers, reference_headers)
        self.assertEqual(len(generated_table.columns), len(reference.tables[0].columns))
        self.assertEqual(
            [cell.text for cell in generated_table.rows[1].cells],
            ["1", "补充项目范围说明", "会议需明确边界；下一步/输出：范围说明文档；状态：待执行", "张三", "待确认"],
        )

    def test_skill_frontmatter_declares_semver_version(self):
        frontmatter = read_frontmatter(SKILL_MD)

        self.assertEqual(frontmatter["name"], "fosunpharma-meeting-minutes")
        self.assertEqual(frontmatter["version"], "0.3.3")
        self.assertIn("v0.3.3", frontmatter["description"])

    def test_manifest_matches_skill_frontmatter_and_declared_files_exist(self):
        frontmatter = read_frontmatter(SKILL_MD)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], frontmatter["name"])
        self.assertEqual(manifest["version"], frontmatter["version"])
        self.assertEqual(manifest["entry"], "SKILL.md")
        self.assertFalse(manifest["breaking"])
        for file_name in manifest["files"]:
            self.assertTrue((ROOT / file_name).exists(), file_name)

    def test_environment_check_reports_python_docx_available(self):
        result = subprocess.run(
            [sys.executable, str(CHECK_ENV)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("python:", result.stdout)
        self.assertIn("python-docx: OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
