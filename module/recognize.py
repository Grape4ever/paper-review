from paddleocr import PaddleOCR
import re
import json
from utils.excel_match import match_and_rename_excel_entry
from rename import rename_file

PAGE_NUM = 2
ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=PAGE_NUM)


def save_recognition_info_to_json(info_dict: dict, json_path: str):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(info_dict, f, ensure_ascii=False, indent=4)


def in_region(box, y_min, y_max):
    y_top = box[0][1]
    return y_min <= y_top <= y_max


# 提取特定区域内的文本
def extract_text_in_region(result, y_min, y_max):
    for line in result:
        text = line[1][0]
        box = line[0]
        if in_region(box, y_min, y_max):
            return text
    return ""


def extract_title_text(result_lines, y_min=500, y_max=700):
    """
    提取论文题目内容，支持多行合并。

    参数：
        result_lines: OCR 识别结果（某一页的识别结果）
        y_min, y_max: 题目所在纵坐标范围
    返回：
        合并后的题目字符串
    """
    title_lines = []

    for line in result_lines:
        box = line[0]
        text = line[1][0]
        y_top = min(pt[1] for pt in box)
        y_bottom = max(pt[1] for pt in box)

        if y_min <= y_top <= y_max or y_min <= y_bottom <= y_max:
            title_lines.append((y_top, text))

    # 按 y 坐标排序，拼接文本
    title_lines.sort()
    full_title = ''.join([line[1] for line in title_lines])

    return full_title.strip()


# 主函数，根据文件类型执行不同操作


def process_pdf_file(pdf_path, excel_path):
    result = ocr.ocr(pdf_path, cls=True)

    # 判断是否是查重报告
    for line in result:
        text = line[1][0]
        y_top = line[0][0][1]
        if ("检测报告单" in text or "检测系统" in text) and 100 <= y_top <= 200:
            # 提取学号区域内容
            raw_text = extract_text_in_region(result, 250, 290)
            student_id = re.findall(r'\d{10}', raw_text)
            if student_id:
                rename_file(pdf_path, student_id[0], 'CCBG', "pdf")
            return

    # 判断是否是论文本体

    for line in result:
        text = line[1][0]
        y_top = line[0][0][1]
        if ("题目" in text or "论文题目" in text) and 500 <= y_top <= 700:
            # 提取学号
            id_text = extract_text_in_region(result, 1100, 1140)
            student_id_match = re.findall(r'\d{10}', id_text)
            student_id = student_id_match[0] if student_id_match else ""

            # 提取题目
            title = extract_title_text(result)

            # 保存为 JSON 文件
            info = {
                "student_id": student_id,
                "title": title,
                "file_type": "LW",
                "origin_path": pdf_path
            }
            save_recognition_info_to_json(info, "./result_info.json")

            # 校验并重命名
            if match_and_rename_excel_entry(info, excel_path):
                rename_file(pdf_path, student_id + "_" + title, "LW", suffix='pdf')
            return

    print("未识别出文件类型")
