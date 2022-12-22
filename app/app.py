from flask import Flask,render_template,send_file
import socket
import ffmpeg

app = Flask(__name__)

@app.route('/get_thumb')
def get_image():
    try:
        (
            ffmpeg
            .input('https://s3.tikschool.ir/sample.mp4', ss=0.5)
            .filter('scale', 1200, -1)
            .output('out.jpg', vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
            
        )
        return send_file('../out.jpg', mimetype='image/jpg')
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
    
    return send_file(filename, mimetype='image/gif')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
