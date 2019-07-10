# -*- coding:utf-8 -*-

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
#from pdfminer.pdfpage import PDFPage
from io import StringIO
from mypdfpage import MyPdfPage
import sys
import re


# 각 목차 안의 페이지를 리스트화 함
def make_index_iterable(index_dic_origin):
    listize_index_idc = {}
    for index, page_str in index_dic_origin.items():
        items = []
        for page in page_str.split(","):
            pages = []
            if "-" in page:
                start, end = page.split('-')
                pages += range(int(start), int(end) + 1)
            else:
                pages += [int(page)]
            items += pages
        listize_index_idc[index] = items
    return listize_index_idc


# 입력된 목차 정보 페이지를 리스트화 함
def listize_index_page(index_dic):
    ret_list = []
    for page_list in index_dic.values():
        ret_list += page_list
    ret_list.sort()
    return ret_list


# 페이지수 입력 시 단원을 태그화 하여 리턴
def get_page_tag(page, index_dic):
    for index, page_list in index_dic.items():
        if page in page_list:
            return index
    return


# 추출된 텍스트를 정규화한다.
def purify_text(extracted_text, pageno, index_dic):
    # 정책
    # - 개행문자로 split해서 라인별로 검사
    # - "다." 혹은 "까?" 로 끝났다면 페이지 태그를 붙인다. 그 후 개행문자를 두 개 붙인다.
    # - "다." 혹은 "까?" 후 공백문자 발견시 놔둔다. 개행문자 붙이지 않는다.
    # - "다." 혹은 "까?" 혹은 공백문자 이외의 문자로 끝났다면 공백 붙인 후, 개행하지 않고 다음으로 넘어간다.
    # - 공백글자로 끝났다면 개행하지 않는다.
    # - 첫 번째 글자에 공백은 놔둔다.
    # - 특수문자 혹은 그 코드(cid)가 나타나면 그 부분은 삭제한다.

    purified_text = ""
    line_list = extracted_text.split('\n')
    for line in line_list:
        if "(cid:" in line:
            while "(cid:" in line:
                tmp_idx = line.find("(cid:")
                remove_text = line[tmp_idx: tmp_idx + line[tmp_idx:].find(")") + 1]
                line = line.replace(remove_text, "")

        trimed_line = line.strip()
        if len(line) <= 1 or len(trimed_line) <= 1:
            continue

        if trimed_line[-2:] == "다." or trimed_line[-2:] == "까?":
            purified_text += trimed_line + "|" + str(pageno) + "|" + get_page_tag(pageno, index_dic) + "\n\n"
        else:
            purified_text += trimed_line + ' '

    # 이중 공백을 제거한다.
    purified_text = re.sub(' +', ' ', purified_text)

    purified_text += "\n\n"
    return purified_text


def convert_pdf_to_txt(path, index_dic, maxpages=0, pagenos=None, password="", caching=True):
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()

    try:
        fp = open(path, 'rb')
        index_dic = make_index_iterable(index_dic)
        pageno_list = listize_index_page(index_dic)

        ret_text = ""
        for pageno, pdf_page in MyPdfPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                                    check_extractable=True):
            if pageno not in pageno_list:
                continue

            print("Current page : {}".format(pageno))
            retstr = StringIO()
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            interpreter.process_page(pdf_page)
            text = retstr.getvalue()
            ret_text += purify_text(text, pageno, index_dic)
            device.close()
            retstr.close()

        fp.close()

        return ret_text
    except FileNotFoundError:
        sys.stderr.write("No file: %s\n" % path)
        exit(1)
