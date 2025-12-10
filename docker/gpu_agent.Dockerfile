FROM python:3.10-slim
WORKDIR /app
COPY agent /app/agent
RUN pip install --no-cache-dir requests
CMD ["python","/app/agent/daemon/agent.py"]
