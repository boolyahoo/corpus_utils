#!/usr/bin/env python
# coding=utf-8
import json
import codecs
import re
import os
import sys
import xlrd

import numpy as np
import matplotlib.pyplot as plt

from optparse import OptionParser

if __name__ == "__main__":
    # x = [27.76, 36.28, 44.82, 53.32, 61.82, 70.35, 78.83, 87.37]
    # y = [92.51, 93.06, 92.73, 93.13, 93.11, 93.31, 93.41, 93.38]
    #
    # plt.plot(x, y, color='k', linewidth=1, marker='o', alpha=0.8, markersize=2)
    #
    # plt.grid(linestyle=":", color='black', linewidth=0.2)
    #
    # plt.xlabel("proportion of fixed label characters (%)", fontname="Times New Roman", fontsize=15)  # X轴标签
    # plt.ylabel("F score (%)", fontname="Times New Roman", fontsize=15)  # Y轴标签
    #
    #
    # plt.savefig("/Users/xcoder/Workplace/paper/paper latex/F-score-of-fixed-label-proportion.pdf")


    x = [10, 20, 30, 40, 50, 60, 70, 80]
    y = [91.92, 92.84, 92.94, 93.25, 93.18, 93.30, 93.08, 93.34]
    plt.plot(x, y, color='k', linewidth=1, marker='o', alpha=0.8, markersize=2)
    plt.grid(linestyle=":", color='black', linewidth=0.2)

    plt.ylabel("F score (%)",fontname="Times New Roman", fontsize=15)  # Y轴标签
    plt.xlabel("# training sentences * 1000",fontname="Times New Roman", fontsize=15)  # X轴标签

    plt.savefig("/Users/xcoder/Workplace/paper/paper latex/F-score-of-training-sentences.pdf")
