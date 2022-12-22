FROM python:3.6
LABEL maintainer="rahmanian@gmail.com"

RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app/app.py"]
