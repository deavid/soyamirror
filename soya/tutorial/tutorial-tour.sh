#!/bin/bash

for tut in `ls *.py`; do {
	echo "Press <ENTER> to begin (<CTRL-C> to abort) :" $tut
	read
	python2.5 $tut
} done
