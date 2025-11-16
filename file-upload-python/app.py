from flask import Flask, request, render_template, send_from_directory, Response
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Tạo thư mục uploads nếu chưa có
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flag ẩn trong file
FLAG_FILE = '/app/flag.txt'

def execute_php(filepath, query_string=''):
    """Thực thi file PHP và trả về output"""
    try:
        # Tạo biến môi trường cho PHP-CGI
        env = os.environ.copy()
        env['REQUEST_METHOD'] = 'GET'
        env['REDIRECT_STATUS'] = '200'
        env['SCRIPT_FILENAME'] = os.path.abspath(filepath)
        env['QUERY_STRING'] = query_string
        
        # Thực thi PHP-CGI (không truyền filepath làm argument)
        result = subprocess.run(
            ['php-cgi'],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            cwd=os.path.dirname(os.path.abspath(filepath))
        )
        
        output = result.stdout
        if '\n\n' in output:
            parts = output.split('\n\n', 1)
            return parts[1] if len(parts) > 1 else output
        elif '\r\n\r\n' in output:
            parts = output.split('\r\n\r\n', 1)
            return parts[1] if len(parts) > 1 else output
        
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Command timeout"
    except FileNotFoundError:
        return "Error: PHP-CGI not found on server"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    message_type = None
    uploaded_file = None  # Lưu tên file vừa upload
    
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file selected!'
            message_type = 'error'
        else:
            file = request.files['file']
            if file.filename == '':
                message = 'No file selected!'
                message_type = 'error'
            else:
                filename = file.filename
                
                # Kiểm tra blacklist extension 
                if '.php' in filename.lower():
                    filename = filename.replace('.php', '').replace('.PHP', '').replace('.Php', '')
                    
                if '.' in filename:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    message = f'File uploaded successfully: {filename}'
                    message_type = 'success'
                    uploaded_file = filename  # Lưu tên file đã upload
                else:
                    message = 'Invalid file! File must have an extension.'
                    message_type = 'error'
    
    return render_template('index.html', message=message, message_type=message_type, uploaded_file=uploaded_file)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Thực thi file PHP đã upload
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Kiểm tra file có tồn tại không
    if not os.path.exists(filepath):
        return "File not found", 404
    
    # Nếu là file PHP, thực thi nó
    if filename.endswith('.php'):
        # Lấy query string từ request
        query_string = request.query_string.decode('utf-8')
        output = execute_php(filepath, query_string)
        return Response(output, mimetype='text/html')
    
    # Các file khác thì trả về bình thường
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Endpoint ẩn để tạo flag file (chỉ dùng khi khởi động container)
@app.route('/init_flag_secret_endpoint_123', methods=['GET'])
def init_flag():
    if not os.path.exists(FLAG_FILE):
        with open(FLAG_FILE, 'w') as f:
            f.write('FLAG{upl0ad_php_sh3ll_and_rc3_1s_fun!}\n')
        return 'Flag initialized'
    return 'Flag already exists'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
