from pathlib import Path
from typing import Dict, Any
import shutil
from mymodule.json_helper import JsonHandler


class FileRenamer:

    # 文件类型映射
    FILE_TYPE_MAPPING = {
        "thesis": "LW",  # 论文
        "report": "CCBG",  # 查重报告
        "ktbg": "CL",
        "grade": "CL"  # 支撑材料
    }

    def __init__(self, 
                 academic_year: str = "2324", 
                 province_code: str = "44",
                 unit_code: str = "14655", major_code: str = "080901"):
        self.json_handler = JsonHandler()
        self.academic_year = academic_year  # 学年度
        self.province_code = province_code  # 省市代码
        self.unit_code = unit_code  # 单位代码
        self.major_code = major_code  # 专业代码

    def generate_new_filename(self, json_data: Dict[str, Any], suffix: str) -> str:

        # 获取学号
        student_id = json_data.get('student_id')
        if not student_id:
            raise ValueError("JSON数据中缺少学号信息")

        # 获取文件类型
        doc_type = json_data.get('type')
        if not doc_type:
            raise ValueError("JSON数据中缺少文件类型信息")

        # 映射文件类型
        file_type = self.FILE_TYPE_MAPPING.get(doc_type)
        if not file_type:
            raise ValueError(f"未知的文件类型: {doc_type}")

        # 构造新文件名
        new_filename = f"{self.academic_year}_{self.province_code}_{self.unit_code}_{self.major_code}_{student_id}_{file_type}.{suffix}"

        return new_filename

    def rename_file(self, source_file: Path, json_file: Path, target_dir: Path) -> Path:

        try:
            # 检查文件是否存在
            if not source_file.exists():
                raise FileNotFoundError(f"源文件不存在: {source_file}")
            if not json_file.exists():
                raise FileNotFoundError(f"JSON文件不存在: {json_file}")

            # 创建目标目录
            target_dir.mkdir(parents=True, exist_ok=True)

            # 读取JSON数据
            json_data = self.json_handler.load_from_json(json_file)

            # 生成新文件名
            new_filename = self.generate_new_filename(json_data, source_file.suffix.lstrip('.'))

            # 构造目标文件路径
            target_file = target_dir / new_filename

            # 如果目标文件已存在，先删除
            if target_file.exists():
                target_file.unlink()

            # 复制文件到新位置并重命名
            shutil.copy2(source_file, target_file)

            print(f"文件重命名成功: {target_file}")
            return target_file

        except Exception as e:
            raise Exception(f"重命名文件时发生错误: {str(e)}")
