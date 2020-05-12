FROM python:3.8.2

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY . ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x /start_app.sh
RUN chmod +x /prestart.sh
RUN /prestart.sh
CMD ["/start_app.sh"]