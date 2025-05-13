from pathlib import Path
from mymodule.recognize import DocumentRecognizer
from mymodule.rename import FileRenamer
from mymodule.compress import DocumentCompressor
from mymodule.excel_handle import ExcelHandler
import logging
from datetime import datetime


# import os
# from paddleocr import PaddleOCR


class DocumentProcessor:
    def __init__(self):
        self.recognizer = DocumentRecognizer()
        self.renamer = FileRenamer()
        self.compressor = DocumentCompressor()
        self.excel_handler = ExcelHandler(Path("./res/学生论文题目.xlsx"))

        # 设置目录结构
        self.root_dir = Path(".")
        self.res_dir = self.root_dir / "res"  # 重命名文件目录
        self.json_dir = self.root_dir / "recognition_results"  # JSON文件目录
        self.input_dir = self.root_dir / "test"  # 输入文件目录
        self.log_dir = self.root_dir / "logs"  # 日志目录
        self.compress_files = {}  # 学号 -> 文件列表的映射

        # 创建所有必要的目录
        self.create_directory_structure()

        # 设置日志
        self.setup_logging()

    def create_directory_structure(self):
        """创建必要的目录结构"""
        dirs = [self.res_dir, self.json_dir, self.input_dir, self.log_dir]
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
            logging.info(f"确保目录存在: {dir_path}")

    def setup_logging(self):
        """设置日志配置"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"document_processing_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def process_document(self, file_path: Path) -> bool:

        global renamed_path
        try:
            logging.info(f"开始处理文件: {file_path}")

            # 1. 文件识别
            recognition_result = self.recognizer.identify_document(file_path)
            student_id = recognition_result.get('student_id')

            if recognition_result.get('type') == 'ktbg' or recognition_result.get('type') == 'grade':
                if student_id not in self.compress_files:
                    self.compress_files[student_id] = []
                self.compress_files[student_id].append((file_path, recognition_result))
                logging.info(f"添加文件到待压缩列表: {file_path}")

            # 3. 在res目录下创建学号目录
            student_res_dir = self.res_dir / str(student_id)
            student_res_dir.mkdir(exist_ok=True)
            logging.info(f"确保res下的学号目录存在: {student_res_dir}")

            # 4. 保存识别结果到recognition_results下的学号目录
            json_path = self.recognizer.save_recognition_result(
                recognition_result,
                self.json_dir,  # 传入json基础目录，student_id会在JsonHandler中使用
                student_id
            )
            logging.info(f"识别结果已保存: {json_path}")

            # 5. 重命名文件并保存到res下的学号目录
            if recognition_result.get('type') == 'thesis' or recognition_result.get('type') == 'report':
                renamed_path = self.renamer.rename_file(
                    file_path,
                    json_path,
                    student_res_dir
                )
                logging.info(f"文件重命名完成: {renamed_path}")

            # 更新Excel
            file_type_mapping = {
                "thesis": "thesis",
                "report": "report",
                "ktbg": "support"
            }
            doc_type = recognition_result.get('type')

            if doc_type in file_type_mapping:
                file_names = {file_type_mapping[doc_type]: renamed_path.name}
                success, message = self.excel_handler.process_student(student_id, file_names)
                if not success:
                    logging.warning(f"Excel更新失败: {message}")
                else:
                    logging.info(f"Excel更新成功: {message}")

            return True


        except Exception as e:
            logging.error(f"处理文件时出错 {file_path}: {str(e)}")
            return False

    def process_compressed_files(self):
        """处理需要压缩的文件"""
        try:
            # 处理每个学号的文件
            for student_id, files in self.compress_files.items():
                if files:
                    logging.info(f"正在处理学号 {student_id} 的文件")

                    # # 先保存所有文件的JSON结果
                    # for _, recognition_result in files:
                    #     self.recognizer.save_recognition_result(
                    #         recognition_result,
                    #         self.json_dir,
                    #         student_id
                    #     )

                    # 使用第一个文件的识别结果作为重命名的依据
                    first_file_result = files[0][1]  # 获取第一个文件的识别结果
                    json_path = self.recognizer.save_recognition_result(
                        first_file_result,
                        self.json_dir,
                        student_id
                    )

                    # 压缩文件
                    zip_path = self.compressor.compress_files(
                        files,
                        student_id,
                        self.res_dir
                    )

                    # 重命名zip文件
                    renamed_zip = self.renamer.rename_file(
                        zip_path,
                        json_path,
                        zip_path.parent
                    )
                    logging.info(f"重命名压缩文件成功: {renamed_zip}")

                    # 删除原始zip文件（如果重命名后的文件存在且不同）
                    if renamed_zip != zip_path and zip_path.exists():
                        zip_path.unlink()
                        logging.info(f"删除原始压缩文件: {zip_path}")

        except Exception as e:
            logging.error(f"处理压缩文件时出错: {str(e)}")
            raise


def main():
    try:
        processor = DocumentProcessor()

        # 处理所有PDF文件
        pdf_files = list(processor.input_dir.glob("*.pdf"))
        if not pdf_files:
            print("没有找到需要处理的PDF文件")
            return

        print(f"找到 {len(pdf_files)} 个PDF文件待处理")
        for pdf_file in pdf_files:
            if processor.process_document(pdf_file):
                print(f"文件处理成功: {pdf_file}")
            else:
                print(f"文件处理失败: {pdf_file}")

        processor.process_compressed_files()
        print("所有文件处理完成")

    except Exception as e:
        print(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
