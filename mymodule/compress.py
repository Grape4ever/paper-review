from pathlib import Path
import zipfile
import logging


class DocumentCompressor:
    def __init__(self):
        self.current_time = "2025-05-11 07:17:45"
        self.current_user = "Grape4ever"

    def compress_files(self, files: list[tuple[Path, dict]], student_id: str, target_dir: Path) -> Path:
        """
        直接压缩文件（开题报告和成绩考核表）

        Args:
            files: 要压缩的文件列表，每个元素是(文件路径, 识别结果)的元组
            student_id: 学号
            target_dir: 目标目录

        Returns:
            压缩文件的路径
        """
        try:
            # 确保学号目录存在
            student_dir = target_dir / str(student_id)
            student_dir.mkdir(parents=True, exist_ok=True)

            # 创建zip文件
            zip_name = f"{student_id}_CL.zip"
            zip_path = student_dir / zip_name

            # 如果zip文件已存在，先删除
            if zip_path.exists():
                zip_path.unlink()

            # 压缩文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, _ in files:
                    # 将文件添加到压缩包，只使用文件名
                    zipf.write(file_path, file_path.name)
                    logging.info(f"已添加文件到压缩包: {file_path.name}")

            logging.info(f"创建压缩文件成功: {zip_path}")
            return zip_path

        except Exception as e:
            raise Exception(f"压缩文件失败: {str(e)}")