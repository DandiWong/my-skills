---
name: fosunpharma-meeting-minutes
description: "v0.3.4. MANDATORY: Generate formal Chinese meeting minutes (.docx) from meeting text, transcripts, chat notes, audio-transcription text, or files (.docx, .txt, .md). MUST be invoked via Skill tool whenever the task involves meeting minutes — even if the user does not explicitly say so. Trigger phrases include: 生成纪要, 生成会议纪要, 会议纪要, 总结会议纪要, 总结纪要, 整理会议记录, 整理纪要, 会议整理, 根据模板生成纪要, 把会议内容整理成纪要, 总结会议, 写纪要, 做纪要, meeting minutes, 转写原文, transcript to minutes, or ANY request to turn raw meeting content into a structured document. Also triggers when user provides a .txt file containing meeting transcript and asks to summarize or organize it."
version: 0.3.4
---

# Generate Meeting Minutes

Use this skill to turn raw meeting content into a polished Chinese `.docx` meeting-minutes file using the bundled `assets/reference.docx` as the visual, structural, and table-layout reference.

Version: `0.3.4`.

## Required Output

- Create a Word document named `{会议主题}_{参会双方}_会议纪要_{yyyymmdd}.docx`. The filename is dynamically built from the JSON payload: `metadata.会议主题` + `metadata.参会单位` (units joined by `&`). Use the current local date unless the user explicitly requests another date. The `{yyyymmdd}` part must not contain hyphens.
- Use `assets/reference.docx` as the base template. Its title block, heading hierarchy, body font, header/footer logos, footer text, section order, and action-item table layout are authoritative.
- The generated document must follow the reference template's three-line title block:
  - `{参会单位A}与{参会单位B}`
  - `{会议主题}`
  - `会议纪要`
- The action-item table must follow the reference template's 5-column layout: `序号`、`行动项`、`具体内容`、`负责人`、`时间节点`.
- Keep the source input intact. Write a new output file in the user's current working directory unless they specify another location.
- If the meeting date/time/location is absent from the input, write `【待补充】` instead of inventing it.

## Workflow

1. Read the input.
   - For pasted content, use it directly.
   - For `.docx`, extract text with `python-docx`.
   - For `.txt` or `.md`, read as UTF-8.
   - If the user provides multiple files, use all relevant meeting-content files and ignore existing output/render artifacts unless requested.

2. Extract meeting facts.
   - Meeting title/topic.
   - Meeting time, location, units, host, and participants.
   - Participant roles/affiliations. When a prior template or reference file is provided, reuse known titles and affiliations from it.
   - Main decisions, conclusions, disagreements, risks, and action items.

3. Write concise formal minutes in this structure:
   - Three-line title block matching `assets/reference.docx`.
   - `一、会议背景`: meeting time, location, key speakers/participants, host, and concise background/purpose.
   - `二、...` to `六、...`: discussion themes and conclusions, using reference Heading 2 for main sections and Heading 3 for subsections.
   - `七、下一步行动项`: action-item table using the reference 5-column layout.
   - `八、会议结论`: concise final conclusion and follow-up direction when available.

4. Prepare a JSON payload for `scripts/generate_minutes_docx.py`.
   - Use clear, finished Chinese prose.
   - Keep bullets specific and attributable where useful.
   - Do not include raw transcript filler, repeated greetings, or speech disfluencies.
   - Use `待确认`, `尽快`, or `【待补充】` when deadlines or facts are not in the source.
   - For action items, prefer the current 5-field shape (`序号`, `行动项`, `具体内容`, `负责人`, `时间节点`). The generator still accepts the older 7-field shape and maps it into the reference table.
   - Treat the frontmatter `version` field as the release version source of truth for distribution metadata.
   - Treat the JSON payload as a temporary build artifact, not a deliverable. Write it under the system temp directory by default and remove it after the DOCX is generated successfully. Keep it only when the user asks for debug artifacts or when generation fails and the JSON is needed for troubleshooting.

   Recommended temporary-file workflow:

   ```bash
   tmp_dir="$(mktemp -d)"
   json_path="$tmp_dir/minutes.json"
   # Write the structured JSON payload to "$json_path".
   ```

   If a generated JSON file fails to parse because Chinese prose contains unescaped inner quotes, run the quote repair helper before generating the DOCX:

   ```bash
   python ./scripts/repair_json_quotes.py "$json_path" --write
   ```

   The helper preserves existing Chinese fullwidth quotes, converts inner halfwidth ASCII quotes and common prose punctuation inside JSON string values to Chinese fullwidth punctuation, preserves structured formats such as times, numeric groupings, ratios, and URLs, validates the repaired JSON, and creates a timestamped `.bak` backup unless `--no-backup` is passed.

5. Check the local Python runtime before generating on a new device or when dependency errors appear.

```bash
python ./scripts/check_env.py
```

If `python-docx` is missing, do not silently install it. Tell the user to run:

```bash
python -m pip install -r requirements.txt
```

6. Run the generator script with the bundled template.

```bash
python ./scripts/generate_minutes_docx.py \
  --json "$json_path" \
  --output-dir . \
  --date YYYY-MM-DD
```

The script defaults to `../assets/reference.docx` and outputs `{会议主题}_{参会双方}_会议纪要_<yyyymmdd>.docx` built from the JSON payload.

After a successful DOCX generation, delete the temporary directory unless debug artifacts are intentionally being retained:

```bash
rm -rf "$tmp_dir"
```

7. Optionally render and visually verify the DOCX.
   - Only if `LibreOffice` (`soffice`) or a DOCX render tool is available on the system:
     ```bash
     which soffice && soffice --headless --convert-to pdf "<output>.docx" --outdir minutes_render
     ```
   - Inspect rendered pages for missing logos, text clipping, overlapping text, table overflow, and broken page breaks.
   - If rendering tools are unavailable, still deliver the DOCX and mention that visual render QA could not be completed.

## JSON Shape

Use this shape for the generator:

```json
{
  "title": "项目沟通会会议纪要",
  "metadata": {
    "会议主题": "项目沟通会",
    "会议时间": "【待补充】",
    "会议地点": "线上会议",
    "参会单位": "单位一，单位二",
    "主持人": "姓名"
  },
  "participants": [
    "姓名（单位/职务）"
  ],
  "sections": [
    {
      "heading": "二、关键决策与核心结论",
      "items": ["结论一", "结论二"]
    },
    {
      "heading": "三、详细讨论要点",
      "subsections": [
        {
          "heading": "1. 议题一",
          "items": ["要点一", "要点二"]
        }
      ]
    },
    {
      "heading": "四、争议 / 重点异议及结论",
      "items": [
        {"topic": "争议点", "discussion": "讨论摘要", "conclusion": "结论"}
      ]
    },
    {
      "heading": "八、会议结论",
      "items": ["会议结论一", "后续展望一"]
    }
  ],
  "actions": [
    {
      "序号": "1",
      "行动项": "事项",
      "具体内容": "背景、输出要求或具体说明",
      "负责人": "负责人",
      "时间节点": "待确认"
    }
  ]
}
```

Older action JSON is still accepted and will be mapped into the reference table:

```json
{
  "actions": [
    {
      "编号": "1",
      "待办事项": "事项",
      "讨论背景": "背景",
      "下一步/输出": "输出",
      "负责人": "负责人",
      "截止时间": "待确认",
      "状态": "待执行"
    }
  ]
}
```

## Bundled Resources

- `assets/reference.docx`: required Word template. Use it as the base document.
- `scripts/generate_minutes_docx.py`: deterministic DOCX builder that clears placeholder body content from the template, inserts structured minutes, formats the action table, and names the output file.
- `scripts/check_env.py`: dependency checker for Python and `python-docx`; it reports installation commands but does not install anything automatically.
- `scripts/repair_json_quotes.py`: JSON repair helper for generated minutes payloads that contain unescaped inner quotes in Chinese prose.
