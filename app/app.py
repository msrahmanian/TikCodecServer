from multiprocessing import Event, Process
from flask import Flask,render_template,send_file,request
import socket
import ffmpeg
import os
import uuid
import shutil
import boto3

s3_resource = boto3.resource(
        's3',
        endpoint_url='https://s3.ir-thr-at1.arvanstorage.com',
        aws_access_key_id='1cc43c48-00ce-4b80-a709-dd0034d8990f',
        aws_secret_access_key='2ccdafd36f0624a03bc05a63d26641f10cd6dd236f4d5cca6f516d3eb5a88b97'
    )
def upload_single_object(file:str,outfile:str,uid:str):
    try:
        bucket_name = "mymedia" #s3 bucket name
        my_bucket = s3_resource.Bucket(bucket_name)
        my_bucket.upload_file(file, uid+'/'+outfile,ExtraArgs={'ACL':'public-read'})

    except Exception as err:
        print(err)

def upload_objects(input:str,uid:str):
    try:
        bucket_name = "mymedia" #s3 bucket name
        root_path = input # local folder for upload

        my_bucket = s3_resource.Bucket(bucket_name)

        for path, subdirs, files in os.walk(root_path):
            path = path.replace("\\","/")
            directory_name = path.replace(root_path,"")
            for file in files:
                my_bucket.upload_file(os.path.join(path, file), uid+'/'+file,ExtraArgs={'ACL':'public-read'})

    except Exception as err:
        print(err)

app = Flask(__name__)
def ffmpegToHSV(input:str,uid:str,scale:int):
        path1 = os.path.join(uid)
        if not os.path.isdir(path1):
            os.mkdir(path1)
        
        path2=os.path.join(path1,str(scale))
        if not os.path.isdir(path2):
            os.mkdir(path2)
        input = ffmpeg.input(input, f='mp4')
        audio = input.audio
        video = input.video.filter('scale', -1, scale)
        output_stream = ffmpeg.output(video,audio, path2 + '/' + str(scale) + '.m3u8', format='hls', start_number=0, hls_time=2, hls_list_size=1000000)
        ffmpeg.run(output_stream)
        upload_objects(path2,uid)
        try:
            shutil.rmtree(path2)
        except OSError as e:
            print("Error: %s : %s" % (path2, e.strerror))

@app.route('/convert_hsv', methods=['POST'])
def convert_hsv_by_url():
    try:        
       url= request.form.get("url")
       uuidFour = uuid.uuid4()     
       p1 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),240))
       p2 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),360))  
       p3 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),480))
       
       p1.start()
       p2.start()
       p3.start()
       
       upload_single_object('playlist.m3u8','playlist.m3u8',str(uuidFour))

       return str(uuidFour)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)




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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

