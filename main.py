from module.recognize import process_pdf_file

pdf_path = "./test/2324_44_14655_080901_202001020107_LW.pdf"
excel_path = "data/学生论文题目.xlsx"
process_pdf_file(pdf_path, excel_path)
# def is_in_vertical_range(box, y_min_limit, y_max_limit):
#     """
#     判断 OCR 识别的 box 是否在指定的纵坐标区间内
#
#     参数:
#     - box: 文本框四个点坐标的列表 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
#     - y_min_limit: 区域下界，例如 500
#     - y_max_limit: 区域上界，例如 650
#
#     返回:
#     - True 表示 box 在该区域内，False 表示不在
#     """
#     y_coords = [point[1] for point in box]
#     y_min = min(y_coords)
#     y_max = max(y_coords)
#     return (y_min_limit <= y_min <= y_max_limit) or \
#         (y_min_limit <= y_max <= y_max_limit)


# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
# PAGE_NUM = 2  # 将识别页码前置作为全局，防止后续打开pdf的参数和前文识别参数不一致 / Set the recognition page number
# pdf_path = './test/2324_44_14655_080901_202001020107_LW.pdf'
# ocr = PaddleOCR(use_angle_cls=True, lang="ch",
#                 page_num=PAGE_NUM)
# result = ocr.ocr(pdf_path, cls=True)
# for idx in range(len(result)):
#     res = result[idx]
#     if res == None:  # 识别到空页就跳过，防止程序报错 / Skip when empty result detected to avoid TypeError:NoneType
#         print(f"[DEBUG] Empty page {idx + 1} detected, skip it.")
#         continue
#     for line in res:
#         box = line[0]
#         # if is_in_vertical_range(box, 500, 650):
#             # print(f"[题目区域] {line[1][0]} (score={line[1][1]:.3f})")
#         print(line)


