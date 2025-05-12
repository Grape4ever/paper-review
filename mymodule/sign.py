import json

import fitz
import numpy as np
import cv2
from pathlib import Path
import logging


class SignatureDetector:
    def __init__(self):
        self.current_time = "2025-05-12 05:25:23"

        # 定义签名区域坐标
        self.SIGNUP_REGION = [
            [852.0, 691.0], [1010.0, 691.0],
            [1010.0, 963.0], [852.0, 963.0]
        ]

    def check_area_content(self, pdf_path: Path, page_num: int = 1,
                           area_coords: list = None, threshold: float = 0.001) -> dict:
        """
        检查PDF指定区域是否有内容

        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从0开始）
            area_coords: 区域坐标，如果为None则使用默认的SIGNUP_REGION
            threshold: 非空白像素占比阈值，默认0.001（0.1%）

        Returns:
            dict: 检测结果
        """
        try:
            # 如果未指定区域坐标，使用默认值
            if area_coords is None:
                area_coords = self.SIGNUP_REGION

            # 计算矩形区域的左上角和右下角坐标
            x0 = min(area_coords[0][0], area_coords[3][0])
            y0 = min(area_coords[0][1], area_coords[1][1])
            x1 = max(area_coords[1][0], area_coords[2][0])
            y1 = max(area_coords[2][1], area_coords[3][1])

            # 打开PDF
            doc = fitz.open(pdf_path)
            page = doc[page_num]

            # 获取页面图像
            zoom = 2  # 放大倍数，提高清晰度
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # 转换为numpy数组
            img = np.frombuffer(pix.samples, dtype=np.uint8)
            img = img.reshape(pix.height, pix.width, pix.n)

            # 提取指定区域
            # 考虑zoom因子
            x0, y0 = int(x0 * zoom), int(y0 * zoom)
            x1, y1 = int(x1 * zoom), int(y1 * zoom)
            area_img = img[y0:y1, x0:x1]

            # 转换为灰度图
            if len(area_img.shape) == 3:
                gray = cv2.cvtColor(area_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = area_img

            # 二值化处理
            _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

            # 计算非空白像素比例
            total_pixels = binary.shape[0] * binary.shape[1]
            non_white_pixels = np.sum(binary > 0)
            content_ratio = non_white_pixels / total_pixels

            # 判断是否有内容
            has_content = content_ratio > threshold

            # 构建结果
            result = {
                "has_content": has_content,
                "content_ratio": float(content_ratio),
                "threshold": threshold,
                "area_size": {
                    "original": [int(x1 / zoom - x0 / zoom), int(y1 / zoom - y0 / zoom)],
                    "zoomed": [int(x1 - x0), int(y1 - y0)]
                },
                "non_white_pixels": int(non_white_pixels),
                "total_pixels": int(total_pixels),
                "coordinates": {
                    "original": [[x0 / zoom, y0 / zoom], [x1 / zoom, y1 / zoom]],
                    "zoomed": [[x0, y0], [x1, y1]]
                }
            }

            doc.close()
            return result

        except Exception as e:
            logging.error(f"区域内容检测失败: {str(e)}")
            raise

    def save_check_result(self, result: dict, save_dir: Path,
                          student_id: str, save_image: bool = False) -> Path:
        """
        保存检查结果

        Args:
            result: 检查结果
            save_dir: 保存目录
            student_id: 学号
            save_image: 是否保存区域图像

        Returns:
            保存的文件路径
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 构建保存数据
        save_data = {
            "student_id": student_id,
            "check_time": self.current_time,
            "result": result
        }

        # 生成文件名
        filename = f"signature_check_{student_id}_{self.current_time.replace(' ', '_').replace(':', '')}.json"
        save_path = save_dir / filename

        # 保存JSON文件
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return save_path