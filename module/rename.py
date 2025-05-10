import os


def rename_file(old_path, student_id, type_id, suffix, year='2425', province_id='44',
                unit_id='14655', major_id='000000'):
    """
    重命名PDF文件为指定格式：年_省_单位_专业_学号_类型.后缀

    :param old_path: 原始PDF路径
    :param student_id: 学号
    :param type_id: 文件类型（如 LW, CCBG）
    :param year: 学年度（默认2425）
    :param province_id: 省份代码（默认44）
    :param unit_id: 单位代码（默认14655）
    :param major_id: 专业代码（默认000000）
    :param suffix: 文件后缀
    :return: 新文件路径
    """

    # 构造目标文件名
    new_filename = f"{year}_{province_id}_{unit_id}_{major_id}_{student_id}_{type_id}.{suffix}"

    # 替换非法字符
    invalid_chars = r'\/:*?"<>|'
    for c in invalid_chars:
        new_filename = new_filename.replace(c, "_")

    # 构造新路径
    new_path = os.path.join(os.path.dirname(old_path), new_filename)

    # 执行重命名
    os.rename(old_path, new_path)
    print(f"文件已重命名为：{new_path}")
    return new_path
