# 提炼结果时保住读者需要的代价

以下是虚构的教学案例，不是科研实测。它用于展示编辑决策，不是供其他论文套用的主题或句式。

## 同一份材料

旧实现 L0 在弹出已取消队列项时才释放预约槽位；L1 用独立账本提前回收取消项的槽位，并保留原队列。每次分派仍检查所有权、取消与到期；已经运行的工作不可提前退款。串行示例不能证明并发安全。L2 集成一条旧有的借用规则，其他工作线程和解析设置与 L1 相同。

固定构造值中，突发取消时 L0→L1 的及时完成为 120,000→136,800，CPU 为 360→372 核秒；稳定流量下，及时完成为 117,600→117,120，CPU 为 104→112 核秒。偏斜流量下，L1→L2 的及时完成为 180,500→194,750，CPU 为 420→443 核秒。没有重复测量，未比较逐租户扫描上限，也未测账本内存。

## 两种入口及选择

**结果先行：** “In constructed cancellation-burst values, separating slot ownership from queue membership raises timely completions by 14%, with CPU time increasing from 360 to 372 core seconds; under steady traffic, timely completions instead fall. The separation allows cancelled requests to return admission slots before their queue entries are removed, while retaining the deadline queues.”

收益和代价容易发现，适合已知资源模型的读者；对第一次接触该服务的人，先读到抽象的“分离”，需要后一句才能理解为什么有用。本例不采用这一理解次序，并不认为所有结果先行的入口都不好。

**障碍先行：** “A cancelled request may keep an admission slot until its queue entry is removed. Separating slot ownership from queue membership permits earlier reuse while retaining the deadline queues. In the constructed cancellation burst, timely completions rise by 14%, with CPU time increasing from 360 to 372 core seconds; under steady traffic, timely completions instead fall.”

采用第二种。它先交代有用的变化，再给有界结果；借用另到其比较段说明。这里不是以更少字获胜，而是让同一机制及其证据形成一个可读单元。完整状态条件仍需留在方法。

## 结果段的实际修复

**缺口稿：** “Borrowing raises timely completions from 180,500 to 194,750 under tenant skew. The improvement is 7.9%. These values do not prove general superiority.”

**修复稿：** “With workers and parsing unchanged, adding the earlier borrowing rule raises timely completions from 180,500 to 194,750 under tenant skew, while CPU time rises from 420 to 443 core seconds. This comparison concerns the integration of borrowing; it does not establish a new borrowing policy.”

重复百分比和空泛警句被实际代价及归因边界替换。逐租户扫描与内存缺口到相应方法/讨论位置说明；不能因为这段没提，就从全文消失。

## 执行后应检查什么

沿一次取消和分派检查，改稿仍写了到期处理、运行态与所有权条件；核对收益对应的 CPU 数值是否进入实际结果段；确认负结果仍有解释而非只留在表里。只做源码或关键词检查不能判断入口是否更顺。此例已用于开发，后续用不同材料检验迁移，不能将同例重建称为独立验证。
