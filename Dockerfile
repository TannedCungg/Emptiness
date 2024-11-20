FROM python:3.8.18-slim

COPY ./requirements.txt /
RUN pip install -r /requirements.txt
RUN apt update && apt-get -y install libglib2.0-0 libsdl1.2-dev libsdl-image1.2 libsdl-mixer1.2 libsdl-ttf2.0 pulseaudio

COPY . /workspace

CMD [ "python", "/workspace/Playing_service.py" ]