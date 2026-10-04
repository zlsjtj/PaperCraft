# 先看这三个案例

都使用原创教学构造材料，不是真实科研结论。这里按你遇到的问题选例子，不按版本号排序。

## 摘要有很多信息，却看不出重点

**压头锁止时序。** 原稿列部件、模式和九行结果；改稿把“何时锁住已有压头”及漂移与操作时间的取舍前置。预载保持、锁定时不抬起等工程工作，留在方法中解释其作用。

[原始材料](../examples/clamp-timing/input/rough.txt) · [清稿 PDF](../examples/clamp-timing/clean.pdf) · [黄色稿 PDF](../examples/clamp-timing/review.pdf) · [完整案例与源码](../examples/clamp-timing/README.md)

适合先试标题和摘要。它没有把已有转动副包装成新部件，也没有用重复装夹代替独立样本。[拿这份材料开始](first-use.md)。

## 实现很复杂，但不知道哪些工作值得写

**热传输更新中的快照所有权。** 两个入口都试过：先比较成本，或先解释为什么邻组改写会让一次判断失去依据。最终采用后者，让必要的状态维护有清楚的技术理由，再谈收益和代价。

![同一记录的前后状态](../examples/heat-story/figures/figure1_owner_states_final.png)

[前稿 PDF](../examples/heat-story/revisions/2.21-complete/documents/manuscript.pdf) · [清稿 PDF](../examples/heat-story/documents/manuscript.pdf) · [取舍与重建](../examples/heat-story/README.md)

适合方法段和全文主线。本例保留六个公式、两张表与负结果；表格仍较密，不作为排版已无不足的例子。

## 结果很多，却容易把收益归错原因

**有界缓存。** 改稿先承认简单方案已经解决什么，再解释相同扫描上限下提前腾空的代价。用“1 MiB 需要 256 个 4 KiB 对象的空间”帮助读者理解困难，不把所有改进都归给新机制。

[原始材料](../examples/cache-reserve/material-paper/) · [前稿 PDF](../examples/cache-reserve/document/before.pdf) · [清稿 PDF](../examples/cache-reserve/document/clean.pdf) · [完整对照与源码](../examples/cache-reserve/README.md)

适合结果段和贡献边界。原始 20 行数值与不利情况保留；这些构造数值不证明设计具有真实性能优势。

这三个案例经过开发与模型审阅，不是本轮重新开展的独立测试。想反馈一个不适用的情况，可以提供允许公开的最小片段；不用上传整篇未发表稿件。
