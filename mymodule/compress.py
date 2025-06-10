from pathlib import Path
import zipfile
import logging
from datetime import datetime


class DocumentCompressor:
    def __init__(self):
        self.current_time = datetime.utcnow().strftime('%Y%m%d')

    def compress_files(self, files: list[tuple[Path, dict]], student_id: str, target_dir: Path) -> Path:

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
