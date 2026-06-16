# Changelog

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
