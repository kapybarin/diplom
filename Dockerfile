FROM python:3.8.3

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY . ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x /start_app.sh
CMD ["/start_app.sh"]