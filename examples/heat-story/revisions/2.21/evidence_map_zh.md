# 主张与给定证据对照

本表只追踪已有材料；不补机制、实验、文献或性能归因。

| 稿件落点 | 正文主张/工作 | 原始来源 | 可以得出的判断 / 不能得出的判断 |
|---|---|---|---|
| 标题、摘要、§1、§3.1 | 两个端点快照随面所有者的刷新事件保存，非所有者不得覆盖 | input/implementation_notes.md → Arrays and ownership；input/manuscript.md → Later group implementation | 已定义一致参考状态及必要操作；不是实际新颖性或并发安全证明 |
| §2、§3.1 | 指数面导通律、单面通量、cell balance、sigma、D对应的两式 | input/manuscript.md → Equations used in the code sketch / Later group implementation | 六式原样保留，可由给定定义检查局部界；不是全程或最终温度误差保证 |
| 摘要、§3.1、§4 | 每活跃组有指数求值与快照访问；64→96 bytes/cell；50%预留增长 | input/manuscript.md → Discussion and conclusion；input/implementation_notes.md → Arrays and ownership | 解释理论省face工作为何不等于总时间收益；没有测量cache或vector occupancy原因 |
| §3.2 | 输入不合法abort；系数不合法不靠减dt修复；sigma超限重试；八次减半；原子式共同提交状态；abort作废临时缓存；restart全刷新 | input/implementation_notes.md → Proposed-step sequence | 设计控制义务完整；无可执行solver、可靠性测量或并发实现。正文的“commit together”只复述设计要求 |
| §3.3 | 两cell数值；D=0.2/0.4；R1终点0.5 s；R2/R3零提交 | input/manuscript.md → Small checks；input/implementation_notes.md → Invented exception traces | 算术/控制描述；不是表内性能样本，也不能代替等区间重试benchmark |
| §1、§4 | V已有连续vector-friendly循环、单面flux、beta=0外提；P4继承更新代码 | input/manuscript.md → Program and initial changes | 比较G相对于已有优化及固定周期的价值；不把继承工程拆成创新 |
| 摘要、§5、§7 | G在五例中三例省时间；P4五例都快但仅slow plate过误差线；G在另两例时间负收益 | input/results_runtime.csv 全18行；input/sources_and_limits.md | 在给定0.010 K规则和构造成本下选择方法；不是实测推荐或普遍加速 |
| §5慢板段 | 400→354.6 ms；省86.4 ms系数、加35 ms guard及6 ms transport；净45.4 ms=11.35% | 同CSV中的plate_slow三行 | 正文原有分解保留；不将90% face work省略直接说成90%加速 |
| §5 Table 1、Table 2 | 18+6行完整表格，0.003 sweep行重复 | 两CSV；input/sources_and_limits.md | 逐单元格与顺序核对；重复不是额外观察，ACCEPTED不是accuracy pass |
| §4误差段、§5扫参段 | final-only、V非真值、≤0.010 K；energy residual不能代温度误差；无automatic eta controller | input/sources_and_limits.md；input/implementation_notes.md | 局部容限、能量恒等式与最终误差承担不同判断；不暗示自适应误差控制 |
| §4、§6 | 无源数组、轨迹、统计重复；构造时间忽略vector occupancy/cache变化；只计reserved arrays | input/sources_and_limits.md；input/implementation_notes.md → Accounting notes | 可复算构造算术；不能复现solver或推出真实耗时/统计意义/production readiness |

本轮对原来已清楚的六式、§2、§3.3、三段主要结果、扫参数值解释、计时与内存口径采取保留。叙事增量主要来自段落职责和接续，未把读取更多字段当成正文工作量。
