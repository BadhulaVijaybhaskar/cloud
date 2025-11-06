FROM python:3.11-slim
WORKDIR /app
COPY src/ src/
RUN pip install --no-cache-dir flask==2.2.5 || true
ENV SERVICE_PORT=8200
ENV SIMULATION_MODE=true
EXPOSE 8200
CMD ["python","src/server.py"]