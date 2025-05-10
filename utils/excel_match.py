import json
import openpyxl


def match_and_rename_excel_entry(json_path, excel_path):
    # 加载识别信息 JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    student_id = data.get("student_id", "").strip()
    title = data.get("title", "").strip()
    file_type = data.get("file_type", "").strip()  # 'LW' 或 'CCBG'
    filename = data.get("filename", "").strip()

    if not all([student_id, file_type, filename]):
        print("缺失必要字段，无法匹配 Excel。")
        return

    # 打开 Excel 表
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    matched = False

    for row in sheet.iter_rows(min_row=2):
        sid_cell = row[8]  # I列（索引从0开始）
        title_cell = row[20]  # U列
        lw_cell = row[24]  # Y列
        cc_cell = row[26]  # AA列

        if sid_cell.value and str(sid_cell.value).strip() == student_id:
            if file_type == "LW":
                if title and title.strip() in str(title_cell.value).strip():
                    lw_cell.value = filename
                    matched = True
                    break
            elif file_type == "CCBG":
                cc_cell.value = filename
                matched = True
                break

    if matched:
        wb.save(excel_path)
        print(f"[INFO] 成功匹配并写入文件名：{filename}")
    else:
        print(f"[WARN] 未能在 Excel 中找到匹配学号/题目：{student_id} / {title}")
