# -*- coding:utf-8 -*-
from utils import convert_pdf_to_txt
import json
import sys
import argparse

parser = argparse.ArgumentParser(description="PdfParser for Textbook - Withcat")
parser.add_argument("-j", "--json", required=True, help="목차와 페이지가 정리된 json파일 경로")
parser.add_argument("-o", "--output", required=True, help="결과가 담길 텍스트 파일 경로")
parser.add_argument("-p", "--pdf", required=True, help="교과서 pdf파일 경로")

# JSON_FILE_PATH = "Source/WorldHistoryIndex.json"
# PDF_FILE_PATH = "Source/WorldHistory.pdf"
# OUTPUT_FILE_PATH = "WorldHistoryParsed.txt"

args = parser.parse_args()

JSON_FILE_PATH = args.json
PDF_FILE_PATH = args.pdf
OUTPUT_FILE_PATH = args.output

index_dic = None
try:
    json_file = open(JSON_FILE_PATH)
    index_dic = json.load(json_file)
    json_file.close()
except FileNotFoundError:
    sys.stderr.write("No file: %s\n" % JSON_FILE_PATH)
    exit(1)

if index_dic is None:
    sys.stderr.write("Failed to load json file\n")
    exit(1)

data = convert_pdf_to_txt(PDF_FILE_PATH, index_dic=index_dic)

try:
    fp = open(OUTPUT_FILE_PATH, "w", -1, "utf-8")
    fp.write(data)
    fp.close()
except FileNotFoundError:
    sys.stderr.write("Failed to write file: %s\n" % OUTPUT_FILE_PATH)
    exit(1)





