# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos y la aplicación
#COPY requirements.txt requirements.txt
COPY app/requirements.txt requirements.txt
RUN apt-get update && apt-get install -y curl
#COPY app.py app.py
COPY app/app.py app.py

#COPY ./static /app/static
COPY app/static /app/static
#COPY ./templates /app/templates
COPY app/templates /app/templates

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
