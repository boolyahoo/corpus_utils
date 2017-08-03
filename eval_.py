#!/usr/bin/env python
# coding=utf-8
import json
import codecs
import re
import os
import sys
import prep
import xlrd

from optparse import OptionParser

ENCODING_UTF_8 = "utf-8"
LINE_BREAK = "\n"


def _eval_on_word(ref_words, ans_words, build):
    if build:
        print "\t".join(ans_words)
    m, n = 0, 0
    ref_len, ans_len = 0, 0
    corr_words = 0
    while m < len(ans_words) and n < len(ref_words):
        if ans_words[m] == ref_words[n]:
            corr_words += 1
            ref_len += len(ref_words[n])
            ans_len += len(ans_words[m])
            m += 1
            n += 1
        else:
            ref_len += len(ref_words[n])
            ans_len += len(ans_words[m])
            m += 1
            n += 1
            while (m < len(ans_words)) and (n < len(ref_words)):
                if (ref_len > ans_len):
                    ans_len += len(ans_words[m])
                    m += 1
                elif (ref_len < ans_len):
                    ref_len += len(ref_words[n])
                    n += 1
                else:
                    break

    return (corr_words, len(ans_words), len(ref_words))


def eval_on_word(references, answers, build=True, detailed=False, reportio=None):
    corr_words, ans_words, ref_words = 0, 0, 0
    for reference, answer in zip(references, answers):
        res = _eval_on_word(reference, answer, build)
        if detailed:
            print >> reportio, "%f %f %f" % (
                float(res[0]) / res[1], float(res[0]) / res[2], 2 * float(res[0]) / (res[1] + res[2]))
        corr_words += res[0]
        ans_words += res[1]
        ref_words += res[2]

    p = float(corr_words) / ans_words * 100
    r = float(corr_words) / ref_words * 100
    f = 0 if p + r == 0 else p * r * 2 / (p + r)
    print >> sys.stderr, "p=%f r=%f f=%f" % (p, r, f)


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


def convert_answer_labels_to_words():
    """convert predict answer to words
    """
    answer_labels_file_name = "corpus/test/predict.part.answer.labels.data"
    predict_raw_data_file_name = "corpus/test/predict.part.raw.data"
    answer_words_file_name = "corpus/test/predict.part.answer.words.data"

    answer_words_file = codecs.open(answer_words_file_name, "w", ENCODING_UTF_8)

    with codecs.open(answer_labels_file_name, "r", ENCODING_UTF_8) as src:
        answers = [[__ for __ in _.strip().split("\n")] for _ in re.split(r"\n{2,}", src.read().strip())]
    with codecs.open(predict_raw_data_file_name, "r", ENCODING_UTF_8) as src:
        references = [_ for _ in src.read().splitlines()]
    assert (len(references) == len(answers))
    for reference, answer in zip(references, answers):
        answer_words_file.write(" ".join(tags2words(answer, reference)) + LINE_BREAK)


def convert_annotated_to_raw():
    predict_annotated_data_file_name = "corpus/test/predict.part.annotated.data"
    predict_raw_data_file_name = "corpus/test/predict.part.raw.data"

    predict_raw_data_file = codecs.open(predict_raw_data_file_name, "w", ENCODING_UTF_8)
    with codecs.open(predict_annotated_data_file_name, "r", ENCODING_UTF_8) as src:
        for line in src.read().splitlines():
            line = re.sub(u"\s+", "", line)
            predict_raw_data_file.write(line + LINE_BREAK)
    predict_raw_data_file.close()


def eval_semi_CRF():
    answer_labels_file_name = "corpus/test/predict.part.answer.labels.data"
    predict_raw_data_file_name = "corpus/test/predict.part.raw.data"
    predict_raw_annotated_file_name = "corpus/test/predict.part.annotated.data"
    answer_words_file_name = "corpus/test/predict.part.answer.words.data"

    # 预测结果形式：一行一个句子对应的分词结果
    with codecs.open(answer_words_file_name, "r", ENCODING_UTF_8) as src:
        answers = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    with codecs.open(predict_raw_annotated_file_name, "r", ENCODING_UTF_8) as src:
        references = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    assert (len(references) == len(answers))
    eval_on_word(references, answers, False)


def eval_hanlp_CRF():
    predict_raw_annotated_file_name = "corpus/test/predict.part.annotated.data"
    answer_words_file_name = "corpus/test/predict.part.answer.words.hanlp.crf.data"

    # 预测结果形式：一行一个句子对应的分词结果
    with codecs.open(answer_words_file_name, "r", ENCODING_UTF_8) as src:
        answers = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    with codecs.open(predict_raw_annotated_file_name, "r", ENCODING_UTF_8) as src:
        references = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    assert (len(references) == len(answers))
    eval_on_word(references, answers, False)


def eval_hanlp_HMM():
    predict_raw_annotated_file_name = "corpus/test/predict.part.annotated.data"
    answer_words_file_name = "corpus/test/predict.part.answer.words.hanlp.hmm.data"

    # 预测结果形式：一行一个句子对应的分词结果
    with codecs.open(answer_words_file_name, "r", ENCODING_UTF_8) as src:
        answers = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    with codecs.open(predict_raw_annotated_file_name, "r", ENCODING_UTF_8) as src:
        references = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    assert (len(references) == len(answers))
    eval_on_word(references, answers, False)


def eval_thulac():
    predict_raw_annotated_file_name = "corpus/test/predict.part.annotated.data"
    answer_words_file_name = "corpus/test/predict.part.answer.words.thulac.data"

    # 预测结果形式：一行一个句子对应的分词结果
    with codecs.open(answer_words_file_name, "r", ENCODING_UTF_8) as src:
        answers = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    with codecs.open(predict_raw_annotated_file_name, "r", ENCODING_UTF_8) as src:
        references = [[__ for __ in re.split(r"\s+", _.strip())] for _ in src.read().splitlines()]
    assert (len(references) == len(answers))
    eval_on_word(references, answers, False)


def connect_answers_to_references():
    connected_file = codecs.open("corpus/test/predict.part.reference+answer.data", "w", ENCODING_UTF_8)
    with codecs.open("corpus/test/predict.part.annotated.data", "r", ENCODING_UTF_8) as src:
        references = [_ for _ in src.read().splitlines()]
    with codecs.open("corpus/test/predict.part.answer.words.data", "r", ENCODING_UTF_8) as src:
        answers = [_ for _ in src.read().splitlines()]
    for r, a in zip(references, answers):
        connected_file.write(r + LINE_BREAK)
        connected_file.write(a + LINE_BREAK)
    connected_file.close()


def extract_answer_words():
    extracted_words_file = codecs.open("corpus/test/predict.part.answer.words.data", "w", ENCODING_UTF_8)
    with codecs.open("corpus/test/predict.part.reference+answer.data", "r", ENCODING_UTF_8) as src:
        lines = [_ for _ in src.read().splitlines()]
    for i in range(len(lines)):
        if i % 2 != 0:
            extracted_words_file.write(lines[i] + LINE_BREAK)
    extracted_words_file.close()


if __name__ == "__main__":
    # convert_annotated_to_raw()
    # extract_answer_words()
    # convert_answer_labels_to_words()
    eval_semi_CRF()
    # eval_thulac()
    # connect_answers_to_references()
