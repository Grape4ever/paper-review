import logging
from pathlib import Path
import pandas as pd
import json
from typing import Dict, Optional, Tuple
import glob
import re
from datetime import datetime


class ExcelHandler:
    def __init__(self, excel_path: Path):
        """
        初始化Excel处理器

        Args:
            excel_path: Excel文件路径
        """
        self.current_time = "2025-05-13 03:05:48"
        self.current_user = "Grape4ever"
        self.excel_path = Path(excel_path)

        # 定义列映射
        self.COLUMN_MAPPING = {
            'student_id': 'I',  # 学号列
            'thesis_title': 'U',  # 论文题目列
            'thesis_file': 'Y',  # 论文文件名列
            'support_file': 'Z',  # 支撑材料文件名列
            'report_file': 'AA'  # 查重报告文件名列
        }

        # 加载Excel文件
        try:
            self.df = pd.read_excel(self.excel_path)
            # 确保所有列名存在
            for col in self.COLUMN_MAPPING.values():
                if col not in self.df.columns:
                    raise ValueError(f"Excel文件中缺少列 {col}")
        except Exception as e:
            logging.error(f"加载Excel文件失败: {str(e)}")
            raise

    def _get_latest_ktbg_json(self, student_id: str) -> Optional[Path]:
        """
        获取最新的开题报告JSON文件

        Args:
            student_id: 学号

        Returns:
            最新的JSON文件路径，如果没有找到则返回None
        """
        # 构建glob模式
        pattern = f"./recognition_result/{student_id}/ktbg_*.json"
        files = glob.glob(pattern)

        if not files:
            logging.warning(f"未找到学号 {student_id} 的开题报告JSON文件")
            return None

        # 从文件名提取时间戳并排序
        def get_timestamp(filepath):
            match = re.search(r'ktbg_(\d{8}_\d{6})\.json', filepath)
            if match:
                try:
                    return datetime.strptime(match.group(1), '%Y%m%d_%H%M%S')
                except ValueError:
                    return datetime.min
            return datetime.min

        # 按时间戳排序并返回最新的
        latest_file = max(files, key=get_timestamp)
        return Path(latest_file)

    def _get_json_path(self, student_id: str, type_prefix: str) -> Optional[Path]:
        """
        获取指定类型的JSON文件路径

        Args:
            student_id: 学号
            type_prefix: 文件类型前缀（thesis/report/ktbg）

        Returns:
            JSON文件路径，如果没有找到则返回None
        """
        if type_prefix == "ktbg":
            return self._get_latest_ktbg_json(student_id)

        # 构建glob模式
        pattern = f"./recognition_result/{student_id}/{type_prefix}_*.json"
        files = glob.glob(pattern)

        if not files:
            logging.warning(f"未找到学号 {student_id} 的 {type_prefix} JSON文件")
            return None

        # 如果有多个文件，使用最新的
        return Path(max(files, key=lambda f: f.stat().st_mtime))

    def _load_json_result(self, json_path: Path) -> Dict:
        """加载JSON结果文件"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载JSON文件失败 ({json_path}): {str(e)}")
            raise

    def _find_student_row(self, student_id: str) -> Optional[int]:
        """在Excel中查找学生所在行"""
        student_id_col = self.COLUMN_MAPPING['student_id']
        mask = self.df[student_id_col].astype(str) == str(student_id)
        matching_rows = self.df[mask].index

        if len(matching_rows) == 0:
            logging.warning(f"未找到学号为 {student_id} 的学生")
            return None
        elif len(matching_rows) > 1:
            logging.warning(f"找到多个学号为 {student_id} 的学生")
            return matching_rows[0]

        return matching_rows[0]

    def _compare_titles(self, row_idx: int, json_title: str) -> bool:
        """比对论文题目是否一致"""
        excel_title = str(self.df.at[row_idx, self.COLUMN_MAPPING['thesis_title']]).strip()
        json_title = str(json_title).strip()

        # 清理标题
        excel_title = re.sub(r'\s+', ' ', excel_title)
        json_title = re.sub(r'\s+', ' ', json_title)

        if excel_title.lower() != json_title.lower():
            logging.warning(
                f"题目不一致:\nExcel: {excel_title}\nJSON: {json_title}"
            )
            return False

        return True

    def process_student(self, student_id: str, file_names: Dict[str, str]) -> Tuple[bool, str]:
        """
        处理单个学生的所有文件

        Args:
            student_id: 学号
            file_names: 文件名字典 {'thesis': 文件名, 'report': 文件名, 'support': 文件名}

        Returns:
            (是否全部处理成功, 错误信息)
        """
        try:
            success = True
            messages = []

            # 查找学生
            row_idx = self._find_student_row(student_id)
            if row_idx is None:
                return False, f"未找到学号为 {student_id} 的学生"

            # 处理论文
            if 'thesis' in file_names:
                json_path = self._get_json_path(student_id, 'thesis')
                if json_path:
                    result = self._load_json_result(json_path)
                    if self._compare_titles(row_idx, result.get('title', '')):
                        self.df.at[row_idx, self.COLUMN_MAPPING['thesis_file']] = file_names['thesis']
                        messages.append("论文处理成功")
                    else:
                        success = False
                        messages.append("论文题目不匹配")
                else:
                    success = False
                    messages.append("未找到论文JSON文件")

            # 处理查重报告
            if 'report' in file_names:
                json_path = self._get_json_path(student_id, 'report')
                if json_path:
                    self.df.at[row_idx, self.COLUMN_MAPPING['report_file']] = file_names['report']
                    messages.append("查重报告处理成功")
                else:
                    success = False
                    messages.append("未找到查重报告JSON文件")

            # 处理支撑材料
            if 'support' in file_names:
                json_path = self._get_latest_ktbg_json(student_id)
                if json_path:
                    result = self._load_json_result(json_path)
                    if self._compare_titles(row_idx, result.get('title', '')):
                        self.df.at[row_idx, self.COLUMN_MAPPING['support_file']] = file_names['support']
                        messages.append("支撑材料处理成功")
                    else:
                        success = False
                        messages.append("开题报告题目不匹配")
                else:
                    success = False
                    messages.append("未找到开题报告JSON文件")

            # 保存Excel
            if success or any(messages):
                self.df.to_excel(self.excel_path, index=False)

            return success, "; ".join(messages)

        except Exception as e:
            error_msg = f"处理学生 {student_id} 的文件时出错: {str(e)}"
            logging.error(error_msg)
            return False, error_msg