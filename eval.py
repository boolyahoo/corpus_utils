#!/usr/bin/env python
# coding=utf-8
import sys
from optparse import OptionParser
import re


def tags2words(tags, chars):
    """convert tags to words"""
    L = len(tags)
    word = "0" if chars is None else chars[0]
    words = []
    i = 1
    while i < L:
        if tags[i] == "B" or tags[i] == "S":
            # current label is B or S, initialize a word
            words.append(word)
            word = "%d" % i if chars is None else chars[i]
        else:
            word += "%d" % i if chars is None else chars[i]
        i += 1
    words.append(word)
    return words


def _eval_on_word(ref_words, ans_words, chars, build):
    if build and chars is not None:
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


def _eval_on_tag(reference, answer, chars, build):
    assert (len(reference) == len(answer))
    nr_tags = len(reference)
    ref_words = tags2words(reference, chars)
    ans_words = tags2words(answer, chars)

    return _eval_on_word(ref_words, ans_words, chars, build)


def eval_on_tag(references, answers, chars, build, detailed=False, reportio=None):
    assert (len(references) == len(answers))
    corr_words, ans_words, ref_words = 0, 0, 0
    for reference, answer, char in zip(references, answers, chars):
        res = _eval_on_tag(reference, answer, char, build)
        if detailed:
            print >> reportio, " ".join(str(i) for i in res)
        corr_words += res[0]
        ans_words += res[1]
        ref_words += res[2]

    p = float(corr_words) / ans_words * 100
    r = float(corr_words) / ref_words * 100
    f = 0 if p + r == 0 else p * r * 2 / (p + r)
    print >> sys.stderr, "p=%f r=%f f=%f" % (p, r, f)


def eval_on_word(references, answers, chars, build, detailed=False, reportio=None):
    corr_words, ans_words, ref_words = 0, 0, 0
    for reference, answer, char in zip(references, answers, chars):
        res = _eval_on_word(reference, answer, char, build)
        if detailed:
            print >> reportio, "%f %f %f" % (float(res[0]) / res[1], float(res[0]) / res[2], 2 * float(res[0]) / (res[1] + res[2]))
        corr_words += res[0]
        ans_words += res[1]
        ref_words += res[2]

    p = float(corr_words) / ans_words * 100
    r = float(corr_words) / ref_words * 100
    f = 0 if p + r == 0 else p * r * 2 / (p + r)
    print >> sys.stderr, "p=%f r=%f f=%f" % (p, r, f)


if __name__ == "__main__":
    optparser = OptionParser()
    optparser.add_option("-r", "--reference", dest="reference", help="")
    optparser.add_option("-a", "--answer", dest="answer", default="-", help="")
    optparser.add_option("-t", "--type", dest="type", default="label", help="")
    optparser.add_option("-d", "--detailed", dest="detailed", action="store_true", default=False)
    optparser.add_option("-p", "--report", dest="report", help="")
    optparser.add_option("-b", "--build", dest="build", action="store_true", default=False)
    opts, args = optparser.parse_args()

    if opts.type not in ["label", "segmented"]:
        print >> sys.stderr, "Unknown type"
        sys.exit(1)

    # 打开report文件
    try:
        fpro = open(opts.report, "w")
    except:
        opts.detailed = False
        print >> sys.stderr, "WARN: Report can't open report file."
        fpro = None
    if opts.type == "label":
        try:
            reference_file = open(opts.reference, "r")
        except:
            print >> sys.stderr, "Failed to open reference file."
            sys.exit(1)
        # obtain the right labels
        references = [[__.split()[0] for __ in _.strip().split("\n")] for _ in re.split(r"\n{2,}", reference_file.read().strip())]

        if opts.answer == "-":
            answer_file = sys.stdin
        else:
            try:
                answer_file = open(opts.answer, "r")
            except:
                print >> sys.stderr, "Failed to open answer file"
                sys.exit(1)
        # obtain predict labels
        answers = [[__.split()[0] for __ in _.strip().split("\n")] for _ in re.split(r"\n{2,}", answer_file.read().strip())]
        if opts.build:
            # reset test file to head
            reference_file.seek(0, 0)
            # obtain characters in test file
            chars = [[__.split()[1] for __ in _.strip().split("\n")] for _ in re.split(r"\n{2,}", reference_file.read().strip())]
        else:
            # reset test file to head
            reference_file.seek(0, 0)
            chars = [None for _ in re.split(r"\n{2,}", reference_file.read().strip())]
        eval_on_tag(references, answers, chars, opts.build, opts.detailed, fpro)
    else:
        try:
            reference_file = open(opts.reference, "r")
        except:
            print >> sys.stderr, "Failed to open reference file."
            sys.exit(1)
        references = [line.strip().split() for line in reference_file]

        if opts.answer == "-":
            answer_file = sys.stdin
        else:
            try:
                answer_file = open(opts.answer, "r")
            except:
                print >> sys.stderr, "Failed to open answer file"
                sys.exit(1)
        answers = [line.strip().split() for line in answer_file]
        reference_file.seek(0, 0)
        chars = [True for _ in reference_file]
        eval_on_word(references, answers, chars, opts.build)
