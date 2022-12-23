from multiprocessing import Event, Process
from flask import Flask,render_template,send_file,request
import socket
import ffmpeg
import os
import sys
import uuid
import shutil
import boto3
from better_ffmpeg_progress import FfmpegProcess

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
def ffmpegToHSV(input:str,uid:str,width:int,height:int):
    path1 = os.path.join(uid)
    if not os.path.isdir(path1):
        os.mkdir(path1)
    
    path2=os.path.join(path1,str(width))
    if not os.path.isdir(path2):
        os.mkdir(path2)
    
    def handle_progress_info(percentage, speed, eta, estimated_filesize):
        if not percentage == None:
            with open(os.path.join(path1,f"{width}.txt"), "w") as f:                
                f.write(str(percentage))
                f.truncate()        
            print(f"Id: {uid} Quality: {width}, Percent: {percentage}, Speed: {speed}, Eta: {eta}",flush=True)

    def handle_success():
        # Code to run if the FFmpeg process completes successfully.   
        print(f"Id: {uid}, Quality:{width} Done!")    
        pass

    def handle_error():
    # Code to run if the FFmpeg process encounters an error.
        pass
    
    #input = ffmpeg.input(input, f='mp4')
    #audio = input.audio
    #video = input.video.filter('scale', height, width)
    #output_stream = ffmpeg.output(video,audio, path2 + '/' + str(width) + '.m3u8', acodec='aac',strict='experimental',aspect='16:9', vcodec='libx264', format='hls', start_number=0, hls_time=2, hls_list_size=1000000)
    #ffmpeg.run(output_stream)
    process = FfmpegProcess(["ffmpeg", "-i", input, "-c:a", "aac", "-strict","experimental","-c:v","libx264","-s",f"{height}x{width}", "-aspect","16:9","-f","hls","-hls_list_size","1000000","-hls_time","2", path2 + '/' + str(width) + '.m3u8'])
    ffmpeg_output_path = 'ffmpeg_output.txt'
    process.run(progress_handler=handle_progress_info,ffmpeg_output_file=ffmpeg_output_path,  error_handler=handle_error)   
    upload_objects(path2,uid)
    try:
        shutil.rmtree(path2)
    except OSError as e:
        print("Error: %s : %s" % (path2, e.strerror))

@app.route('/convert_hsv')
def convert_hsv_by_url():
    try:        
       url= request.args.get("url")
       uuidFour = uuid.uuid4()     
       p1 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),240,320))
       p2 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),360,640))  
       p3 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),480,800))
       p4 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),540,960))
       p5 = Process(target=ffmpegToHSV, args=(url,str(uuidFour),720,1280))
       p1.start()
       p2.start()
       p3.start()
       p4.start()
       p5.start()
       upload_single_object('playlist.m3u8','playlist.m3u8',str(uuidFour))

       return str(uuidFour)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)


@app.route('/get_stats/<string:id>/<string:quality>')
def get_stats_by_quality(id:str,quality:str):
    with open(os.path.join(id,f"{quality}.txt"), "r") as f:                
        return f.read()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

