FROM tiangolo/uvicorn-gunicorn-fastapi:latest

COPY ./app /app
COPY .env /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ls
RUN pwd