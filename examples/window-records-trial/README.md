# 一份未整理的材料，能否自己讲出主线？

本例是原创教学 DEMO，全部数值为构造值，不是真实科研结果。生成前固定原稿、实现笔记、十行结果及评价问题；没有给生成者预写贡献答案。两个新模型上下文分别采用普通提示和 PaperCraft，输出同样范围的短稿。模型配置相同，参考预算和一次自修机会相同；实际工具耗时并非严格相等。

## 先看产物

| 版本 | 全文 | 修改标记 | 文字来源 |
|---|---|---|---|
| 原稿 | [Word](input/rough.docx) | — | [原始材料](input/) |
| 普通提示 | [PDF](plain/clean.pdf) | [黄色稿](plain/review.pdf) | [连续正文](plain/paper.md) |
| PaperCraft 首轮定稿 | [PDF](skill/clean.pdf) | [黄色稿](skill/review.pdf) | [连续正文](skill/paper.md) |
| 评后选定稿 | [Word](selected/clean.docx) · [PDF](selected/clean.pdf) | [Word](selected/review.docx) · [PDF](selected/review.pdf) | [逐段修改](selected/edits.json) |

黄色是修改高亮，不是 Word 原生修订。两组使用同一工具装配 Word，故本例比较表达选择，不能证明各组独立完成复杂 Word 工具操作。

## 读者实际读到了什么

原稿把窗口状态、标识符、字段和各行结果放在一起。PaperCraft 先提出单次发布的限制，再解释允许后续替换会给接收端带来什么义务，最后组织首次完整性、最终修复、状态成本与失效边界。工作量通过必要决策显现，没有另造三项创新。

[匿名模型首评](anonymous-review.md)认为两稿的贡献与继承边界实质相当；PaperCraft 的动机到机制衔接、结果解释更集中，普通稿的完整替换和版本排序职责更显式。首评在条件公开前固定，字母映射见[记录](condition-map.json)。没有真人参与，也没有投稿认可。

评后稿仅重写关键方法段，把完整替换、版本排序、成对事务的作用分别讲清。首次评后文字把来源说明挤到第三页，实际渲染后又合并重复表达；这一过程不能重新算独立首读。完整数据、超期失败、开发中放弃的做法及未测场景均保留。公式与表格内容和 XML 未变。

这不是技能在所有材料上稳定胜出的证明，也不代表长论文验证。一次比较、同一模型配置、构造材料和模型辅助评阅，都是本例的边界。表格分组仍可更醒目。

## 重建固定产物

在仓库根目录运行，依赖沿用 PaperCraft 的安装说明：

```text
python examples/window-records-trial/rebuild.py --condition selected --out ../window-records-rebuild
python scripts/render_review.py ../window-records-rebuild/clean.docx ../window-records-rebuild/clean-pages --soffice /path/to/soffice --pdftoppm /path/to/pdftoppm
python scripts/render_review.py ../window-records-rebuild/review.docx ../window-records-rebuild/review-pages --soffice /path/to/soffice --pdftoppm /path/to/pdftoppm
```

把工具路径替换为本机路径。输出目录必须不存在；`--condition` 也支持 `plain`、`skill`。重建脚本使用保存的修改文本，**不调用模型，不等于再次从新材料提炼贡献**。首次生成的候选提交与技能入口哈希见 [candidate.json](candidate.json)，评审问题见 [questions.md](questions.md)。

[评后定向复验](postreview-check.md) · [最终文件与剩余取舍](final-file-check.md)
