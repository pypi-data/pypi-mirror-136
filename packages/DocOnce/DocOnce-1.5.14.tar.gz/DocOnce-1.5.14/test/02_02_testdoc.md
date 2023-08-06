<!-- !split -->
<!-- jupyter-book 02_02_testdoc.md -->
# Subsection 2: Testing figures

<div id="subsec:ex"></div>

Test of figures. In particular we refer to [Figure](fig:impact.html#fig:impact) in which
there is a flow.

<!-- <img src="testfigs/wave1D.png" width="200"><p><em>Visualization **of** a *wave*. <div id="fig:impact"></div></em></p> -->
![<p><em>Visualization **of** a *wave*. <div id="fig:impact"></div></em></p>](testfigs/wave1D.png)

Figures without captions are allowed and will be inlined.

<!-- <img src="testfigs/wave1D.png" width="200"> -->
![](testfigs/wave1D.png)

<!-- Test multi-line caption in figure with sidecap=True -->

Here is [figure](myfig.html#myfig) with a long (illegal) multi-line caption
containing inline verbatim text:

<!-- <img src="testfigs/wave1D.png" width="500"><p><em>A long caption spanning several lines and containing verbatim words like `my_file_v1` and `my_file_v2` as well as math with subscript as in $t_{i+1}$. <div id="myfig"></div></em></p> -->
![<p><em>A long caption spanning several lines and containing verbatim words like `my_file_v1` and `my_file_v2` as well as math with subscript as in $t_{i+1}$. <div id="myfig"></div></em></p>](testfigs/wave1D.png)

<!-- Must be a blank line after MOVIE or FIGURE to detect this problem -->

Test URL as figure name:

<!-- <img src="https://raw.githubusercontent.com/doconce/doconce_doc/main/src/blog/f_plot.png" width="500"> -->
![](https://raw.githubusercontent.com/doconce/doconce_doc/main/src/blog/f_plot.png)

<!-- Test wikimedia type of files that otherwise reside in subdirs -->

*Remark.*
Movies are tested in separate file `movies.do.txt`.

<!-- Somewhat challenging heading with latex math, \t, \n, ? and parenthesis -->

