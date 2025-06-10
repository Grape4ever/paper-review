from paddleocr import PaddleOCR

PAGE_NUM = 2  # 将识别页码前置作为全局，防止后续打开pdf的参数和前文识别参数不一致 / Set the recognition page number
pdf_path = './ZCCBG.pdf'

ocr = PaddleOCR(
    det_model_dir="PP-OCRv5_server_det",
    # text_detection_model_name="PP-OCRv5_server_det",
    # text_recognition_model_name="PP-OCRv5_server_rec",
    use_doc_orientation_classify=False,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
    use_doc_unwarping=False,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
    use_textline_orientation=False,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
    page_num=PAGE_NUM,
    det_db_thresh=0.1,  # 降低检测阈值（默认0.3）
    det_db_box_thresh=0.1,  # 降低框阈值（默认0.6）
    det_db_unclip_ratio=2.0,  # 扩大文本框范围（默认1.5）

)
result = ocr.ocr(pdf_path)
print(result[0])
