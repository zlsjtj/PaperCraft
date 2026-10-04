# 原创材料包：栅格任务恢复

这是确定性工程DEMO，不代表设备性能或公开研究。材料包含原始英文稿、一个原生公式、一张表、两张初始草图、实现说明、完整事件账本和有限故障检查。生成者获得同一份事实材料，但没有评审事实清单或预写贡献答案。

原稿科学内容与首次冻结输入保持一致。`ORIGINAL-SHA256SUMS.txt` 是当时完整输入的哈希；当前 `SHA256SUMS.txt` 反映公共包中命令可移植性与中文说明的调整。未更改模型参数、数据、原稿或测试结果。

若需要重建原始DEMO，在本目录执行，输出目录必须不存在：

```powershell
python build_materials.py --out rebuilt-input --font "$env:WINDIR/Fonts/arial.ttf" --bold-font "$env:WINDIR/Fonts/arialbd.ttf"
```

依赖 Python、python-docx、Pillow、lxml 与真实字体。重建会在新目录重新计算合成模型，不访问网络、不操作设备。Word时间戳固定，同字体和依赖环境可核对字节。它不读取或生成独立评审清单。科学来源说明仍用英文，与原始稿件材料保持一致。
