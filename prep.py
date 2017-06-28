# -*- coding:utf-8 -*-
# !/usr/in/python
# pre-processing
# by Bo Sui, 2017-03-29
import re

# 特种字符替换表, 本功能仍在开发中
BadChrs = {'㎎': 'mg', '㎏': 'kg', '㎜': 'mm',
           '㎝': 'cm', '㎞': 'km', '㏄': 'cc',
           '㏎': 'KM', '㏑': 'ln', '㏒': 'log',
           '㏕': 'mil', '㎡': 'm^2'}


def full2half(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        # 全角空格直接转换
        if inside_code == 0x3000:
            inside_code = 0x0020
        # 全角字符（除空格）根据关系转化
        elif inside_code >= 0xFF01 and inside_code <= 0xFF5E:
            inside_code -= 0xFEE0
        rstring += unichr(inside_code)
    return rstring


def half2full(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        # 半角空格直接转化
        if inside_code == 0x0020:
            inside_code = 0x3000
        elif inside_code >= 0x0020 and inside_code <= 0x7E:  # 半角字符（除空格）根据关系转化
            inside_code += 0xFEE0

        rstring += unichr(inside_code)
    return rstring


def basic_prep(txt):
    # 去空格，仅去除两个中文字符中间的空格，全角半角空格都考虑
    pattern = u"([一-龠])([\s]+)([一-龠])"
    txt = re.sub(pattern, "\\1\\3", txt)
    # 去换行符
    pattern = u"[\s]*\n+[\s]*"
    txt = re.sub(pattern, "", txt)
    # 去除数字两边的方括号
    pattern = u"[\[][\s]*([\d\.]+[×*～\-－\/:]?[\d\.\^]*)[\s]*[\]]"
    txt = re.sub(pattern, "\\1", txt)
    # 去除~-/等符号相邻的空格
    pattern = u"[\s]*([×\*～\-－\/\:\^])[\s]*"
    txt = re.sub(pattern, "\\1", txt)
    return txt


def positive_negative_convert(txt):
    def convert(match):
        """
            按如下关系进行转换
            (+) => 阳性; (-) => 阴性
            (:2+) => 2级阳性;  （+-） => 弱阳性;
            （++++） => 4级阳性; (++) => 2级阳性
            （+/-） => 弱阳性; （/-） => 阴性；
            （±） =>弱阳性
            (2+) => 2级阳性; (+2) => 2级阳性;
        """
        # step 0 为了运算速度，常见的先处理
        txt = match.group(0)
        pattern = u"[\(（][\s]*[\—－一\-][\s]*[\)）]"
        if re.match(pattern, txt):
            return u"阴性"
        pattern = u"[\(（][\s]*[\+＋十][\s]*[\)）]"
        if re.match(pattern, txt):
            return u"阳性"
        # step 1 统一格式
        # 去空格
        pattern = u"[\s]*"
        txt = re.sub(pattern, "", txt)
        # -号
        pattern = u"[\—－一\-]"
        txt = re.sub(pattern, "-", txt)
        # +号
        pattern = u"[\+＋十]"
        txt = re.sub(pattern, "+", txt)
        # step 2 去除日期时间类型
        pattern = u"[\d]+[\—－一\-\+＋十][\d]+"
        lst = re.findall(pattern, txt)
        if lst:
            return lst[0]
        # step 3 读数字
        lst = re.findall(u"\d", txt)
        pre_str = ""
        if len(lst) > 1:
            # one digit is OK
            return txt
        if len(lst) == 1:
            pre_str = lst[0] + u"级 "
        # step 4 +-都有为弱阳
        if re.search(u"\+.*\-|\.*\+|±", txt):
            return u"弱阳性"
        # step 5 几个+号?
        lst = re.findall(u"\+", txt)
        if len(lst) == 1:
            return pre_str + u"阳性"
        if len(lst) > 1:
            return str(len(lst)) + u"级阳性"
        return txt

    # 修改词（-）=>阴性， （+）=>阳性
    pattern = u"[\(（].{0,2}[\—－一\-\+＋十±].{0,2}[\)）]"
    txt = re.sub(pattern, convert, txt)
    return txt


def clean_number(txt):
    # 数量词替换为空
    pattern = u"[\d\.]+[×\*～\-－\/\:\^]?[\d\.]*[×\*～\-－\/\:\^]?[\d\.]*[\s]*(次\/分)?(声\/次)?(次\/天)?(片\/天)?(个月)?(月份)?(月余)?(余天)?[\/a-zA-Zμ天岁%％℃次个周年月日时分秒度°级包盒]*|[IＩⅠ-Ⅻ][度°○级型]"
    txt = re.sub(pattern, "", txt)
    return txt


def prep(txt):
    # 全角转半角
    txt = full2half(txt)
    # 基础转换，去空格，换行符等
    txt = basic_prep(txt)
    # 删除数量词
    txt = clean_number(txt)
    # 阴性阳性替换
    txt = positive_negative_convert(txt)
    return txt
