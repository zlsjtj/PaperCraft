# 空间对象：从画得齐全到画得可信

两个原创、非科研测量的演示，用于检验 PaperCraft 的图文呈现路径。保留首稿和退步，不把最终代码重建称作重新发现构图。它们没有证明顶刊级审美、作者认可或论文录用。

## 包覆颗粒：已用材料上的开发

输入在 `particles/input.md`。六个完整颗粒、两个相接支撑层、重复同一 P6；只移除包覆层的一部分，不切开内核。旧图 `before.png` 的身份与开口边界清楚，但强描边、偏亮高光和过小的整体图削弱质感。

| 实际方案 | 得到什么 | 失去什么 / 处理 |
|---|---|---|
| `before.png` | 容易计数、内外边界明确 | 主体偏小，画法偏图标。保留其身份关系。 |
| `first/figure.png` | 同一切面裁切球面与环状边缘 | 分片渲染出现细纹，可能被误认为材料纹理；不采用。 |
| `selected/figure.png` | 连续曲面、克制颜色、较大的整体结构；前后排拉开，接触阴影收紧 | 柔和明暗不能完全消除黄色内核像椭圆贴片的感觉，仍记部分改善。 |

选择依据是相同约160 mm宽度下的计数、开口与完整内核、标签归属和造型。另一次右向光照尝试没有明显解决贴片感，未选用；完整迭代保留在本地交付。不是换色后宣布重新设计成功。

`particles/rebuild.py` 从解析球面与同一斜切面生成可编辑矢量。裁切不是物理模拟；连续明暗是示意渐变，不是数值场。重复细节和装饰面有独立分组与所属对象。图内只留必要对象标签，正文介绍整体—内部关系，图注说明开口、重复与示意边界。

## 弯曲双层：新材料首次生成及反馈后修复

输入在 `strip/input.md`。一个弯曲条带，两层同宽、全长贴合，内厚外薄，一端同被夹持、一端自由；没有外力、运动、脱层或性能证据。

执行者最初仅收到输入、候选技能和输出约束，没有收到预设构图答案。`strip/before.png` 和 `first/rebuild.py` 是首次产物；`self_review.png` 是执行者一次自主修复后的产物，仍有端面遮挡疑点。正文将散列事实组织为一个条带—两层—两端，不声称找到了科研创新。

外部反馈后，`strip/rebuild.py` 与 `drawing_backend.py` 以统一正交相机、法向可见性、空间分割绘制顺序和边线可见性替代全曲面叠画。`selected/` 为反馈后修复，**不是独立首次生成的成功记录**。主图的连续结构更明确；局部端面仍偏平面，曲面局部仍有细密渲染纹。保留这些不足，不靠缩览声称完全消除。

两个案例均没有普通提示、旧技能、新技能三组同预算比较；没有真人盲测或真实打印。初始匿名审阅与反馈后知情复验是不同阶段。纳入此包后，这两个材料不再是未见任务。

## 重建

Python依赖见 `requirements.txt`；另需可用的常规和粗体字体、Poppler `pdftoppm`。字体不随包分发。下面从仓库根目录执行；输出应为新目录：

```powershell
python -m pip install -r examples/space-illustrations/requirements.txt
python examples/space-illustrations/build_example.py --case particles --out test-output/particles-new --font C:/Windows/Fonts/arial.ttf --bold-font C:/Windows/Fonts/arialbd.ttf --pdftoppm C:/path/to/pdftoppm.exe
python examples/space-illustrations/build_example.py --case strip --out test-output/strip-new --font C:/Windows/Fonts/arial.ttf --bold-font C:/Windows/Fonts/arialbd.ttf --pdftoppm C:/path/to/pdftoppm.exe
```

输出可编辑SVG、PDF、PNG、辅助色觉视图，以及原段页面、清稿、黄色审阅稿。黄色表示相对原段的本轮文字修改，不是 Word 原生修订；图片替换见前后图。文档三页均需用实际 documents 渲染流程打开检查，脚本写入成功不等于版面验收。

最终图源为固定开发结果；新上下文从技能生成了新源代码，是另一项有限证据。严谨的3D建模、复杂有机形态、外部矢量编辑器往返、原生Word显示和作者审美认可均未由此验证。
