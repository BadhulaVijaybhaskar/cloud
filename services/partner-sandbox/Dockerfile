FROM python:3.11-slim
WORKDIR /app
COPY src/ src/
ENV SERVICE_PORT=8220
ENV SIMULATION_MODE=true
EXPOSE 8220
CMD ["python","src/mock_runtime.py"]