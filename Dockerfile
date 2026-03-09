FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto (static, templates, instance, app.py, etc.)
COPY . .

# Exponemos el puerto 5000 para los 24 usuarios
EXPOSE 5000

# Ejecutamos la aplicación
CMD ["python", "run.py"]
