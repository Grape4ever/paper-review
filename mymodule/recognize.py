import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from paddleocr import PaddleOCR
import re
from mymodule.json_helper import JsonHandler
from mymodule.sign import SignatureDetector


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

    SIGNUP_REGION = [
        [852.0, 691.0], [1010.0, 691.0], [1010.0, 963.0], [852.0, 963.0]
    ]

    def __init__(self):
        """初始化OCR对象"""
        self.current_file_path = None
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

    def check_signature_area(self, pdf_path: Path, student_id: str,
                             save_dir: Path = Path("check_results")) -> dict:
        """
        检查论文签名区域是否有内容

        Args:
            pdf_path: PDF文件路径
            student_id: 学号
            save_dir: 保存目录路径

        Returns:
            dict: 检查结果
        """
        try:
            detector = SignatureDetector()

            # 检查签名区域内容（第二页）
            result = detector.check_area_content(
                pdf_path=pdf_path,  # 使用传入的pdf_path参数
                page_num=1,  # 第二页
                threshold=0.001  # 可以调整阈值
            )

            # 保存检查结果
            result_path = detector.save_check_result(
                result=result,
                save_dir=save_dir,
                student_id=student_id
            )

            return {
                "student_id": student_id,
                "has_signature": result["has_content"],
                "content_ratio": result["content_ratio"],
                "check_time": detector.current_time,
                "result_file": str(result_path)
            }

        except Exception as e:
            logging.error(f"签名区域检查失败: {str(e)}")
            raise

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

        signature_result = self.check_signature_area(
            pdf_path=self.current_file_path,  # 需要在类中添加current_file_path属性
            student_id=student_id
        )

        if signature_result["has_signature"]:
            return {
                "type": "thesis",
                "title": cleaned_title,
                "student_id": student_id
            }
        raise Exception("毕业论文作者未签名")

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
            self.current_file_path = Path(file_path)

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
