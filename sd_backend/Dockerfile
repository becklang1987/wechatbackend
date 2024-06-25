FROM arm64v8/ubuntu:latest

RUN mkdir /app
COPY . /app
RUN apt-get update && apt-get install -y python3 python3-pip vim curl iputils-ping  python-dev
RUN apt-get update
RUN apt install -y python3-flask python3-requests  python3-msal python3-gunicorn
WORKDIR /app
EXPOSE 5020
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5020", "wsgi:app"]