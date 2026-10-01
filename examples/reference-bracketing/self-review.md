# 自审记录

首稿 `first.md` 完整保存后，重新读取 `input.md` 及首稿，完成一轮自修并另存 `final.md`。没有外部评语轮、独立审阅者或作者接受记录。

## 首稿实际阻碍与本轮修改

首稿的摘要使用 “bracketing two samples with shared reference endpoints”，读者需先猜测共享的是哪种操作。自修改为 “references before and after two sample readings ... sharing endpoints between adjacent groups”，让读者先看见参考与样本的先后关系。

首稿方法首段在 R0、R1、R2 定义之后立即接入时间戳、时长、跨组共享与跨扫描禁复用；下一段又先报所有采集数，才说明为何要等待。必要信息存在，但一次操作的先后不够突出。

- 首稿：“R2 places a reference immediately before and after each group of two samples, interpolating linearly between those reference values at the sample acquisition timestamps.”
- 自修：“An R2 group reads an opening reference, two samples, then a closing reference.” 接着解释闭合参考成为下一组开头、扫描之间不复用，再说明插值条件与采集数。
- 首稿把“不能即时导出”的原因放在采集数之后，跨段才写私存；自修用 “When either sample arrives, its closing reference is still unavailable. R2 therefore stores both readings privately and exports no interim corrected values.” 把原因与具体动作放在一起。

这些改动让“少取参考”与“必须等组闭合”在读者能跟随的同一次扫描中相遇。代价是方法仍需保留时间戳与同长采集条件，不能只留下最短操作句；其必要性来自插值和时间比较的定义。没有改写数据、改变因果归属或把队列行为说成独立速度贡献。

## 对照来源后的判断

标题、摘要与各节首段共同指向条件性选择：R1 已经应对变化偏移；R2 的差异是两样本区间及共享端点，节省既定采集预算，组内阶跃却使误差变大。摘要保留阶跃反例，结果保留 R0 的常量优势，故这条主线不依靠弱化对照成立。

方法保留没有中间校正值、缺任一端点整组不可用、不得借前组参考填充；正文把六样本缺失情况与八样本误差表明确分开。读者无需查本报告才能看到这些会改变结论的条件。

技术核对：首稿与自修稿的完整表格逐字符比较均与原表一致（统一换行符后）；9 个数据行、表头、行序和数值均未修改。数字推导仅有 16−13=3 次、160−130=30 ms、8/2=4 组及 4+1=5 次参考，不引入实验点。

字数按空白分词，去掉表格行和 Markdown 标题标记，包含标题、披露、章节标题与表题：首稿 816，自修稿 796。两版均符合 650–850 词范围。

这些核对用于确认约束，不用于给写作质量打分。上述阅读连接是作者模型的自审判断，尚未获得独立读者效果或作者科学认可。Markdown 不构成 Word 页面视觉验收；没有生成、渲染或检查 Word/PDF。

## 保留的限制与停止决定

未提供噪声、变长采集、重复测量、置信区间、随机缺失统计、恢复时延、队列单项计时或硬件新颖性证据；论文内保留对应边界。没有联网、引用新增、实验执行或其他试用结果读取。未提出需要第二轮自修的明确假设，按任务约定保留本轮 `final.md`。
