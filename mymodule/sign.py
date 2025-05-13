import json
import fitz
import numpy as np
import cv2
from pathlib import Path
import logging


# 未做好！！！！！！！！！！！

class SignatureDetector:
    def __init__(self):
        self.current_time = "2025-05-12 15:18:29"
        self.current_user = "Grape4ever"

        # 签名区域坐标
        self.SIGNUP_REGION = [
            [400.0, 500.0], [500.0, 500.0],
            [500.0, 600.0], [400.0, 600.0]
        ]

    def _convert_to_serializable(self, obj):
        """转换NumPy类型为Python原生类型"""
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def check_area_content(self, pdf_path: Path, page_num: int = 1,
                           area_coords: list = None, threshold: float = 0.001) -> dict:
        """
        检查PDF指定区域是否有内容
        """
        try:
            pdf_path = Path(pdf_path) if not isinstance(pdf_path, Path) else pdf_path
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

            if area_coords is None:
                area_coords = self.SIGNUP_REGION

            doc = fitz.open(pdf_path)

            try:
                if page_num >= len(doc):
                    raise ValueError(f"页码 {page_num} 超出PDF页数范围 (总页数: {len(doc)})")

                page = doc[page_num]

                # 获取页面信息
                page_width = float(page.rect.width)
                page_height = float(page.rect.height)

                # 获取页面图像
                pix = page.get_pixmap(dpi=300)

                # 计算缩放比例
                scale_x = pix.width / page_width
                scale_y = pix.height / page_height

                # 计算坐标
                x0 = int(min(area_coords[0][0], area_coords[3][0]) * scale_x)
                y0 = int(min(area_coords[0][1], area_coords[1][1]) * scale_y)
                x1 = int(max(area_coords[1][0], area_coords[2][0]) * scale_x)
                y1 = int(max(area_coords[2][1], area_coords[3][1]) * scale_y)

                # 确保坐标在有效范围内
                x0 = max(0, min(x0, pix.width))
                y0 = max(0, min(y0, pix.height))
                x1 = max(0, min(x1, pix.width))
                y1 = max(0, min(y1, pix.height))

                # 转换图像
                img = np.frombuffer(pix.samples, dtype=np.uint8)
                img = img.reshape(pix.height, pix.width, pix.n)

                # 提取区域
                area_img = img[y0:y1, x0:x1]

                if area_img.size == 0:
                    raise ValueError("提取的图像区域为空")

                # 转换为灰度图
                if len(area_img.shape) == 3:
                    gray = cv2.cvtColor(area_img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = area_img

                # 二值化处理
                _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

                # 计算非空白像素比例
                total_pixels = int(binary.shape[0] * binary.shape[1])
                non_white_pixels = int(np.sum(binary > 0))
                content_ratio = float(non_white_pixels) / float(total_pixels)

                # 构建结果（确保所有值都是可序列化的）
                result = {
                    "has_content": bool(content_ratio > threshold),
                    "content_ratio": float(content_ratio),
                    "threshold": float(threshold),
                    "debug_info": {
                        "pdf_size": [float(page_width), float(page_height)],
                        "image_size": [int(pix.width), int(pix.height)],
                        "scale_factors": [float(scale_x), float(scale_y)],
                        "original_coords": [[float(x), float(y)] for x, y in area_coords],
                        "scaled_coords": [int(x0), int(y0), int(x1), int(y1)],
                        "extracted_area_shape": [int(x) for x in area_img.shape]
                    },
                    "extraction_info": {
                        "non_white_pixels": int(non_white_pixels),
                        "total_pixels": int(total_pixels)
                    }
                }

                return result

            finally:
                doc.close()

        except Exception as e:
            logging.error(f"区域内容检测失败 - 文件: {pdf_path}, 页码: {page_num}, 错误: {str(e)}")
            logging.error("调用栈:", exc_info=True)
            raise

    def save_check_result(self, result: dict, save_dir: Path,
                          student_id: str) -> Path:
        """保存检查结果到JSON文件"""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 转换结果中的所有值为可序列化的类型
        converted_result = json.loads(
            json.dumps(result, default=self._convert_to_serializable)
        )

        save_data = {
            "student_id": student_id,
            "check_time": self.current_time,
            "checker": self.current_user,
            "result": converted_result
        }

        filename = f"signature_check_{student_id}_{self.current_time.replace(' ', '_').replace(':', '')}.json"
        save_path = save_dir / filename

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        return save_path
