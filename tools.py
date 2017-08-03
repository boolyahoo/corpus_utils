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
    x = [10,    20,    30,    40,    50,    60,    70,    80  ]
    y = [91.92, 92.84, 92.94, 93.25, 93.18, 93.30, 93.08, 93.34]
    plt.plot(x, y, color='k', linewidth=1, marker='o',alpha=0.8 ,markersize=2)

    plt.grid(linestyle=":", color='black',linewidth=0.2)
    plt.xlabel("# training sentences * 1000")  # X轴标签
    plt.ylabel("F score")  # Y轴标签

    # plt.show()  # 显示图
    plt.savefig("/Users/xcoder/Workplace/paper/paper latex/F-score.pdf")
