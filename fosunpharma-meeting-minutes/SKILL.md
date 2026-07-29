---
name: fosunpharma-meeting-minutes
description: "v0.4.2. Generate formal Chinese meeting-minutes DOCX files from pasted text, transcripts, chat notes, audio-transcription text, or local .docx/.txt/.md files. Use this skill whenever the user asks to 生成会议纪要、整理会议记录、总结纪要、写纪要、根据模板或转写生成纪要, meeting minutes, meeting summary, or transcript-to-minutes, even if they do not name the skill. Supports 中山医院合作 and 复星医药内部会议纪要 templates."
compatibility: "Requires Python 3.10+ and python-docx; LibreOffice is optional for visual QA."
metadata:
  version: "0.4.2"
---

# 复星医药会议纪要生成

把原始会议内容整理成简洁、正式的中文 `.docx` 会议纪要。使用本 skill 自带模板和生成脚本，不要重新实现 DOCX 排版。

## 内容与样式边界

- 本文件决定纪要结构、事实提取、归因、行动项和缺失信息处理。
- `assets/*.docx` 只决定字体、标识、页眉页脚、页面布局和表格样式。
- 模板占位文字与本文件冲突时，内容按本文件，样式按模板。

## 输出要求

- 文件名：`{会议主题}_{参会单位A&参会单位B}_会议纪要_{yyyymmdd}.docx`。
- 默认写入用户当前工作目录；用户指定目录时按其要求。
- 不修改源文件。
- 缺失的时间、地点、人员写 `【待补充】`，缺失期限写 `待确认`，不得编造。
- 删除寒暄、口头语、重复内容和非必要技术细节；每条要点最多两句话，确保非专业读者可理解。

## 模板选择

| 参数 | 模板 | 使用场景 |
|---|---|---|
| `zhongshan` | `assets/template_zhongshan.docx` | 与中山医院合作；页眉含复星医药与中山医院标识 |
| `internal` | `assets/template_internal.docx` | 复星医药内部会议；页眉仅含复星医药标识 |

用户已说明场景时直接选择。场景不明确且模板会影响交付时，先询问用户。未传 `--template` 时默认 `zhongshan`；也可传任意 `.docx` 路径。

## 工作流

1. 读取全部会议素材。
   - 粘贴文本：直接使用。
   - `.txt` / `.md`：按 UTF-8 读取。
   - `.docx`：用 `python-docx` 提取段落和表格文本。
   - 多文件：合并相关内容，忽略旧输出和渲染产物，除非用户要求引用。

2. 提取事实。
   - 会议主题、时间、地点、参会单位、主持人和参与者。
   - 决策、共识、个人观点、分歧、风险和行动项。
   - 只沿用来源明确支持的单位、角色、职务和归属。
   - 不遗漏合同、商务、合规、知识产权、审批、部署、数据安全、运维等后续事项。

3. 组织正式纪要。
   - 三行标题：
     - `zhongshan`：`{参会单位A}与{参会单位B}`、`{会议主题}`、`会议纪要`。
     - `internal`：`复星医药`、`{会议主题}`、`会议纪要`。
   - `一、会议背景`：时间、地点、参会人员、必要时的主持人、目的和背景。
   - `二、...` 至 `六、...`：按讨论主题和结果组织，不照抄发言顺序。
   - `七、下一步行动项`：5 列表格（序号、行动项、具体内容、负责人、时间节点）。
   - `八、会议结论`：简要结论和后续方向。

4. 创建临时 JSON。使用已完成的正式表述，不要把原始转写直接塞进字段。

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
  "participants": ["单位一：姓名、姓名", "单位二：姓名、姓名"],
  "sections": [
    {
      "heading": "二、关键决策与核心结论",
      "items": ["一致结论：按行动项推进。"]
    },
    {
      "heading": "三、详细讨论要点",
      "subsections": [
        {"heading": "1. 议题一", "items": ["要点一", "要点二"]}
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
      "items": ["会议结论", "后续方向"]
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

旧版 7 字段行动项仍兼容：`编号`、`待办事项`、`讨论背景`、`下一步/输出`、`负责人`、`截止时间`、`状态`。

将 JSON 放在系统临时目录，生成成功后删除；只在用户要求调试或生成失败时保留。

```bash
tmp_dir="$(mktemp -d)"
json_path="$tmp_dir/minutes.json"
```

若生成的中文 JSON 因字符串内半角引号而无法解析，先修复：

```bash
python <skill-dir>/scripts/repair_json_quotes.py "$json_path" --write
```

5. 首次运行或依赖报错时检查环境：

```bash
python <skill-dir>/scripts/check_env.py
```

若缺少 `python-docx`，告知用户运行：

```bash
python -m pip install -r <skill-dir>/requirements.txt
```

不要静默安装依赖。

6. 生成 DOCX：

```bash
python <skill-dir>/scripts/generate_minutes_docx.py \
  --json "$json_path" \
  --template zhongshan \
  --output-dir . \
  --date YYYY-MM-DD
```

成功后删除临时目录。不要删除用户提供的文件或用户要求保留的调试材料。

7. 如系统有 LibreOffice 或 DOCX 渲染器，渲染并逐页检查标识、字体、表格、分页、裁切和重叠。没有渲染工具时仍可交付，但说明未完成视觉 QA。

## 写作与归因规则

- 先写会议共识，再写独立观点、异议或保留意见。
- 只有来源明确显示共同接受时才写 `一致结论：...`；不要把个人判断包装成集体结论。
- 独立观点用自然、平等的表达，如 `张三：...` 或 `关于产品形态，李四关注...`。
- 少用 `指出`、`强调`、`明确` 等权威化动词，不因职位改变语气。
- 技术内容只保留影响决策的依赖、假设、可行性、风险和选定路径。
- 精简版仍保留重要风险和非技术行动项，只压缩措辞。

## 参会人员规则

- `zhongshan`：单位明确时按单位分行，如 `复星医药：张三、李四`、`中山医院：王五`。
- `internal`：用一行 `参会人员：...`，不按甲方、乙方拆分。
- 职务不明确时只写姓名，不添加猜测或括号内的 `【待补充】`。
- 房间号、设备名等标签不作为人名，除非用户提供映射。
- 主持人缺失时不输出主持人占位行。

## 行动项规则

- `具体内容` 应足以让负责人无需重读转写即可执行。
- 仅当负责人、期限和目的相同时合并行动项。
- 负责人不明确写 `【待补充】`；期限不明确写 `待确认`，或使用来源支持的相对期限。
- 合同、商务、法务/合规、保密、知识产权、采购、审批、部署、数据安全、运维事项即使次要也应保留。

## 捆绑资源

- `assets/template_zhongshan.docx`
- `assets/template_internal.docx`
- `scripts/generate_minutes_docx.py`
- `scripts/check_env.py`
- `scripts/repair_json_quotes.py`
- `tests/test_generate_minutes_docx.py`
- `tests/test_repair_json_quotes.py`
