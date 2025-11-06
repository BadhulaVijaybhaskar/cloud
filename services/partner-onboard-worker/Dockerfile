FROM python:3.11-slim
WORKDIR /app
COPY src/ src/
ENV SIMULATION_MODE=true
CMD ["python","src/worker.py"]