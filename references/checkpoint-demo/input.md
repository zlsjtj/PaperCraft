# 检查点流水线教学输入

这是合成 DEMO，用于测试论文编辑行为，不是真实科研结果。以下三段保持英文稿件语言，只允许使用给定事实。任务范围为局部 Markdown 修改及中文改动记录，不生成 Word，不查文献、不运行实验。

## 待修改原文

We present a novel reliable checkpoint architecture. Compression and grouping make it efficient. Our significant implementation effort includes chunk IDs, buffers, generation counters, checksums, a serial path and a configurable threshold. This is a general checkpoint optimization.

We used a staging queue with a limit of four chunks. Every checkpoint has a generation. Results carry an ID and generation. The writer checks them. The staging path was used for checkpoints above 64 MiB. This parameter was chosen scientifically. In addition, compression is used. The reliability of the pipeline was demonstrated by a large number of completed writes.

The throughput gains were 11.11%, 5.26% and -9.09% on three data sets. Therefore our method is widely useful and consistently faster. Five runs prove robust generality. The small data set did not improve, but it can be left out of the main results because large jobs matter more. The study also validates crash recovery.

## 给定证据

1. 基线已用同一压缩器压缩数据块并分组写入，不能将它们的效果归给本次变化。
2. 新路径将独立块的压缩与较早块的写入重叠；串行基线每次先等压缩完成再写。
3. 检查点可能取消和重启。回收缓冲区不能接受前任所有者的迟到结果，只有块 ID 和检查点代次均与当前槽匹配才接收；提交前核验校验和，写入完成或取消使所有权失效后才释放缓冲区。
4. 队列上限四块来自可用内存，是工程选择，不是证明过的最优值，未做队列长度敏感性研究。
5. 64 MiB 阈值来自下列同组三输入的初步计时，没有独立调参和测试划分。选定配置对较小检查点保留串行路径，但为诊断在三例上都测了强制 staging。
6. 强制 staging 对照排除文件创建和清理，使用一个固定线程数。A 的基线/staging 时间为 10.0/9.0 s，B 为 20.0/19.0 s，C 为 1.0/1.1 s，均为每例五次重复的中位数。三个独立输入都必须保留，吞吐比以每例相同工作量为前提。
7. 定向错误注入覆盖陈旧代次、错误块 ID 和校验和不匹配，均拒绝了注入结果。完成写入次数只表示活动，不是正确性证明；未做穷尽证明、掉电测试或崩溃恢复实验。

## 请求

使用 PaperCraft 将贡献、必要工程工作、观察到的价值和边界写清楚。保持简洁，保留负例与未完成验证。交付修改后的三段与逐项证据对应，区分文字编辑和新增分析。
