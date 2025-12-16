# Kullanılacak temel imaj
FROM python:3.9-slim

# Çalışma dizinini belirle
WORKDIR /app

# Gereksinimlerinizi kopyalayın
COPY requirements.txt .

# Gerekli Python paketlerini yükleyin
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyasını kopyalayın
COPY . .

# Uygulamayı çalıştırmak için komut
CMD ["python", "-c", "import time; print('Container ready'); time.sleep(10**9)"]

