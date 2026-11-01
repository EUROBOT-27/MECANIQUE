# 2. STM32 Peripheral Configuration (.ioc)

## 2.1 Peripheral Overview

| Peripheral | Role |
|---|---|
| `CAN1` | Bus link to the Raspberry Pi — receives target poses and stop/reset/ack signals, sends back pose telemetry and navigation status. |
| `TIM1` | Generates the 4 PWM channels driving the BTS7960 half-bridge modules (left/right motor, forward/reverse per side). |
| `TIM2` | Quadrature encoder input for one wheel. |
| `TIM5` | Quadrature encoder input for the other wheel. |
| `TIM6` | Fires the 5 ms global control-loop interrupt that ticks the whole navigation state machine. |


## 2.2 TIM1 — Motor PWM Frequency

The motors are driven through **BTS7960 half-bridge modules**, so the PWM frequency had to sit in the range those drivers handle cleanly (according to their datasheet)— high enough to avoid audible switching noise and keep current ripple low, but not so high that switching losses in the BTS7960's internal MOSFETs become a problem. That put the target in the **~15–20 kHz** range.

TIM1 sits on **APB2**. With the clock tree in `SystemClock_Config()` (HSI → PLL, PLLM=8, PLLN=168, PLLP=2 → 168 MHz SYSCLK/HCLK, APB2 prescaler DIV2), the APB2 peripheral clock is 84 MHz — but because the APB prescaler is not 1, the **timer** clock feeding TIM1 is automatically doubled by hardware to **168 MHz**.

With `Prescaler = 2` and `Period (ARR) = 3199`:

```
timer_tick_freq = 168 MHz / (2 + 1)        = 56 MHz
PWM_freq        = 56 MHz / (3199 + 1)      = 17.5 kHz
```

17.5 kHz lands comfortably inside the target band for the BTS7960 — enough headroom below its switching limit, and high enough to stay out of the most audible part of the range. 
## 2.3 TIM6 — 5 ms Global Control-Loop Interrupt

The whole navigation state machine is ticked from a single periodic interrupt. **5 ms** was chosen as the tick period, and TIM6 was configured to hit that exactly.

TIM6 sits on **APB1**. APB1 is configured with a DIV4 prescaler, giving a 42 MHz peripheral clock — but again, since the prescaler isn't 1, the timer clock is doubled by hardware, so TIM6 is actually clocked at **84 MHz**.

With `Prescaler = 999` and `Period (ARR) = 419`:

```
timer_tick_freq = 84 MHz / (999 + 1)       = 84 kHz
interrupt_period = (419 + 1) / 84 kHz      = 5.000 ms  →  200 Hz
```

HAL_TIM_Base_Start_IT(&htim6) arms the timer in main(). **Every 5 ms it fires HAL_TIM_PeriodElapsedCallback()**, which is where the whole navigation loop hangs off: the state machine tick and the CAN telemetry(can sends every 100ms) send both happen from inside that callback.


