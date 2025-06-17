from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import main
app = Flask(__name__)

# 配置上传文件保存目录
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip'}

# 存储重命名参数的全局变量
rename_params = {
    'academic_year': '2324',
    'province_code': '44',
    'unit_code': '14655',
    'major_code': '080901'
}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/rename-params', methods=['POST'])
def update_rename_params():
    """更新文件重命名参数的接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '未接收到参数数据'}), 400

        # 更新参数
        for key in ['academic_year', 'province_code', 'unit_code', 'major_code']:
            if key in data:
                rename_params[key] = data[key]

        return jsonify({
            'message': '参数更新成功',
            'params': rename_params
        }), 200
    except Exception as e:
        return jsonify({'error': f'更新参数失败: {str(e)}'}), 500


@app.route('/api/rename-params', methods=['GET'])
def get_rename_params():
    """获取当前的重命名参数"""
    return jsonify(rename_params), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': '未检测到文件'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '未选择文件'}), 400

    successful_uploads = []
    failed_uploads = []

    for file in files:
        if file and allowed_file(file.filename):
            try:
                # 保留文件夹结构（如前端有 webkitRelativePath 字段）
                relative_path = file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                # 调用业务审核处理
                # from main import process_single_file
                # result = process_single_file(save_path, rename_params)
                # if result:
                successful_uploads.append(relative_path)
                # else:
                #     failed_uploads.append(relative_path)
                # 处理完成可删除
                # if os.path.exists(save_path):
                #     os.remove(save_path)
            except Exception as e:
                failed_uploads.append(f"{relative_path} (错误: {str(e)})")
        else:
            failed_uploads.append(f"{file.filename} (不支持的文件类型)")

    message = f"成功处理 {len(successful_uploads)} 个文件"
    if failed_uploads:
        message += f"\n失败 {len(failed_uploads)} 个文件: {', '.join(failed_uploads)}"

    return jsonify({
        'message': message,
        'successful': successful_uploads,
        'failed': failed_uploads
    }), 200 if successful_uploads else 400
    
@app.route('/api/review-upload', methods=['POST'])
def review_upload_folder():

    try:
        # 可以用 params 动态传递命名参数，否则用默认
        params = request.get_json() or None
        result = main.batch_review_upload(params)
        return jsonify({
            "message": f"共找到{result['total']}个PDF，成功{result['success_count']}个，失败{result['fail_count']}个",
            "detail": result
        }), 200
    except Exception as e:
        return jsonify({'error': f'批量审核失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
