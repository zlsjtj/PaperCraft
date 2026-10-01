# 两稿开篇独立评阅

本记录仅基于依次阅读 `output/first.md` 和 `output/final.md` 的标题、摘要及引言，在读取 `input.md`、`task.md`、`reviewer-only.md` 或两稿全文之前写成。未读取 skill、decision、自审或其他产物。这里只评读者能从开篇理解什么，不预先认定数值或技术主张已经获源材料验证；没有人类阅读计时、总分或作者认可判断。

## 首稿开篇

**问题可辨认。** 单传感器扫描八个 sample wells，变化的 additive offset 影响参考扣除后的读数。开篇没有以光学应用的重要性代替实际问题，也限定 arbitrary signal units 不代表浓度、生物属性或温度。

**已有基础和对照明确。** 摘要开头 `“Reading a reference before every sample already addresses changing additive offset.”`，引言再说明 reference subtraction、scan order、reference well 和 sensor firmware 均已存在。读者能够知道“提供参考支持”本身不是所提出的进步。

**新增做法及价值基本清楚。** `“bracketing two samples with shared reference endpoints”` 指向两个 sample 共用首尾参考、减少参考采集的设计；随后给出 13 对 16 次 acquisition 和 130 对 160 ms 的 prescribed schedule。标题中的 Scheduled Scan Savings 与摘要中的 prescribed schedule 有助于避免将其当成已测得的硬件加速。

**损益并列，工程决定有明确触发条件。** 摘要同时列出线性漂移的 0 对 0.5，以及组内 step 的 4.0 对 1.0 最大绝对误差，避免只报顺利情形。`“withholds each sample pair until its closing reference arrives”` 说明不完整参考区间不得导出的控制规则，读者能看到组内数据何时才可使用。

**阅读负担和待核对点。** “bracketing”“shared reference endpoints” 首次出现时没有直接说明哪些组共享哪一端，尚需正文图景或时序解释。开篇能看出时序与误差间的取舍，但不能仅凭摘要判断 13 次如何组成、零误差依赖什么插值假设、step 的具体位置、export withholding 是否有实现覆盖。这些是全文需补齐的论证，不是此阶段已发现的缺失证据。

## 最终稿开篇相对首稿

标题、DEMO 披露、引言和数值比较均保持不变。主要修改是一句：

- 首稿：`“bracketing two samples with shared reference endpoints”`。
- 最终稿：`“references before and after two sample readings ... sharing endpoints between adjacent groups”`。

最终表达更容易构建具体顺序：两次 sample 读数的前后有 reference，相邻组共享端点。它补清了首稿需要读者自行展开的术语含义，并未增加新性能主张。该改善范围有限；不能因为一次局部说明变清楚，就声称整篇论证或实验可信度已经提高。

## 开篇结论

两稿都能让读者早期读到：既有 per-sample reference 对照、减少采集次数的目标、线性漂移与 step 下相反的误差表现，以及 closing reference 到齐后的导出条件。最终开篇在共享端点的解释上更直接，没有发现开篇自修导致的明确退步。

这些结论只适用于本材料的首稿与自修稿。只有一个生成条件，且尚未读取原始材料，不能据此比较其他技能、确认研究新颖性，或认证实际实验性能。
