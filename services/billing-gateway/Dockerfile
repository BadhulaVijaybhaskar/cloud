FROM python:3.10-slim
WORKDIR /app
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY src /app
ENV FLASK_APP=main.py
CMD ["python", "main.py"]