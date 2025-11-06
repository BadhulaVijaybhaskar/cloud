FROM python:3.11-slim
WORKDIR /app
COPY src/ src/
RUN pip install --no-cache-dir
ENV SERVICE_PORT=8210
ENV SIMULATION_MODE=true
EXPOSE 8210
CMD ["python","src/main.py"]