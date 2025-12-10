FROM python:3.10-slim
WORKDIR /app
COPY telemetry.py /app/telemetry.py
RUN pip install --no-cache-dir requests
CMD ["python","/app/telemetry.py"]
