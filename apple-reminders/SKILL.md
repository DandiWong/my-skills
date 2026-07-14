---
name: fosunpharma-meeting-minutes
description: "v0.3.9. MANDATORY: Generate formal Chinese meeting minutes (.docx) from meeting text, transcripts, chat notes, audio-transcription text, or files (.docx, .txt, .md). MUST be invoked via Skill tool whenever the task involves meeting minutes — even if the user does not explicitly say so. Trigger phrases include: 生成纪要, 生成会议纪要, 会议纪要, 总结会议纪要, 总结纪要, 整理会议记录, 整理纪要, 会议整理, 根据模板生成纪要, 把会议内容整理成纪要, 总结会议, 写纪要, 做纪要, meeting minutes, 转写原文, transcript to minutes, or ANY request to turn raw meeting content into a structured document. Also triggers when user provides a .txt file containing meeting transcript and asks to summarize or organize it."
version: 0.3.9
---

# Generate Meeting Minutes

Use this skill to turn raw meeting content into a polished Chinese `.docx` meeting-minutes file. This `SKILL.md` is the authority for content structure, writing rules, and meeting-minutes norms; the bundled `assets/reference.docx` is only the visual template for Word formatting and layout.

Version: `0.3.9`.

## Source-of-Truth Boundary

Keep content rules and visual rules separate.

- `SKILL.md` is authoritative for:
  - meeting-minutes content structure and section order;
  - what facts to extract;
  - how to write participants, conclusions, speaker attribution, risks, and action items;
  - how to handle missing facts, concision, traceability, and scope control.
- `assets/reference.docx` is authoritative only for:
  - Word styles and typography;
  - title/heading/body visual formatting;
  - header/footer/logo preservation;
  - page layout and table visual styling;
  - the 5-column action-item table layout.
- Do not infer content requirements from placeholder text in `reference.docx`. If the template wording and this skill differ, follow this skill for content and use the template only for styling.
- Keep template-derived formatting changes in scripts/assets. Keep content behavior changes in this `SKILL.md`.

## Required Output

- Create a Word document named `{会议主题}_{参会双方}_会议纪要_{yyyymmdd}.docx`. The filename is dynamically built from the JSON payload: `metadata.会议主题` + `metadata.参会单位` (units joined by `&`). Use the current local date unless the user explicitly requests another date. The `{yyyymmdd}` part must not contain hyphens.
- Use `assets/reference.docx` as the base visual template. Its styles, header/footer logos, footer text, page layout, and table styling are authoritative for presentation only.
- The generated document must follow this skill's three-line title block, styled according to the reference template:
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
   - Participant names, known roles, and known affiliations. When a prior template or reference file is provided, reuse only the titles and affiliations that are supported by the source.
   - Main decisions, conclusions, disagreements, risks, and action items.
   - Shared conclusions first, then speaker-attributed standalone opinions, judgments, concerns, proposals, and conclusions. Preserve the speaker name when the point is not a shared meeting consensus.
   - Contract, commercial, compliance, IP, approval, deployment, and operations follow-ups, even when they are secondary to the main technical discussion.

3. Write concise formal minutes using the content structure defined in this skill. Apply `assets/reference.docx` styles to the generated content.

## Content Structure

Use this structure for all generated minutes unless the user explicitly requests a different structure.

1. Three-line title block:
   - `{参会单位A}与{参会单位B}` when two or more participating sides are clear.
   - `{参会单位A}` when only one participating side is clear; do not invent a second side.
   - `{会议主题}`.
   - `会议纪要`.
2. `一、会议背景`
   - `会议时间：...`
   - `会议地点：...`
   - `主要参会与发言人员`
   - participant lines grouped by participating side, e.g. `复星医药：张三、李四` and `中山医院：王五、赵六`.
   - concise background/purpose.
   - Include `主持人：...` only when the host is explicit and useful for accountability; otherwise omit from content planning.
3. `二、...` to `六、...`
   - Use content-specific headings that reflect the meeting, such as `观点与结论`、`待确认事项`、`风险提示`、`关键决策`、`详细讨论要点`.
   - Use Heading 2 for main sections and Heading 3 for subsections.
   - Prefer outcome-oriented sections over transcript order.
4. `七、下一步行动项`
   - Use the 5-column action-item table: `序号`、`行动项`、`具体内容`、`负责人`、`时间节点`.
5. `八、会议结论`
   - Write a concise final conclusion and follow-up direction when available.

## Writing and Condensing Rules

When cleaning transcripts into formal minutes, reduce noise without erasing traceability.

- Compress background aggressively: keep the meeting purpose, scope, and current state; remove greetings, scheduling chatter, repetition, and speech disfluencies.
- Merge repeated points when multiple speakers are reinforcing the same conclusion. Present the merged point as a meeting consensus only when the transcript clearly shows agreement.
- Prefer shared conclusions over speaker-by-speaker attribution when the discussion reaches the same landing point. Use `一致结论：...` for shared decisions, shared judgments, agreed next steps, or points accepted by the group.
- Preserve speaker attribution for standalone or source-sensitive content:
  - Use natural, neutral attribution when a point is an individual's independent view, risk judgment, proposal, objection, or conclusion.
  - Do not convert an individual viewpoint into a collective conclusion unless other speakers explicitly agree or the meeting closes on that basis.
  - For disputes or alternatives, identify who raised each option and summarize the resulting conclusion separately.
- Reduce technical detail to decision-relevant substance:
  - Keep key dependencies, assumptions, feasibility judgments, risks, and selected paths.
  - Remove low-level reasoning steps unless they explain a decision, blocker, or action item.
- Organize by outcome rather than by speaking order, except where source attribution is needed for accountability.
- For a "精简版" or short minutes request, prefer compact sections such as `会议背景`、`核心共识`、`可行方向`、`待确认事项`、`风险提示`、`会议结论`. Keep the user's requested template and action table.
- Keep language formal and finished. Avoid transcript filler such as `我觉得`、`反正`、`说白了` unless the wording itself is material; rewrite as concise business prose.
- Use `待确认`, `尽快`, or `【待补充】` for missing facts. Do not invent dates, owners, locations, affiliations, or decisions.

## Participant Formatting Rules

Participant information should be useful for accountability without fabricating identity details.

- If a participant's role/title/identity is not explicit in the source, list the name only. Do not add `【待补充】` inside parentheses and do not infer a title from context unless it is clearly stated.
- If a participant's affiliation or participating side is clear, group participants by side using one line per side, for example `复星医药：张三、李四` and `中山医院：王五、赵六`.
- If multiple participating sides are clear, use separate participant entries for each side so the generated document displays one line per side.
- If only one side is clear, use one grouped entry for that side. Do not create a fake second side.
- If a name is known but the side is not clear, list the person under `其他参会人员：姓名` or list the name alone if there is no need for grouping.
- If a speaker label is only a room/device label and the actual person is unknown, do not list it as a participant unless the user maps the label to a person.
- Keep roles only when explicit and useful, e.g. `复星医药：马君一、王建春（IT智能体平台产品经理）`. Avoid cluttering participant lines with uncertain or low-value identity text.

## Speaker Attribution Style

Speaker attribution is for traceability, not hierarchy. First decide whether the point is a shared conclusion; only use personal attribution when it remains source-specific.

- Attribution priority:
  1. If the group reaches the same conclusion, write `一致结论：...`. This is the preferred form.
  2. If a point is not resolved, not agreed, or remains an individual's judgment, write it as a speaker-specific point.
  3. If multiple speakers raised related but different points, group them under the topic and keep names only where the differences matter.
- Use `一致结论：...` for consensus on direction, scope, decisions, next steps, risk treatment, or accepted assumptions. Do not repeat the same point again under individual speakers.
- Do not force consensus. If the transcript only shows one person's view and no agreement, keep the speaker attribution.
- If the conversation has both consensus and individual caveats, write the consensus first, then list the caveat with the speaker name.

Keep the wording natural, objective, and equal.

- Prefer concise colon or topic-first patterns:
  - `张健：若目标是在 EDC 中直接配置 edit check，则需要先解决 CRF 标准化问题。`
  - `关于产品形态，王建春关注两种可能：复星侧平台输出规则/报告，或院内工具辅助规则整理和导入。`
  - `郑涧飞的看法是，下一步应先请院方一线接口人讲清实际流程。`
- Avoid overly official or authority-heavy verbs such as `指出`、`明确`、`强调`、`提醒` when they are not necessary.
- Do not overuse `提出`、`建议` in every bullet. If a section lists multiple speaker-specific points, the `姓名：观点` format is usually cleaner.
- Use `认为` sparingly when it helps readability. Prefer describing the content directly over stacking reporting verbs.
- Keep all speakers in the same tone; do not make one speaker sound like the decision-maker unless the transcript actually shows that role.

## Action Item Preservation

Action items are not just technical tasks. Always preserve follow-ups that move the project forward, including secondary but material items.

- Always include contract, commercial, legal/compliance, confidentiality, IP, procurement, approval, deployment, data-security, operations, and maintenance follow-ups when mentioned.
- Do not drop those items merely because the user asks for a concise or simplified version. Shorten the wording instead.
- Merge action items only when they have the same owner, same timing, and same operational purpose. Otherwise keep them separate.
- If an action has no explicit owner, infer only when the transcript clearly assigns responsibility; otherwise write `【待补充】`.
- If an action has no explicit deadline, use `待确认` or a transcript-supported relative timing such as `会后尽快`、`下一次沟通前`、`院方澄清会后 1-2 周`.
- In the `具体内容` column, keep enough context that the owner can execute the item without rereading the transcript.

4. Prepare a JSON payload for `scripts/generate_minutes_docx.py`.
   - Use clear, finished Chinese prose.
   - Keep bullets specific and attributable where useful.
   - Do not include raw transcript filler, repeated greetings, or speech disfluencies.
   - Use `待确认`, `尽快`, or `【待补充】` when deadlines or facts are not in the source.
   - In `participants`, group by participating side when affiliation is clear, and omit uncertain identities/roles.
   - In `sections`, write shared conclusions first as `一致结论：...`; include speaker names only for independent opinions or unresolved conclusions using natural attribution, for example `张健：...` or `关于...，郑涧飞的看法是...`.
   - In `actions`, retain contract/commercial/compliance/IP/deployment/operations follow-ups even in concise versions.
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
    "单位一：姓名、姓名",
    "单位二：姓名、姓名"
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
