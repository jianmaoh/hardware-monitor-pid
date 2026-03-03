#include <iostream>
#include <fstream>
#include <string>

using namespace std;

// 讀取 Mac 傳遞過來的真實溫度
float getRealTemperature() {
    // 讀取掛載進來的共享檔案
    ifstream file("/app/real_temp.txt"); 
    if (!file.is_open()) {
        return -1.0; 
    }
    float temp;
    file >> temp;
    file.close();
    return temp;
}
// 讀取系統記憶體資訊
void printMemoryInfo() {
    ifstream file("/proc/meminfo");
    string line;
    if (file.is_open()) {
        while (getline(file, line)) {
            if (line.find("MemTotal") != string::npos || line.find("MemFree") != string::npos) {
                cout << line << endl;
            }
        }
        file.close();
    }
}

int main() {
    cout << "CPU_TEMP_C:" << getRealTemperature() << endl;
    printMemoryInfo();
    return 0;
}
