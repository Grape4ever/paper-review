import json
from typing import Dict, Any
from pathlib import Path
# import os
from datetime import datetime


class JsonHandler:
    @staticmethod
    def save_to_json(data: Dict[str, Any], json_base_dir: Path, student_id: str) -> Path:

        try:
            # 在recognition_results下创建学号目录
            student_dir = json_base_dir / str(student_id)
            student_dir.mkdir(parents=True, exist_ok=True)

            # 构造文件名：类型_时间戳.json
            doc_type = data.get('type', 'unknown')
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_name = f"{doc_type}_{timestamp}.json"
            file_path = student_dir / file_name

            # 在保存前添加时间戳和用户信息到数据中
            data_with_metadata = {
                **data,
                "created_at": datetime.utcnow().strftime('%Y%m%d')
            }

            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_with_metadata, f, ensure_ascii=False, indent=4)

            return file_path

        except Exception as e:
            raise Exception(f"保存JSON文件失败: {str(e)}")

    @staticmethod
    def load_from_json(file_path: Path) -> Dict[str, Any]:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"读取JSON文件失败: {str(e)}")
