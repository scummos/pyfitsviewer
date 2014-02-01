#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pyfits
import os
import sys

common_calibrators = ['3C48', '3C123', '3C161', '3C147', '3C286', '3C295', '3C196', '3C138', 'NGC7027']

def get_file_list(directory):
    files = os.listdir(directory)
    fits = []
    skipped = 0
    for filename in files:
        if filename[-5:].lower() != '.fits':
            skipped += 1
            continue
        fits.append(directory + "/" + filename)
    return fits, skipped

def print_entry(**args):
    color = 33 if args["objname"] not in common_calibrators else 30
    args["color"] = color
    print "{size:>8}M  {tables:>4}   {name:<40} | \033[1;{color}m{objname:<8}\033[0m  {receiver:<12}".format(**args)

def print_fits_list(fits):
    for filename in fits:
        hdulist = pyfits.open(filename)
        objname = hdulist[1].header["OBJECT"]
        table_count = len(hdulist)
        file_size_mb = round(os.stat(filename).st_size / 1e6, 1)
        receiver = hdulist[2].header["FEBE"]
        print_entry(
            size = file_size_mb,
            name = filename.split('/')[-1],
            objname = objname,
            tables = table_count,
            receiver = receiver
        )

if __name__ == '__main__':
    if len(sys.argv) == 1:
        d, others = get_file_list(os.getcwd())
    elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        d, others = get_file_list(sys.argv[1])
    else:
        d = filter(lambda x: x[-5:].lower() == ".fits", sys.argv[1:])
    if len(d) != 0:
        print_fits_list(d)
        if others != 0:
            print " ... and {0} non-FITS items".format(others)
    elif others != 0:
        print "{0} non-FITS items".format(others)
