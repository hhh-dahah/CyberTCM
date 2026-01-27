<img width="1334" height="667" alt="image" src="https://github.com/user-attachments/assets/0ec41fd6-c4d5-4d61-a65c-7d986b9e7ba1" />
##如何运行？
注意： 运行 Streamlit 网页，不能点 VS Code 右上角的那个三角形“播放键”。

必须在终端里输入命令：

巴什
streamlit run app.py
回车后：

你的默认浏览器（Chrome/Edge）会自动弹出来。

如果没有弹出，终端里会显示一个 Local URL: http://localhost:8501，按住 Ctrl 点击那个链接。

操作：

去浏览器里点一点那个 “启动检测” 按钮。

拖动一下左边的滑块。

看着气球飞起来。

##第五步：体验“光速修改” (Hot Reload)
这是 Streamlit 最爽的地方，一定要让大家体验一下：

不要关闭浏览器，把浏览器窗口和 VS Code 窗口并排放在桌面上。

在 VS Code 里，把代码第 8 行的标题改一下：

把 "TCM-BTI: 赛博体质辨识系统" 改成 "我修改了标题！"。

按 Ctrl + S 保存代码。

看一眼浏览器：

右上角通常会弹出一个 Source file changed。

点击 Always rerun (总是重新运行)。

瞬间，网页上的标题就变了，不需要你手动刷新，也不需要重启终端。
