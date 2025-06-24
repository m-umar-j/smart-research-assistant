FROM python:3.12

WORKDIR /app


COPY backend /app/backend
COPY frontend /app/frontend


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 7860

CMD ["/app/start.sh"]
