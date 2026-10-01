# 光学扫描的新材料试用

这是在栅格传输开发之后固定的新原创DEMO。生成者只读取input、task与冻结候选技能，没有预写贡献答案，也未看其他稿件或评阅清单。一个新上下文生成first后只自修一次，final为796词另加完整9行表格。它选择“采集预算与阶跃误差的取舍”，没有把队列保护单独拔高成发明。两种实际入口及取舍在decision中。

数据与设备均为教学构造，非实验。表格原文与数值全部保留；R1是变化偏移下的强对照，R0常数条件更简洁，R2的阶跃失败和缺参考样本不被隐去。这只有新版一个条件，不支持相对旧版胜出，也没有重复稳定性或真人认可。

清稿和黄色审阅稿均为实际Word/PDF。黄色相对本例first，非原生Word修订；原始碎片输入也保留。重建使用同仓库已写成文本的排版脚本：

```powershell
python examples/raster-publication/build_documents.py --source examples/reference-bracketing/final.md --baseline examples/reference-bracketing/first.md --out output/reference-bracketing
```

此命令只验证文档重建，不会再次自主写作。要检验生成，须另开上下文，只提供input/task及技能，不提供本目录答案和评阅。PDF渲染依赖documents、LibreOffice、Poppler；本次实际检查另见版本验收。
