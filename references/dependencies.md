# 真实依赖与降级

本 skill 的编辑判断由 Codex 执行；它不是一个能独立判断科研创新的 Python 程序。依赖以当前宿主实际存在为准。

| 能力 | 真实依赖 | 本包如何使用 | 不可用时 |
|---|---|---|---|
| 文稿读取、推理、改写 | 宿主模型与本包参考文件 | 核对材料并编写补丁和诊断 | 不能把模板填充宣称为智能修订 |
| Word 定位修改与报告 | Python 3、lxml、python-docx | `scripts/review_docx.py`；只改简单正文段落，保留其他 ZIP 部件 | 缺库时明确 Word 生成未完成，不伪造链接 |
| 复杂 Word | 实际安装的 documents skill 及脚本 | 按该技能读 OOXML/红线指引做受控修改 | 不把复杂对象扁平化；保留原件并报告具体未完成编辑 |
| 最终视觉验收 | documents 的 `render_docx.py`、LibreOffice、PDF 渲染依赖 | 真正导出 PNG，逐页人工检查 | 标记视觉未验收；结构检查仍可执行 |
| 公式、表图与引用保护 | lxml、XML/ZIP 检查及内容审阅 | `audit_preservation.py` 检查原生数学结构、表格内容、关系/域源和明确保护段 | 数量相同不代表内容相同，保护相同不证明科学正确 |
| 图表编辑 | 可用的科学图形/SVG/Matplotlib 工作流及图源/数据 | 按科学意义选择工具；输入不足交设计 | 无数据不产生性能点；未画不称已画 |
| 文献和期刊核验 | 原始论文/官方网页与可用阅读工具 | 只为新增/强化的比较核实，记录来源 | 说明不可访问或未核实；不用出版社名替代规范 |
| 自动发现 | 宿主技能目录、SKILL 元信息、agents/openai.yaml | 保持原名称和隐式调用默认 | 文件有效不等于新会话实际触发已验证 |
| 并行代理 | 宿主能力与当次授权 | 可选；独立建议、单编辑合并 | 顺序处理三路并如实记录 |

在 Codex 桌面先用 `load_workspace_dependencies` 获取真实 Python/Node 路径，读当前技能目录中的 documents 技能，不硬编码旧插件版本。`check_dependencies.py` 接受显式 documents 和 soffice 路径；检查“存在”不启动渲染，更不宣称视觉通过。参见 [README](../README.md) 和 [实际验收](../tests/acceptance-results.md)。

可追加 `--require docx --require preservation --require render`，使所选能力缺依赖时返回失败而非仅列清单。官方校验额外 `--require official`；缺 PyYAML 不影响 Word 路径，二者分别记录。未指定 require 保持旧接口，仅断言入口和本地链接完整，不隐含所有能力可执行。渲染仍需实际运行和逐页查看。

本包没有需要安装的外部 MCP 服务，也不伪造依赖项。参考方法不是执行权限；任务书提及的工具也不等于已安装依赖。当前稿的机制和证据必须从对应版本核实。
