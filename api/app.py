from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main
app = Flask(__name__)

# 配置上传文件保存目录
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    academic_year = request.form.get('academic_year', '2324')
    province_code = request.form.get('province_code', '44')
    unit_code = request.form.get('unit_code', '14655')
    major_code = request.form.get('major_code', '080901')

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
                relative_path = file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], relative_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                successful_uploads.append(relative_path)
            except Exception as e:
                failed_uploads.append(f"{relative_path} (错误: {str(e)})")
        else:
            failed_uploads.append(f"{file.filename} (不支持的文件类型)")

    message = f"成功上传 {len(successful_uploads)} 个文件"
    if failed_uploads:
        message += f"\n失败 {len(failed_uploads)} 个文件: {', '.join(failed_uploads)}"

    return jsonify({
        'message': message,
        'successful': successful_uploads,
        'failed': failed_uploads
    }), 200 if successful_uploads else 400
    
@app.route('/api/review-upload', methods=['POST'])
def review_upload_folder():
    """批量审核 uploads 目录下所有pdf文件"""
    try:
        # 支持参数从json body接收
        data = request.get_json() or {}
        params = {
            'academic_year': data.get('academic_year', '2324'),
            'province_code': data.get('province_code', '44'),
            'unit_code': data.get('unit_code', '14655'),
            'major_code': data.get('major_code', '080901')
        }
        result = main.batch_review_upload(params)
        return jsonify({
            "message": f"共找到{result['total']}个PDF，成功{result['success_count']}个，失败{result['fail_count']}个",
            "details": result["details"]
        }), 200
    except Exception as e:
        return jsonify({'error': f'批量审核失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
