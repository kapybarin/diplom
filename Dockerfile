FROM python:3.8.2

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY . ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ./test.sh