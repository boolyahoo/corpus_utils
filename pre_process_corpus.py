#!/usr/bin/env python
# coding=utf-8

import re
import codecs
import random


def get_words_from_line(line):
    """
    从一行原始语料中获取单词列表
    :param line: 一行原始格式的语料
    :return: 语料对应的单词列表
    """
    match = re.match(r"^[0-9-]*/m", line)
    words = []
    if match:
        start = match.end() + 1
        while True:
            while start < len(line) and is_space(line[start]):
                start += 1
            if start >= len(line):
                break
            end = start

            if line[start] == u"[":
                while line[end] != u"]":
                    end += 1
                raws = line[start + 1:end].split()
                for raw in raws:
                    words.append(raw.split("/")[0])
                while end < len(line) and not is_space(line[end]):
                    end += 1
            else:
                while end < len(line) and not is_space(line[end]):
                    end += 1
                raw = line[start:end]
                words.append(raw.split("/")[0])
            start = end + 1
    return words


def get_chars_from_line(line):
    """
    从一行原始语料中获取字符序列
    :param line: 一行原始语料
    :return: 对应的字符序列
    """
    words = get_words_from_line(line)
    chars = []
    for word in words:
        for char in word:
            chars.append(char)
    return chars


def random_initialize_tags(sentences, train_file_name, test_file_name):
    """
    对句子做标签初始化
    :param sentences: 原始语料中的句子列表
    :param train_file_name: 训练数据文件名
    :param test_file_name：测试数据集文件名
    """
    FUZZY_TAGS = "S|B|M|E"
    BOS = "_bos_"
    EOS = "_eos_"
    U_PRE = "u[-1]="
    U_CUR = "u[0]="
    U_NEXT = "u[1]="
    SEPARATOR = "\t"
    NEW_LINE = "\n"
    try:
        train_out_put = codecs.open(train_file_name, "w", "utf-8")
        test_out_put = codecs.open(test_file_name, "w", "utf-8")

        for line in sentences:
            words = get_words_from_line(line)
            chars = get_chars_from_line(line)
            start = 0
            end = -1
            buffer = ["", "", "", ""]
            for_train = random.random() < 0.98

            for i in range(len(words)):
                current = words[i]
                start = end + 1
                end = len(current) + start - 1
                fuzzy = random.random() < 0.2
                for k in range(start, end + 1):
                    # 当前字符
                    buffer[2] = U_CUR + chars[k] + SEPARATOR
                    # 标签
                    if for_train and fuzzy:
                        buffer[0] = FUZZY_TAGS + SEPARATOR
                    else:
                        if start == end:
                            buffer[0] = "S" + SEPARATOR
                        elif k == start:
                            buffer[0] = "B" + SEPARATOR
                        elif k < end:
                            buffer[0] = "M" + SEPARATOR
                        elif k == end:
                            buffer[0] = "E" + SEPARATOR
                    # 前后字符
                    if 0 == k:
                        buffer[1] = U_PRE + BOS + SEPARATOR
                        buffer[3] = U_NEXT + chars[k + 1] + NEW_LINE
                    elif k < len(chars) - 1:
                        buffer[1] = U_PRE + chars[k - 1] + SEPARATOR
                        buffer[3] = U_NEXT + chars[k + 1] + NEW_LINE
                    elif k == len(chars) - 1:
                        buffer[1] = U_PRE + chars[k - 1] + SEPARATOR
                        buffer[3] = U_NEXT + EOS + NEW_LINE
                    # 输出当前字符信息
                    if for_train:
                        train_out_put.write("".join(buffer))
                    else:
                        test_out_put.write("".join(buffer))

            # 输出当前句子换行符
            if for_train:
                train_out_put.write("\n")
            else:
                test_out_put.write("\n")

    except:
        print("file access error")


def is_space(char):
    """"
    判断字符是否为空格符（全角或半角）
    """
    return unicode(char) == u"\u0020" or unicode(char) == u"\u3000"


def convert_test_to_reference(test_file_name, reference_file_name):
    corpus_for_test = codecs.open(test_file_name, "r", "utf-8")
    corpus_for_reference = codecs.open(reference_file_name, "w", "utf-8")
    for line in corpus_for_test.readlines():
        if len(line) == 1:
            corpus_for_reference.write(line)
        else:
            tag = line.split()[0]
            char = line.split()[2].split("=")[1]
            corpus_for_reference.write(tag + "\t" + char + "\t" + char + "\n")
    corpus_for_reference.close()


if __name__ == "__main__":

    # 原始语料文件
    corpus_file_name = "corpus/people_daily.txt"
    # 字典文件
    dictionary_file_name = "corpus/people_daily_dictionary.txt"
    # 不包含标注的文件
    corpus_pure_file_name = "corpus/people_daily_pure.txt"
    # 原始语料文件
    sentences = codecs.open(corpus_file_name, "r", "utf-8").readlines()
    # 词典文件
    dictionary_file = codecs.open(dictionary_file_name, "w", "utf-8")
    # 不包含标注的语料
    corpus_pure_file = codecs.open(corpus_pure_file_name, "w", "utf-8")
    dictionary = {}
    count = 0
    for line in sentences:
        line = line.strip()
        words = get_words_from_line(line)
        for word in words:
            dictionary[word] = count
            count += 1
            corpus_pure_file.write(word)
        corpus_pure_file.write("\n")
    for key, val in dictionary.items():
        dictionary_file.write(key + "\n")
