FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -r requirements.txt || pip install .  # Install dependencies
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]