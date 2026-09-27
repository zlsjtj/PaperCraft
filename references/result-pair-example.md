# 提炼结果时保住读者需要的代价

以下是虚构的教学案例，不是科研实测。它用于展示编辑决策，不是供其他论文套用的主题或句式。

## 同一份材料

旧实现 L0 在弹出已取消队列项时才释放预约槽位；L1 用独立账本提前回收取消项的槽位，并保留原队列。每次分派仍检查所有权、取消与到期；已经运行的工作不可提前退款。串行示例不能证明并发安全。L2 集成一条旧有的借用规则，其他工作线程和解析设置与 L1 相同。

固定构造值中，突发取消时 L0→L1 的及时完成为 120,000→136,800，CPU 为 360→372 核秒；稳定流量下，及时完成为 117,600→117,120，CPU 为 104→112 核秒。偏斜流量下，L1→L2 的及时完成为 180,500→194,750，CPU 为 420→443 核秒。没有重复测量，未比较逐租户扫描上限，也未测账本内存。

## 从完整比较到摘要与正文

先建立完整比较，再决定读者在入口需要的粒度。下面的密集稿没有造假，但把完整账目与主要变化同时交给第一次接触该服务的读者。

**摘要修改前：** “L1 separates slot ownership from queue membership using a reservation ledger and checks ownership, cancellation and expiration on dispatch. In constructed cancellation bursts, timely completions increase from 120,000 to 136,800 and CPU time rises from 360 to 372 core seconds. Under steady traffic, completions change from 117,600 to 117,120 and CPU time rises from 104 to 112 core seconds. L2 adds an earlier borrowing rule, increasing skewed-traffic completions from 180,500 to 194,750 at 420 to 443 core seconds. These values do not establish general superiority.”

**摘要修改后：** “A cancelled request can block a new admission while its queue entry awaits removal. We release its reserved slot through a separate ownership ledger while retaining the deadline queues. In constructed cancellation bursts, this change raises timely completions by 14% at higher CPU cost; under steady traffic, completions instead decline. The contribution is earlier reuse after cancellation, with ownership checks that prevent refunding running work. The sequential construction does not establish concurrent safety.”

采用这个入口，是因为读者先知道被什么挡住，再理解为什么要另记所有权。摘要仍给出收益、CPU 代价方向和不利流量，没有把“代价较高”替换为无内容的谨慎警句。这里的主张是有代价的可用性变化，不是资源效率；如果稿件主张净效率、更低成本或跨过某个部署预算，就必须在入口留下足以判断该主张的成本量级。L2 是继承规则的集成比较，退出摘要但留在下方实际结果段。

**方法承接段：** “The ledger records the owner of each reserved slot independently of the queue node. Cancellation can release the reservation before that node is removed. Dispatch still checks ownership, cancellation and expiration; a running request cannot receive an early refund. These state checks define the sequential release decision. They do not prove that simultaneous cancellation and dispatch are safe.”

**主结果承接段：** “Against L0, L1 raises timely completions from 120,000 to 136,800 in the constructed cancellation burst, while CPU time increases from 360 to 372 core seconds. The same separation does not help steady traffic: completions fall from 117,600 to 117,120 and CPU time increases from 104 to 112 core seconds. Thus the example supports recovering admission capacity after cancellation, not a workload-independent completion or efficiency gain. These fixed values have no repeated-trial uncertainty estimate.”

完整数值并未搬到编辑报告里，而是紧挨对应结果出现在论文中。方法承接了退出入口的状态条件；CPU 代价和负结果仍参与结论。未测账本内存及逐租户扫描上限放在讨论中：“The construction does not quantify ledger memory or compare per-tenant scan limits; neither cost can be treated as zero.”

## 结果段的实际修复

**缺口稿：** “Borrowing raises timely completions from 180,500 to 194,750 under tenant skew. The improvement is 7.9%. These values do not prove general superiority.”

**修复稿：** “With workers and parsing unchanged, adding the earlier borrowing rule raises timely completions from 180,500 to 194,750 under tenant skew, while CPU time rises from 420 to 443 core seconds. This comparison concerns the integration of borrowing; it does not establish a new borrowing policy.”

重复百分比和空泛警句被实际代价及归因边界替换。这段继续出现在主结果之后，因而 L2 的退出入口没有抹去其实际工作。

## 执行后应检查什么

沿一次取消和分派检查，改稿仍写了到期处理、运行态与所有权条件；核对收益对应的 CPU 数值是否进入实际结果段；确认负结果仍有解释而非只留在表里。只做源码或关键词检查不能判断入口是否更顺。此例已用于开发，后续用不同材料检验迁移，不能将同例重建称为独立验证。
