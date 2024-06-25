FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir /app
COPY . /app
RUN pip3 install -r /app/requirements.txt
WORKDIR /app
EXPOSE 5020
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5020", "wsgi:app"]