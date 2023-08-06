#!/bin/bash
echo Making sphinx-testdoc
mkdir sphinx-testdoc
sphinx-quickstart <<EOF
sphinx-testdoc
n
_
A Document for Testing DocOnce
Hans Petter Langtangen, Kaare Dump, A. Dummy Author, I. S. Overworked and Outburned and J. Doe
0.1
0.1
en
.rst
index
y
y
n
n
n
n
n
y
n
y
y
y

EOF