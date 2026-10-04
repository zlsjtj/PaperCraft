# 同一份完整材料怎样减负

这是原创压力夹具DEMO的开发案例，不是真实科研结果，也不是未见材料验证。原材料与完整初版见[完整夹具例](../complete-fixture/README.md)。[首次修改](first-edits.json)覆盖摘要到结论；匿名[首读](first-impression.md)和[全文评阅](review.md)之后，[最终修改](edits.json)只保留明确占优的结果段。每处都保留完整前后文字与来源哈希。[源码](rebuild.py)调用正式文档适配器保留完整表和图。运行 `python examples/replacement-story/rebuild.py --out NEW_OUTPUT` 可重建独立清稿与黄色审阅稿，输出目录须不存在。本案例聚焦全文编辑，图形继续沿用父稿，不能冒称已做视觉升级。

最初假设是摘要与各节重复交代接口，因而需要全面压缩。按这个假设生成完整改稿后，匿名模型评阅仍小幅偏好旧稿：旧引言先交代已有共同参考能力，再提出剩余问题，讨论也更直接地把定位、密封与合格时间收益相连。首稿压缩后的“reference to three isolated samples”则省掉了参考侧这一角色，直到方法才消除歧义。这是一个真实退步，不能用总字数下降抵消。

## 两条实际入口及选择

**失败先行：** “The fastest pressure-fixture assembly in this synthetic DEMO is not consistently usable: two of three pin-free attempts fail their leak checks. We compare a removable reference base with three separate hoses while leaving the sample modules fixed.”

这版先让最快记录失去吸引力，但读者尚不知道夹具改了什么；容易把一个很小的控制当作主要研究对象。

**操作先行：** “Replacing the reference connections in a pressure fixture should leave its sample modules in place. This synthetic DEMO examines a removable base that replaces three reference hoses with one aligned, sealed interface. Both arrangements supply the same common reference to three isolated samples.”

开发时选择后者，但评阅没有确认它优于旧稿。最后恢复旧摘要与引言，而不是为了展示新技能强行采用新入口。共同参考的具体归属和每个部件为什么必要，比少读几个词更重要。两条尝试及完整初稿保留在过程文件中。

## 不是把工作量删掉

前稿的结果逐对复述表中每个时间和压力值，然后再次解释密封资格。新版保留完整原表，段落先给三组配对节省量，再指出两组压力偏差增加0.01 kPa、一组不变；随后用无销失败说明最快尝试为什么不能算可用收益。结果承担的是比较判断，而非抄表。

评阅认为原讨论对定位、密封与完整装配的关联更直接，因此也恢复原讨论。最终只采用结果段的明确改善：两种完整装配先均合格，再比较三组收益与压力代价；原始配对值全部留在表里。这样是把判断提前，而不是把每一节都改一遍。

## 保留与代价

原表九条记录、失败NA、60 s排除窗口、固定而非随机条件、未测的分离参考盒、传感原理继承、组件时间贡献未被隔离及真实装置未验证均留在论文。减负来自减少反复进入和把数据解释放回对照，不是删掉负结果。

读者若需要逐项核对原始时间，仍须看原表；这是正文与表的分工代价。字数仅作描述，不能证明说服力。最终改动范围缩小，是比较后的选择，不是未执行全文审阅。该案例教会编辑在整稿比较中保留旧优势、采用新优势；迁移效果须在新的完整材料上独立检验。
