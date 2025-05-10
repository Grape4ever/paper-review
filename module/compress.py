# zip
import zipfile
import os


def zip_files(file_list, output_path='temp_output.zip'):
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for f in file_list:
            arcname = os.path.basename(f)
            zipf.write(f, arcname=arcname)
    print(f"已压缩为：{output_path}")
    return output_path


# 示例用法（可以注释掉，只在调试时用）
files = ['./test/开题报告.pdf', './test/成绩考核表.pdf']
zip_files(files, 'output.zip')
