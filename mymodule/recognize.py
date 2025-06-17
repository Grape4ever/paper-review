
from pathlib import Path
from typing import Dict, Any, List, Optional
from paddleocr import PaddleOCR

import re
from mymodule.json_helper import JsonHandler


class DocumentRecognizer:
    # 定义常量
    PAGE_NUM = 2

    # 定义区域坐标
    THESIS_TITLE_REGIONS = [
        [0.0, 200.0], [1000.0, 200.0], [1000.0, 800.0], [0.0, 800.0]
    ]

    REPORT_TITLE_REGION = [
        [0.0, 300.0], [1000.0, 300.0], [1000.0, 800.0], [0.0, 800.0]
    ]

    KTBG_TITLE_REGION = [
        [0.0, 0.0], [1000.0, 0.0], [1000.0, 440.0], [0.0, 440.0]
    ]

    STUDENT_ID_REGION_THESIS = [
        [500.0, 900.0], [900.0, 900.0], [900.0, 1300.0], [500.0, 1300.0]
    ]

    STUDENT_ID_REGION_REPORT = [
        [80.0, 350.0], [500.0, 350.0], [500.0, 390.0], [80.0, 390.0]
    ]

    STUDENT_ID_REGION_KTBG = [
        # [613.0, 333.0], [744.0, 333.0], [744.0, 358.0], [613.0, 358.0]
        [195.0, 0.0], [1000.0, 0.0], [1000.0, 440.0], [195.0, 440.0]
    ]

    STUDENT_ID_REGION_CJKH = [
        [500.0, 300.0], [1000.0, 300.0], [1000.0, 500.0], [500.0, 500.0]
    ]

    SIGNUP_REGION = [
        [852.0, 691.0], [1010.0, 691.0], [1010.0, 963.0], [852.0, 963.0]
    ]

    def __init__(self):
        """初始化OCR对象"""
        self.current_file_path = None
        self.ocr = PaddleOCR(
            det_model_dir="PP-OCRv5_server_det",
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="PP-OCRv5_server_rec",
            use_doc_orientation_classify=False,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
            use_doc_unwarping=False,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
            use_textline_orientation=False,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
            page_num=self.PAGE_NUM,
            det_db_thresh=0.1,  # 降低检测阈值（默认0.3）
            det_db_box_thresh=0.1,  # 降低框阈值（默认0.6）
            det_db_unclip_ratio=2.0  # 扩大文本框范围（默认1.5）
        )
        # self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=self.PAGE_NUM)
        self.json_handler = JsonHandler()

    def is_point_in_region(self, point: List[float], region: List[List[float]]) -> bool:
        x, y = point
        x_coords = [p[0] for p in region]
        y_coords = [p[1] for p in region]
        return (min(x_coords) <= x <= max(x_coords) and
                min(y_coords) <= y <= max(y_coords))

    def clean_thesis_title(self, title: str) -> str:

        # 去除"题目："或"题目: "或"题目 "
        title = re.sub(r'.*题目[：: ]?\s*', '', title)
        # print("title:" + title)
        # 去除换行和多余空格
        title = ''.join(title.split())

        return title.strip()

    def extract_title_with_pattern(self, text: str) -> Optional[str]:
        """
        使用正则表达式从文本中提取论文题目

        Args:
            text: 待匹配的文本
        """

        pattern = r"题[\s]*目([\s\S]*?)学生姓名"
        if match := re.search(pattern, text, re.DOTALL):  # 使用DOTALL标志允许匹配跨行文本
            title = match.group(1).strip()
            print("成功了")
            return title

        return None

    def extract_text_from_region(self, result: List, region: List[List[float]]) -> str:  # 从指定区域提取文本

        texts = []
        for line in result:
            box = line[0]
            text = line[1][0]
            # 使用第一个点（左上角）判断是否在区域内
            if self.is_point_in_region(box[0], region):
                texts.append(text)
        return " ".join(texts)

    def extract_student_id(self, text: str) -> Optional[str]:

        if match := re.search(r'\d{12}', text):
            return match.group()
        return None

    def has_signature(self, second_page_result):
        """
        判断毕业论文第二页有无签名
        :param second_page_result: OCR识别后的第二页结果，通常是List
        :return: True/False
        """
        # 拼接所有文本内容
        all_text = " ".join([line[1][0] for line in second_page_result if line[1][0].strip()])
        # 正则匹配 签名： 和 日期 之间的内容，可跨行
        # print("all_text", all_text)
        pattern = r"签名\s*[:：]\s*(.*?)\s*日期"
        match = re.search(pattern, all_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # print("content" + content)
            # 判断内容是否为空（可以根据需要添加更严格的判断，比如长度、是否全是标点等）
            return bool(content)
        else:
            # 没有匹配到“签名”和“日期”，也视为无签名
            return False

    def process_thesis(self, result: List) -> Dict[str, Any]:

        text = self.extract_text_from_region(result[0], self.THESIS_TITLE_REGIONS)
        # print(text)
        cleaned_title = self.clean_thesis_title(text)
        # print(cleaned_title)
        # 提取学号s
        student_id_text = self.extract_text_from_region(result[0], self.STUDENT_ID_REGION_THESIS)

        student_id = self.extract_student_id(student_id_text)
        signature_result = self.has_signature(result[1])
        if signature_result:
            return {
                "type": "thesis",
                "title": cleaned_title,
                "student_id": student_id,
                "signature": "true"
            }
        # return {
        #     "type": "thesis",
        #     "title": cleaned_title,
        #     "student_id": student_id
        # }
        raise Exception("毕业论文作者未签名")

    def process_report(self, result: List) -> Dict[str, Any]:

        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_REPORT)
        student_id = self.extract_student_id(student_id_text)
        # print(student_id_text)
        # print(student_id)

        return {
            "type": "report",
            "student_id": student_id
        }

    def process_ktbg(self, result: List) -> Dict[str, Any]:
        # 开题报告处理
        student_id_text = self.extract_text_from_region(result, self.STUDENT_ID_REGION_KTBG)
        student_id = self.extract_student_id(student_id_text)

        # title_texts = []

        text = self.extract_text_from_region(result, self.KTBG_TITLE_REGION)

        # 合并标题文本并尝试正则匹配
        # full_title = " ".join(title_texts)
        title = self.extract_title_with_pattern(text)
        # if not title:
        #     # 如果正则匹配失败，使用原有的清理方法作为备选
        #     title = self.clean_thesis_title(text)

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

    def identify_document(self, file_path: Path) -> Dict[str, Any]:  # 识别文档类型并提取信息

        try:
            # OCR识别
            file_path_str = str(file_path)
            result = self.ocr.ocr(file_path_str)
            if not result or not result[0]:  # 使用第一页的结果
                raise Exception("OCR识别失败")

            first_page_result = result[0]
            # second_page_result = result[1]
            self.current_file_path = Path(file_path)

            # 检查文件名是否为开题报告或成绩考核表
            file_name = file_path.name.lower()
            if "开题报告" in file_name:
                return self.process_ktbg(first_page_result)

            if "成绩考核表" in file_name:
                return self.process_grade(first_page_result)

            # 检查是否为论文本体
            text = self.extract_text_from_region(first_page_result, self.THESIS_TITLE_REGIONS)
           
            skip_words = ["任务书", "中期检查", "评审", "答辩", "进展情况", "过程记录"]
            if any(word in text for word in skip_words):
                raise Exception(f"检测到需跳过的关键词: {', '.join([w for w in skip_words if w in text])}")
            if "题目" in text:
                return self.process_thesis(result)

            # 检查是否为查重报告
            report_text = self.extract_text_from_region(first_page_result, self.REPORT_TITLE_REGION)
            # print("report_text:" + report_text)
            if "检测" in report_text:
                return self.process_report(first_page_result)

            return {"type": "unknown"}

        except Exception as e:
            raise Exception(str(e))

    def save_recognition_result(self, result: Dict[str, Any], output_dir: Path, student_id: str) -> Path:

        if not student_id:
            raise Exception("无法保存：识别结果中没有学号")

        return self.json_handler.save_to_json(result, output_dir, student_id)
