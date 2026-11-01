/**
 ******************************************************************************
 * @file    Nav_Standalone.h
 * @brief   Standalone navigator — no Raspberry Pi / CAN required.
 ******************************************************************************
 */

#ifndef NAV_STANDALONE_H
#define NAV_STANDALONE_H

#include <stdint.h>

/* Call this instead of Nav_vStateMachine_Routine() in the timer ISR. */
void Nav_vStandaloneStateMachine_Routine(void);

/*
 * Set either flag from a GPIO EXTI callback (or in a debugger) at any time.
 *   Nav_SA_StopRequested  = 1  →  emergency stop (mirrors CAN stop signal)
 *   Nav_SA_ResetRequested = 1  →  soft MCU reset  (mirrors CAN reset signal)
 */
extern volatile uint8_t Nav_SA_StopRequested;
extern volatile uint8_t Nav_SA_ResetRequested;

#endif /* NAV_STANDALONE_H */
