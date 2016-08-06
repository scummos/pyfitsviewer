#!/bin/sh
export ANACONDA=/home/bwinkel/local/anaconda2/
alias apyuic="PYTHONPATH= LDFLAGS= CFLAGS= LD_LIBRARY_PATH= QT5DIR= $ANACONDA/bin/pyuic4"

apyuic mainwindow_form.ui -o mainwindow_form.py
apyuic plotwindow_form.ui -o plotwindow_form.py
