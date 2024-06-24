FROM ubuntu:latest

RUN mkdir /app
COPY . /app
RUN apt-get update && apt-get install -y python3 python3-pip vim curl iputils-ping
RUN apt-get update
RUN apt install -y python3-flask python3-requests python3-random python3-json python3-msal python3-gunicorn
RUN apt install -y python3-string
WORKDIR /app
EXPOSE 5020
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5020", "wsgi:app"]