FROM python:3.10.7-slim-buster

WORKDIR /kettle

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY kettle_work.py .

CMD ["python", "kettle_work.py"]