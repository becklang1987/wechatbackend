FROM ubuntu:latest

RUN mkdir /app
COPY . /app
RUN apt-get update && apt-get install -y python3 python3-pip vim curl iputils-ping
RUN apt-get update
RUN pip3 install -r /app/requirements.txt
WORKDIR /app
EXPOSE 5020
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5020", "wsgi:app"]