#!/bin/bash
# 儲存路徑設定為我們與 Docker 共享的資料夾
OUTPUT_FILE="$(pwd)/real_temp.txt"

echo "開始攔截 Mac 真實溫度並轉發至 Docker... (按 Ctrl+C 停止)"

while true; do
    # 抓取溫度，並用 awk 過濾掉 "°C" 符號，只保留數字
    TEMP=$(osx-cpu-temp | awk -F '°' '{print $1}')
    
    # 將數字寫入檔案
    echo $TEMP > "$OUTPUT_FILE"
    
    sleep 2
done
