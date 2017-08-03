#!/usr/bin/env python
# coding=utf-8

import json
import codecs
import re
import os
import prep
import xlrd

ENCODING_UTF_8 = "utf-8"
LINE_BREAK = "\n"
MAX_SENTENCE_LENGTH = 120


def clean(root_dir, dst_file_name):
    """read json format data, write cleaned data to dst file
    :param root_dir
    :param dst_file_name
    """
    corpus_file = codecs.open(dst_file_name, "w", ENCODING_UTF_8)
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if not f.endswith(".json"):
                continue
            with codecs.open(root + "/" + f, "r", ENCODING_UTF_8) as src:
                json_data = json.load(src)
                for d in json_data:
                    line = d["Content_Txt"]
                    line = prep.prep(line)
                    corpus_file.write(line)
                    corpus_file.write(LINE_BREAK)
    corpus_file.close()


def re_func():
    """some regular expressions to clean corpus"""
    corpus_file = codecs.open("corpus/medical_record/data.txt", "r", ENCODING_UTF_8)
    f = codecs.open("corpus/medical_record/data.temp.txt", "w", ENCODING_UTF_8)
    for line in corpus_file.readlines():
        if len(line) < 4:
            continue
        # 调用prep预处理
        line = prep(line)
        # 将连续的标点符号保留为一个半角逗号
        line = re.sub(u"[,。、:/\?]{2,}", ",", line)
        # 删除连续的左右括号
        line = re.sub(u"\(\)", "", line)
        # 删除两个汉字之间的～号
        line = re.sub(u"([一-龠,。]+)([~]+)([一-龠，。]+)", "\\1\\3", line)
        # 删除英文字符之间的空白
        line = re.sub(u"([a-zA-z0-9]+)([\s]+)([a-zA-Z0-9一-龠，。,]+)", "\\1\\3", line)
        # 删除英文字符
        line = re.sub(u"[a-zA-Z0-9,\*]+", "", line)
        # 提取连续的汉字字符
        line = re.findall(u"[\u4e00-\u9fa5]+", line)
        line = ",".join(line)
        f.write(line + LINE_BREAK)
    f.close()


def split():
    """"按照最大长度和标点符号对语料进行分割"""
    corpus_file = codecs.open("corpus/medical_record/data.raw", "r", ENCODING_UTF_8)
    f = codecs.open("corpus/medical_record/data.split", "w", ENCODING_UTF_8)
    for line in corpus_file.readlines():
        start = 0
        end = 0
        i = 0
        while i < len(line):
            # 长度超过最大值
            if i - start + 1 >= MAX_SENTENCE_LENGTH:
                temp = ""
                if end == start:
                    temp = line[start:i + 1]
                else:
                    temp = line[start:end + 1]
                start = start + len(temp)
                f.write(temp + LINE_BREAK)
                end = start
                i = start
            elif line[i] == ",":
                end = i
                i += 1
            else:
                i += 1
        temp = line[start:i]
        f.write(temp)
    f.close()


def convert_ccks():
    corpus_file = codecs.open("corpus/ccks/training_data_20160626_v4.json", "r", ENCODING_UTF_8)
    raw_file = codecs.open("corpus/ccks/raw.data", "w", ENCODING_UTF_8)
    dic_file = codecs.open("corpus/ccks/dic.data", "w", ENCODING_UTF_8)
    raw_data = {}
    dic_data = {}
    json_data = json.load(corpus_file)
    for d in json_data:
        idx = d["idx"]
        raw = d["Raw"]
        factors = []
        # raw data
        if idx not in raw_data:
            raw_data[idx] = raw
        else:
            pre = raw_data[idx]
            pre = pre + raw
            raw_data[idx] = pre
        # factors
        if "Factor" in d:
            words = d["Factor"]
            for w in words:
                d = re.split(r";", w)[0]
                if d not in dic_data:
                    dic_data[d] = -1
    for (key, raw) in raw_data.items():
        line = re.findall(u"[\u4e00-\u9fa5]+", raw)
        line = ",".join(line)
        raw_file.write(line + LINE_BREAK)
    raw_file.close()

    for (key, raw) in dic_data.items():
        line = re.findall(u"[\u4e00-\u9fa5]+", key)
        for w in line:
            dic_file.write(w + LINE_BREAK)
    dic_file.close()


def filter_dic():
    dic_file = codecs.open("corpus/ccks/dic.data", "r", ENCODING_UTF_8)
    temp_dic_file = codecs.open("corpus/ccks/dic.temp.data", "w", ENCODING_UTF_8)
    temp = []
    for word in dic_file.readlines():
        if len(word) > 5:
            temp.append(word)
        else:
            temp_dic_file.write(word)
    # for word in temp:
    #     temp_dic_file.write(word)
    temp_dic_file.close()


def split_data(line, line_length):
    """split line by max line length
    :param line the line to be split
    :param line_length max length of result line
    :return list of split line
    """
    start = 0
    end = 0
    i = 0
    res = []
    while i < len(line):
        # length exceed max line length
        if i - start + 1 >= line_length:
            temp = ""
            if end == start:
                temp = line[start:i + 1]
            else:
                temp = line[start:end + 1]
            start = start + len(temp)
            res.append(temp)
            end = start
            i = start
        elif line[i] == ",":
            end = i
            i += 1
        else:
            i += 1
    temp = line[start:i]
    res.append(temp)
    return res


def convert_to_predict(corpus_file_name, dst_file_name):
    """convert source file to partial crfsuite predict format
    line format of partial crfsuite predict input:
    B|M|E|S u[-1]=item1 u[0]=item2 u[1]=item3
    notice:
    the leading labels can be any of predict label as it will be ignored by predict algorithm
    items should be separated by '\t'
    each line represents for one character in a input line, different input line should be separated by '\n'
    :param corpus_file_name:raw input data, each line represent one document
    :param dst_file_name: input file for predict with the format of partial crfsuite format
    """
    FUZZY_TAGS = "B|M|E|S"
    BOS = "_BOS_"
    EOS = "_EOS_"
    U_PRE = "u[-1]="
    U_CUR = "u[0]="
    U_NEXT = "u[1]="
    SEPARATOR = "\t"

    dst = codecs.open(dst_file_name, "w", ENCODING_UTF_8)
    with codecs.open(corpus_file_name, "r", ENCODING_UTF_8) as src:
        for line in src.read().splitlines():
            for split_line in split_data(line, MAX_SENTENCE_LENGTH):
                buffer = ["", "", "", ""]
                buffer[0] = FUZZY_TAGS + SEPARATOR
                for i in range(len(split_line)):
                    # pre character
                    if i == 0:
                        buffer[1] = U_PRE + BOS + SEPARATOR
                    else:
                        buffer[1] = U_PRE + split_line[i - 1] + SEPARATOR
                    # current character
                    buffer[2] = U_CUR + split_line[i] + SEPARATOR
                    # next character
                    if i == len(split_line) - 1:
                        buffer[3] = U_NEXT + EOS + LINE_BREAK
                    else:
                        buffer[3] = U_NEXT + split_line[i + 1] + LINE_BREAK
                    # output current character
                    dst.write("".join(buffer))
                # output line break for current line
                dst.write(LINE_BREAK)
    dst.close()


def tags2words(tags, chars):
    L = len(tags)
    # word取值为0如果chars为空，否则为chars[0]
    word = "0" if chars is None else chars[0]
    words = []
    i = 1
    while i < L:
        if tags[i] == "E" or tags[i] == "S":
            # 当前字符是词尾
            word += "%d" % i if chars is None else chars[i]
            words.append(word)
            word = ""
        elif tags[i] == "B":
            # 当前字符是单字词
            words.append(word)
            word = "%d" % i if chars is None else chars[i]
        else:
            word += "%d" % i if chars is None else chars[i]
        i += 1
    words.append(word)
    return words


def convert_answer_to_words(answer_file_name, predict_data_file_name):
    """convert predict answer to words
     :param answer_file_name one label for each line, corresponding predict line is separated by '\n'
     :param predict_data_file_name origin data for predicting with format of partial crfsuite format
    """
    with codecs.open(answer_file_name) as src:
        answers = [[__.split()[0] for __ in _.strip().split("\n")] for _ in re.split(r"\n{2,}", src.read().strip())]
    with codecs.open(predict_data_file_name) as src:
        references = [[__.split()[2].split("=")[1] for __ in _.strip().split("\n")] for _ in
                      re.split(r"\n{2,}", src.read().strip())]
    assert (len(references) == len(answers))
    for reference, answer in zip(references, answers):
        line = "".join(reference)
        print line
        words = tags2words(answer, reference)
        print "|".join(words)


def dir_walk(root_dir):
    """
    walk from root dir to extract word from file
    :param root_dir: root dir
    :return:
    """
    dict = {}
    dst_file = codecs.open("corpus/dic/dic_collection.data", "w", ENCODING_UTF_8)

    def walk(root_dir):
        for lists in os.listdir(root_dir):
            path = os.path.join(root_dir, lists)
            if os.path.isdir(path):
                walk(path)
            else:
                match = re.search(r"(xlsx|xls)$", path)
                if match is not None:
                    handle_excel(path, dict)
                match = re.search(r"(dic|txt)$", path)
                if match is not None:
                    handle_txt(path, dict)

    walk(root_dir)

    words = dict.items()
    words.sort()
    for k, v in words:
        dst_file.write(k + LINE_BREAK)


def handle_excel(src_file, dict):
    print "begin handling file %s" % src_file
    wb = xlrd.open_workbook(src_file)
    for sheet in wb.sheets():
        for i in range(sheet.nrows):
            for col in sheet.row_values(i):
                if not isinstance(col, unicode):
                    continue
                words = re.findall(u"[\u4e00-\u9fa5]+", col)
                for word in words:
                    dict[word] = -1


def handle_txt(src_file, dict):
    print type(dict)
    print "begin handling file %s" % src_file
    for line in codecs.open(src_file, "r", ENCODING_UTF_8).read().splitlines():
        words = re.findall(u"[\u4e00-\u9fa5]+", line)
        for word in words:
            dict[word] = -1


def test():
    file_name = "corpus/dic/词库/卫宁词库/标准编码/药品/安徽省药品信息编码库3.0版.xlsx"

    wb = xlrd.open_workbook(file_name)
    for sheet in wb.sheets():
        for i in range(sheet.nrows):
            for col in sheet.row_values(i):
                if not isinstance(col, unicode):
                    continue
                line = re.findall(u"[\u4e00-\u9fa5]+", col)
                if len(line) <= 0:
                    continue
                for c in line:
                    print c


if __name__ == "__main__":
    dic_short_file = codecs.open("corpus/test/dic_short.data", "w", ENCODING_UTF_8)
    dic_short = {}

    with codecs.open("corpus/test/dic_final.data", "r", ENCODING_UTF_8) as src:
        for word in src.read().splitlines():
            if not dic_short.has_key(word):
                dic_short.setdefault(word, -1)
            else:
                continue

    sitems = dic_short.items()
    sitems.sort()
    for word, v in sitems:
        dic_short_file.write(word + LINE_BREAK)
    dic_short_file.close()
