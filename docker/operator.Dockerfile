FROM python:3.10-slim
WORKDIR /app
COPY operator /app/operator
CMD ["python","-c","print('operator placeholder')"]
