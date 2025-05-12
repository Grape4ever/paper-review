# import os
# import re
#
# import numpy as np
#
# from utils.excel_match import match_and_rename_excel_entry
# from mymodule.rename import rename_file
# from paddleocr import PaddleOCR
# from utils.json_helper import save_json
#
# PAGE_NUM = 2
# ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=PAGE_NUM)
#
#
# # 工具函数：判断 OCR 框是否在目标区域内（带误差）
# def is_in_region(box, target_box, tolerance=15):
#     # 获取 box 的上下左右边界
#     box = np.array(box)
#     box_x_min, box_y_min = box[:, 0].min(), box[:, 1].min()
#     box_x_max, box_y_max = box[:, 0].max(), box[:, 1].max()
#
#     target = np.array(target_box)
#     target_x_min, target_y_min = target[:, 0].min() - tolerance, target[:, 1].min() - tolerance
#     target_x_max, target_y_max = target[:, 0].max() + tolerance, target[:, 1].max() + tolerance
#
#     return (target_x_min <= box_x_min <= target_x_max and
#             target_y_min <= box_y_min <= target_y_max and
#             target_x_min <= box_x_max <= target_x_max and
#             target_y_min <= box_y_max <= target_y_max)
#
#
# # 区域定义
# THESIS_TITLE_REGIONS = [
#     [[335.0, 525.0], [907.0, 519.0], [908.0, 561.0], [335.0, 567.0]],
#     [[477.0, 584.0], [773.0, 584.0], [773.0, 626.0], [477.0, 626.0]],
# ]
# STUDENT_ID_REGION = [[574.0, 1105.0], [799.0, 1105.0], [799.0, 1135.0], [574.0, 1135.0]]
#
# REPORT_TITLE_REGIONS = [
#     [[427.0, 107.0], [749.0, 107.0], [749.0, 144.0], [427.0, 144.0]],
#     [[413.0, 159.0], [762.0, 163.0], [761.0, 200.0], [412.0, 196.0]],
# ]
# REPORT_ID_REGION = [[113.0, 258.0], [352.0, 258.0], [352.0, 282.0], [113.0, 282.0]]
#
#
# def in_region(box, y_min, y_max):
#     y_top = box[0][1]
#     return y_min <= y_top <= y_max
#
#
# # 提取特定区域内的文本
# def extract_text_in_region(result, y_min, y_max):
#     for line in result:
#         text = line[1][0]
#         box = line[0]
#         if in_region(box, y_min, y_max):
#             return text
#     return ""
#
#
# def extract_title_text(result_lines, y_min=500, y_max=700):
#     """
#     提取论文题目内容，支持多行合并。
#
#     参数：
#         result_lines: OCR 识别结果（某一页的识别结果）
#         y_min, y_max: 题目所在纵坐标范围
#     返回：
#         合并后的题目字符串
#     """
#     title_lines = []
#
#     for line in result_lines:
#         box = line[0]
#         text = line[1][0]
#         y_top = min(pt[1] for pt in box)
#         y_bottom = max(pt[1] for pt in box)
#
#         if y_min <= y_top <= y_max or y_min <= y_bottom <= y_max:
#             title_lines.append((y_top, text))
#
#     # 按 y 坐标排序，拼接文本
#     title_lines.sort()
#     full_title = ''.join([line[1] for line in title_lines])
#
#     return full_title.strip()
#
#
# # 主函数，根据文件类型执行不同操作
#
#
# def process_pdf_file(pdf_path, excel_path):
#     # print(result)
#     filename = os.path.basename(pdf_path)
#     if "成绩考核表" in filename:
#         print(f"跳过识别：{filename}")
#         return
#
#     result = ocr.ocr(pdf_path, cls=True)
#     # 判断是否是查重报告
#     for line in result:
#
#         text = line[1][0]
#         y_top = line[0][0][1]
#         if ("检测报告单" in text or "检测系统" in text) and 100 <= y_top <= 200:
#             # 提取学号区域内容
#             print('是查重报告')
#             raw_text = extract_text_in_region(result, 250, 290)
#             student_id = re.findall(r'\d{10}', raw_text)
#             if student_id:
#                 rename_file(pdf_path, student_id[0], 'CCBG', "pdf")
#             return
#
#     # 判断是否是论文本体
#
#     for line in result:
#         text = line[1][0]
#         y_top = line[0][0][1]
#         if ("题目" in text or "论文题目" in text) and 500 <= y_top <= 700:
#             # 提取学号
#             print('是论文')
#             id_text = extract_text_in_region(result, 1100, 1140)
#             student_id_match = re.findall(r'\d{10}', id_text)
#             student_id = student_id_match[0] if student_id_match else ""
#
#             # 提取题目
#             title = extract_title_text(result)
#
#             # 保存为 JSON 文件
#             info = {
#                 "student_id": student_id,
#                 "title": title,
#                 "file_type": "LW",
#                 "origin_path": pdf_path
#             }
#
#             save_json(info, f"../data/{student_id}_LW.json")
#
#             # 校验并重命名
#             if match_and_rename_excel_entry(info, excel_path):
#                 rename_file(pdf_path, student_id, "LW", suffix='pdf')
#             return
#
#     print("未识别出文件类型")

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from paddleocr import PaddleOCR
import re
from utils.json_helper import JsonHandler


class DocumentRecognizer:
    # 定义常量
    PAGE_NUM = 2

    # 定义区域坐标
    THESIS_TITLE_REGIONS = [
        [[335.0, 525.0], [907.0, 519.0], [908.0, 561.0], [335.0, 567.0]],
        [[477.0, 584.0], [773.0, 584.0], [773.0, 626.0], [477.0, 626.0]]
    ]

    REPORT_TITLE_REGION = [
        [413.0, 159.0], [762.0, 163.0], [761.0, 200.0], [412.0, 196.0]
    ]

    KTBG_TITLE_REGION = [
        [351.0, 283.0], [991.0, 283.0], [991.0, 320.0], [351.0, 320.0]
    ]

    STUDENT_ID_REGION_THESIS = [
        [574.0, 1105.0], [799.0, 1105.0], [799.0, 1135.0], [574.0, 1135.0]
    ]

    STUDENT_ID_REGION_REPORT = [
        [113.0, 258.0], [352.0, 258.0], [352.0, 282.0], [113.0, 282.0]
    ]

    STUDENT_ID_REGION_KTBG = [
        [613.0, 333.0], [744.0, 333.0], [744.0, 358.0], [613.0, 358.0]
    ]

    STUDENT_ID_REGION_CJKH = [
        [600.0, 384.0], [877.0, 384.0], [877.0, 419.0], [600.0, 419.0]
    ]

    def __init__(self):
        """初始化OCR对象"""
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=self.PAGE_NUM)
        self.json_handler = JsonHandler()

    def is_point_in_region(self, point: List[float], region: List[List[float]]) -> bool:
        """
        判断点是否在指定区域内

        Args:
            point: [x, y] 坐标点
            region: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] 区域坐标
        """
        x, y = point
        x_coords = [p[0] for p in region]
        y_coords = [p[1] for p in region]

        return (min(x_coords) <= x <= max(x_coords) and
                min(y_coords) <= y <= max(y_coords))

    def clean_thesis_title(self, title: str) -> str:
        """
        清理论文题目文本，去除"题目："和多余的空格

        Args:
            title: 原始题目文本

        Returns:
            清理后的题目文本
        """
        # 去除"题目："或"题目: "或"题目 "
        title = re.sub(r'^题目[：: ]?\s*', '', title)

        # 去除换行和多余空格
        title = ''.join(title.split())

        return title.strip()

    def extract_text_from_region(self, result: List, region: List[List[float]]) -> str:
        """
        从指定区域提取文本

        Args:
            result: OCR识别结果
            region: 目标区域坐标
        """
        texts = []
        for line in result:
            box = line[0]
            text = line[1][0]
            # 使用第一个点（左上角）判断是否在区域内
            if self.is_point_in_region(box[0], region):
                texts.append(text)
        return " ".join(texts)

    def extract_student_id(self, text: str) -> Optional[str]:
        """
        从文本中提取学号（12位数字）
        """
        if match := re.search(r'\d{12}', text):
            return match.group()
        return None

    def process_thesis(self, result: List) -> Dict[str, Any]:
        """
        处理论文本体
        """
        # 提取论文题目（合并两个区域的文本）
        title_texts = []
        for region in self.THESIS_TITLE_REGIONS:
            text = self.extract_text_from_region(result, region)
            if text:
                title_texts.append(text)

        # 合并标题并清理
        full_title = "".join(title_texts)
        cleaned_title = self.clean_thesis_title(full_title)

        # 提取学号
        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_THESIS)
        student_id = self.extract_student_id(student_id_text)

        return {
            "type": "thesis",
            "title": cleaned_title,
            "student_id": student_id
        }

    def process_report(self, result: List) -> Dict[str, Any]:
        """
        处理查重报告
        """
        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_REPORT)
        student_id = self.extract_student_id(student_id_text)

        return {
            "type": "report",
            "student_id": student_id
        }

    def process_ktbg(self, result: List) -> Dict[str, Any]:
        # 开题报告处理
        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_KTBG)
        student_id = self.extract_student_id(student_id_text)

        title = self.extract_text_from_region(result, self.KTBG_TITLE_REGION)

        return {
            "type": "ktbg",
            "title": title,
            "student_id": student_id
        }

    def process_grade(self, result: List) -> Dict[str, Any]:
        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_CJKH)
        student_id = self.extract_student_id(student_id_text)

        return {
            "type": "grade",
            "student_id": student_id
        }

    def identify_document(self, file_path: Path) -> Dict[str, Any]:
        """
        识别文档类型并提取信息

        Args:
            file_path: PDF文件路径

        Returns:
            包含文档类型和提取信息的字典
        """
        try:
            # OCR识别
            result = self.ocr.ocr(str(file_path), cls=True)
            if not result or not result[0]:  # 使用第一页的结果
                raise Exception("OCR识别失败")

            first_page_result = result[0]

            # 检查文件名是否为开题报告或成绩考核表
            file_name = file_path.name.lower()
            if "开题报告" in file_name:
                return self.process_ktbg(first_page_result)

            if "成绩考核表" in file_name:
                return self.process_grade(first_page_result)

            # 检查是否为论文本体
            for region in self.THESIS_TITLE_REGIONS:
                text = self.extract_text_from_region(first_page_result, region)
                if "题目" in text:
                    return self.process_thesis(first_page_result)

            # 检查是否为查重报告
            report_text = self.extract_text_from_region(first_page_result, self.REPORT_TITLE_REGION)
            if "文本复制检测报告单 (简洁)" in report_text:
                return self.process_report(first_page_result)

            return {"type": "unknown"}

        except Exception as e:
            raise Exception(f"文档识别失败: {str(e)}")

    def save_recognition_result(self, result: Dict[str, Any], output_dir: Path, student_id: str) -> Path:
        """
        保存识别结果

        Args:
            result: 识别结果字典
            output_dir: 输出目录路径

        Returns:
            保存的文件路径

        Raises:
            Exception: 当没有学号或保存失败时抛出异常
        """

        if not student_id:
            raise Exception("无法保存：识别结果中没有学号")

        # 保存结果
        return self.json_handler.save_to_json(result, output_dir, student_id)
