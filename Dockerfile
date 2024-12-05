# # Exemplo de Dockerfile
# FROM python:3.10

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["python", "app.py"]


# Use a imagem base do Python 3.10 slim para evitar problemas de compatibilidade no Azure
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o container
COPY requirements.txt .

# Instala as dependências sem armazenar cache para reduzir o tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da aplicação para o diretório de trabalho no container
COPY . .

# Exponha a porta padrão usada pelo Gunicorn
EXPOSE 5000

# Comando para iniciar o Gunicorn com 4 workers e usando app como entrada
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
