# Usa una imagen base de Python
FROM python:3.8-slim

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos en el directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación en el directorio de trabajo
COPY . .

CMD ["python", "taximide.py"]

# Para que funcione en MacOs: 
    # 1. Averiguar dirección IPv4 (ifconfig en0)
    # 2. Instalar XQuarz y configurar: xhost 192.XXXXXX (dirección IPv4)
    # 3. Crear una imagen de nuestra app en Docker (taximetro, por ejemplo) 
    # 4. Ejecutar: docker run -it -e DISPLAY=192.XXXXX:0 --name taximetro-container taximetro (siendo "taximetro-container" el nombre del contenedor y "taximetro" el nombre de la imagen)
