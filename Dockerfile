# 使用 Ubuntu 22.04 作為基礎映像檔
FROM ubuntu:22.04

# 更新套件庫並安裝 C++ 編譯器、Python3 與 pip
RUN apt-get update && apt-get install -y \
    g++ \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Gemini API 套件
RUN pip3 install google-generativeai

# 設定工作目錄
WORKDIR /app

# 將本機的專案檔案複製到容器內
COPY . /app
