from better_ffmpeg_progress import FfmpegProcess
input= 'https://cdn2.pors.app/S-F3-10om-Test-267.mp4'
width=240
height=320
process = FfmpegProcess(["ffmpeg", "-i", input, "-c:a", "aac", "-strict","experimental","-c:v","libx264","-s",f"{width}x{height}", "-aspect","16:9","-f","hls","-hls_list_size","1000000","-hls_time","2", f"{width}.m3u8"])
process.run()

