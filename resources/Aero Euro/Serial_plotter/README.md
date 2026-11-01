# Serial_plotter — live plots of microcontroller data

A small Python tool that plots up to **four signals in real time** from a microcontroller over serial. AEROBOTIX INSAT uses it to tune PID loops (wheel speeds, arm positions) on the ESP32 and STM32 boards: the firmware streams values, and you watch the response while changing gains.

## Run

```bash
pip install pyserial pyqtgraph PyQt5 numpy
python "Serial Plotter.py"
```

Set your serial port and baud rate at the top of the script first:

```python
ser = serial.Serial('COM3', 115200, timeout=0.01)   # e.g. '/dev/ttyUSB0' on Linux
```

The window shows the last 1000 samples of each signal, refreshed 50 times per second, with a fixed Y range of ±1000. Change `plot.setYRange(...)` to suit your data.

## Packet format

Each sample is **5 bytes**: a 1-byte header that identifies the signal, followed by a little-endian 32-bit float.

| Header | Signal | Colour |
|---|---|---|
| `0xAA` | value 1 | white |
| `0xAB` | value 2 | green |
| `0xAC` | value 3 | red |
| `0xAD` | value 4 | yellow |

Bytes that are not a known header are skipped, so text printed on the same port does not break the stream.

## Sending data from Arduino / ESP32

```cpp
void plot(uint8_t header, float value) {
  Serial.write(header);
  Serial.write((uint8_t *)&value, sizeof(value));   // ESP32 and STM32 are little-endian
}

void loop() {
  plot(0xAA, target_speed);
  plot(0xAB, measured_speed);
  plot(0xAC, pwm_output);
  delay(10);
}
```

## Repository contents

| Path | Content |
|---|---|
| `Serial Plotter.py` | The plotter |
| `Line_Follower_app_esp32/`, `PAMI/`, `Systems_tests/` | Links to test firmware repositories. They are recorded as Git submodules without a `.gitmodules` file, so they are empty when you clone. |
| `spark_max_test.code-workspace`, `kabbecha_test.lnk` | Local editor shortcuts |

A variant of this plotter that receives data over Wi-Fi (WebSocket) instead of serial is in [PAMI_ESP32_code/server](https://github.com/Eurobot-2026-Aerobotix/PAMI_ESP32_code/tree/main/server).
