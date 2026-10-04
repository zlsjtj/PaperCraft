# 从原始材料组织主线：局部焦面更新 DEMO

全部装置、事件、数据为确定性构造，没有物理实验。这是表达能力试用，不是科研论文或新算法成果。

## 同样材料下比较了什么

`input/` 含未经预写主旨的草稿、装置记录、实现、完整结果和数据构造源码。生成任务约定约两千词、三图、两表和160 mm图宽，没有指定核心贡献或构图答案。普通提示、旧技能、新技能分别在新上下文生成；保留普通稿、旧技能稿、新技能初稿和一次自修。模型配置相同，任务范围相同，未精确匹配消耗，单次比较不代表统计胜率。

| 方案 | 得到什么 | 代价或问题 |
|---|---|---|
| ordinary.md | 操作规则明确，结果概括直接 | 首图先解释装置；局部状态图失去全局行对应 |
| previous-skill.md | 测量、更新与保留区分较好，完整记录可查 | 入口仍先介绍仪器；结果图字多、点区压缩 |
| candidate-self.md | 先解释哨点能看见什么，用同样五次测量的成功/失败配对引出方法价值；强简单对照前置 | 摘要把未触发简称为未变化，图中更新状态需要澄清；离散案例不宜连成轨迹 |
| selected.md | 修正上述措辞及状态图例，离散点保留所有失败和三条数值基线 | 仍有必要的技术方法和数据表，不能把它宣称为无阅读负担或顶刊审美已获认可 |

匿名模型评审先读前部，再读全文，最后核对原始材料。它支持新版前部主旨更清楚，没有认为每项都胜过旧版。评后修复属于开发完善，不能追称独立首次成功。新稿没有把较低平均用时包装成更高有效吞吐，也保留了强简单对照、12/24失败及密集更新更慢的结果。

## 可复用的判断

价值问题先于装置目录：读者先知道多做的测量何时有用，再记尺寸和完整代价模型。真实工作通过公平对照、空间失败条件、返程避让成本和完整记录被看见，而不是多拆贡献条数。第一幅实际出现的图要与这个入口一致。这不是要求所有论文先画成功/失败配对图。

## 重建

需 Python、`requirements.txt`、提供的正常/粗体字体与 Poppler。下面从本示例目录运行；输出路径须尚不存在。

```powershell
python build_figures.py --data data --out rebuilt-figures --font C:/Windows/Fonts/arial.ttf --bold C:/Windows/Fonts/arialbd.ttf --pdftoppm <pdftoppm路径>
python assemble_demo.py --manuscript selected.md --baseline input/rough_manuscript_v0.md --figure 1=rebuilt-figures/figure1.png --figure 2=rebuilt-figures/figure2.png --figure 3=rebuilt-figures/figure3.png --out rebuilt-documents
python audit_demo_documents.py --dir rebuilt-documents --manuscript selected.md
```

组装器只实现本 DEMO 的排版，不代替通用 Word 编辑器。五个公式为原生 OMML；黄色稿按相对原始草稿改写的段落标黄，不是 Word 原生修订。干净稿与黄色稿数学、表格和图件一致。PDF 由 LibreOffice 渲染，六页清稿及六页审阅稿逐页查看；未验证原生 Microsoft Word、打印、人类审美认可。

图源为可编辑SVG及生成Python。`figures/figure_spec.json`中的生成时未执行项只代表生成者阶段；最终Word/PDF检查在后续统一装配执行。素材原始单位、对照范围、数值和失败记录未更改。
