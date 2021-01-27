FROM python:3.7-slim

ADD requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8774
CMD gunicorn --bind 0.0.0.0:8774 data.ext.ext:app
