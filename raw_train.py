#!/usr/bin/env python
# coding=utf-8
import json
import codecs
import re
import os
import sys
import xlrd

import random


def contains_fuzzy_labels(line, fuzzy_labels):
    label = re.split(u"\s+", line)[0]
    return label == fuzzy_labels


if __name__ == "__main__":
    raw_train_file_name = "corpus/raw_train/raw.train.data"
    buffer = []
    fuzzy_labels = "B|M|E|S"
    threshold = 0.2

    target_file = codecs.open("corpus/raw_train/raw.train.p20.data", "w", "utf-8")

    with codecs.open(raw_train_file_name, "r", "utf-8") as src:
        for line in src.read().splitlines():
            labels = re.split(u"\s+", line)[0]

            if labels == "B" or labels == "S":
                p = random.uniform(0, 1)
                if p < threshold:
                    # 小于阈值，输出fuzzy buffer
                    if len(buffer) >= 1:
                        if not contains_fuzzy_labels(buffer[0], fuzzy_labels):
                            for features in buffer:
                                sequence = re.split(u"\s+", features)
                                sequence[0] = fuzzy_labels
                                target_file.write("\t".join(sequence) + "\n")
                        else:
                            for features in buffer:
                                target_file.write(features + "\n")
                    else:
                        continue
                else:
                    # 大于阈值，输出buffer
                    for features in buffer:
                        target_file.write(features + "\n")

                # 清空，并将当前行加入到buffer中
                buffer = []
                buffer.append(line)
            elif len(line) == 0:
                # 换行符，输出buffer
                for features in buffer:
                    target_file.write(features + "\n")
                target_file.write("\n")
                buffer = []
            else:
                buffer.append(line)
