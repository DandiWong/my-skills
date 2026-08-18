# Changelog

## 0.4.5

- Standardized chapter structure to six fixed sections: `一、会议背景` → `二、关键结论和共识` → `三、详细讨论要点` → `四、争议项` → `五、下一步行动项` → `六、会议总结`.
- Renamed `争议项与结论` → `争议项`; renamed `会议结论` → `会议总结`; moved action items from `七` to `五`; moved conclusion from `八` to `六`.
- Removed numeric prefixes from dispute viewpoints — each viewpoint is now a standalone line without `1.` `2.` numbering.
- Updated section filtering logic to skip `一` and `五` (auto-rendered), treat `六` / `会议总结` / `会议结论` as conclusion.
- Updated SKILL.md JSON example, writing rules, tests, and manifest to match new structure.

## 0.4.4

- Added action-item owner inference rules: infer the real owner from dialogue cues (self-volunteer, superior assignment, demander/provider) instead of defaulting to the topic raiser.
- Standardized three-level section numbering: `一、` → `（一）` → `1.`.
- Renamed dispute section to `争议项与结论`; replaced `discussion` field with `viewpoints` list (A/B viewpoints + conclusion), backward compatible.
- Action-item `具体内容` now contains only the task itself, no dialogue evidence or parenthetical notes.
- Added meeting time format `YYYY年M月D日 hh:mm-hh:mm`; multi-party participant lines are indented.
- Reduced title line spacing (space_before 8.5pt, space_after 8.25pt).
- Added table width normalization: columns scale to fill page content width with minimum-width enforcement to prevent awkward character wrapping.
- Excluded meta-tasks (e.g., outputting minutes, listing questions) from action items.
- Meeting conclusion now written as 1-2 paragraphs for management, no technical details, under 200 characters.
- Section structure aligned to template: `一` (background, auto-rendered) → `二`–`六` (content) → `七` (action table) → `八` (conclusion). JSON no longer includes section `一`.
- Removed duplicate `apply_cell_run_format` function; unified to `apply_run_format`.
- Added tests for viewpoints rendering, table width normalization, and section filtering.

## 0.4.3

- Added meeting-time inference: derive date/time from content text first, then from uploaded filename patterns, before falling back to `【待补充】`.
- Added multi-party meeting support: title, filename, and participant list now handle three or more participating units.
- Updated participant rules: list by stakeholder side; use `姓名（职务）` when title is clear, bare name otherwise.
- Added speaker-name cross-confirmation rule: infer uncertain speaker names from mutual address patterns in the transcript.
- Added numbered-list rule for body text: enumerated situations in section body (excluding action tables and conclusion) must use `1. 2. 3.` numbering.
- Updated `title_units()` in the generation script to join 3+ units with 顿号 + 与.

## 0.4.2

- Consolidated the v0.3.9 and v0.4.1 skills under the stable `fosunpharma-meeting-minutes` name.
- Added named `zhongshan` and `internal` templates plus custom DOCX template paths.
- Kept the detailed content, attribution, participant, action-item, JSON-repair, and compatibility rules from v0.3.9.
- Applied template-specific titles, header logos, and participant formatting.

## 0.4.1

- Added the Fosun Pharma header logo to the internal template.
- Changed the internal title block to `复星医药` plus the meeting topic, without party-A/party-B wording.
- Changed the internal participant placeholder to one combined participant list.

## 0.4.0

- Added named `zhongshan` and `internal` templates plus support for custom DOCX template paths.
- Added concise, non-technical writing guidance and explicit template selection rules.

## 0.3.9

- Clarified the source-of-truth boundary: `SKILL.md` defines content structure and writing norms, while `assets/reference.docx` is used only for Word styling and layout.
- Added an explicit content structure section covering the title block, meeting background, participant lines, discussion sections, action table, and final conclusion.
- Updated participant rendering so grouped participants are written as one line per participating side.
- Changed host rendering so `主持人` is included only when explicitly provided and useful, instead of outputting placeholder host text.
- Synchronized manifest and regression tests with the current skill version.

## 0.3.4

- Documented the structured minutes JSON as a temporary build artifact rather than a deliverable.
- Updated the workflow to write generated JSON under a system temp directory and remove it after successful DOCX generation.
- Added guidance to retain the JSON only for debugging or failed generation troubleshooting.

## 0.3.3

- Preserved halfwidth punctuation inside structured formats during JSON repair, including times such as `09:56`, numeric groupings such as `1,000`, ratios such as `1:1`, and URLs.

## 0.3.2

- Fixed JSON quote repair to preserve existing Chinese fullwidth quotes (`“”` and `‘’`) instead of replacing them with other punctuation.
- Changed unescaped halfwidth ASCII quotes inside JSON string values to Chinese fullwidth quotes (`“”` / `‘’`).
- Added conversion for common halfwidth prose punctuation inside JSON string values, such as commas, colons, semicolons, question marks, exclamation marks, and parentheses.

## 0.3.1

- Added `scripts/repair_json_quotes.py` to repair generated minutes JSON files containing unescaped inner quotes in Chinese prose.
- Documented the repair workflow and included regression tests for generated JSON quote normalization.

## 0.3.0

- Added `scripts/check_env.py` to verify Python and `python-docx` availability on new devices.
- Documented the explicit dependency setup command without silently installing Python or libraries during minutes generation.
- Updated distribution metadata to version `0.3.0`.

## 0.2.0

- Updated generated meeting minutes to use `assets/reference.docx` as the authoritative source for title, heading, body, and action-table styling.
- Changed the title block to the reference template's three-line structure: participating units, meeting topic, and `会议纪要`.
- Changed the action-item table to the reference template's 5-column layout: `序号`、`行动项`、`具体内容`、`负责人`、`时间节点`.
- Preserved compatibility with the earlier 7-field action JSON by mapping old fields into the v0.2.0 table.
- Added regression tests for reference-style output and distribution metadata.

## 0.1.0

- Initial version for generating formal Chinese meeting-minutes `.docx` files from structured meeting JSON.
- Bundled `assets/reference.docx` and `scripts/generate_minutes_docx.py`.
