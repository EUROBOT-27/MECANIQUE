# D-MAX — remote-controlled robot

Arduino sketch for **D-MAX**, a remote-controlled (*télé-guidé*) differential-drive robot built by AEROBOTIX INSAT. An ESP32 receives a **PlayStation controller** over Bluetooth with [Bluepad32](https://github.com/ricardoquesada/bluepad32), drives two DC motors, and plays sounds on a buzzer.

## Controls

| Input | Action |
|---|---|
| Left stick | Drive: up/down = forward/backward, left/right = turn (arcade mix) |
| *(default)* | Top speed 25 % |
| L1 | Top speed 35 % |
| R1 | Top speed 50 % |
| L2 | Top speed 75 % |
| R2 | Top speed 100 % |
| ○ Circle | Victory fanfare |
| ✕ Cross | Mario coin |
| △ Triangle | Sad trombone |
| □ Square | Megalovania |

The stick has a dead zone of ±30. The robot stops when the controller disconnects.

## Wiring

| Signal | ESP32 pin |
|---|---|
| Left motor `LPWM` / `RPWM` | 26 / 27 |
| Right motor `LPWM` / `RPWM` | 32 / 33 |
| Driver enable | 25 |
| Buzzer | 15 |

The `LPWM` / `RPWM` / `EN` naming matches BTS7960-style H-bridge drivers.

## Flash it

1. In the Arduino IDE, open **File → Preferences** and add these two lines to *Additional boards manager URLs*:

   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   https://raw.githubusercontent.com/ricardoquesada/esp32-arduino-lib-builder/master/bluepad32_files/package_esp32_bluepad32_index.json
   ```

2. In **Tools → Board → Boards Manager**, install **esp32** and **esp32_bluepad32** (by Ricardo Quesada).
3. Select the Bluepad32 version of your board (usually *ESP32 Dev Module* or *DOIT ESP32 DEVKIT V1*).
4. Open `dmax/dmax.ino` and upload.

## Pair the controller

The sketch forgets old pairings at every boot. After power-up, put the controller in pairing mode (**SHARE + PS** on a DualShock 4 / DualSense) until it connects. The serial monitor (115200 baud) shows the connection.
