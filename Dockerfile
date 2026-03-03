# 使用 Ubuntu 22.04 作為基礎映像檔
FROM ubuntu:22.04

# 更新套件庫並安裝 C++ 編譯器與 Python3
RUN apt-get update && apt-get install -y \
    g++ \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 將本機的專案檔案複製到容器內
COPY . /app

# 預先編譯 C++ 程式 (稍後會建立原始碼檔案)
# RUN g++ src/monitor.cpp -o src/monitor
