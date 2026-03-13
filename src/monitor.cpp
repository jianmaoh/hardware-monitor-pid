#include <iostream>
#include <fstream>
#include <string>

using namespace std;

// read the real temp of my mac
float getRealTemperature() {
    // read the shared file
    ifstream file("/app/real_temp.txt"); 
    if (!file.is_open()) {
        return -1.0; 
    }
    float temp;
    file >> temp;
    file.close();
    return temp;
}
// read infos of mem
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
