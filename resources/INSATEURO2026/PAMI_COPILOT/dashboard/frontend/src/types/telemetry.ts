/** Telemetry data from ESP32 */
export interface Telemetry {
  timestamp: number;
  state: string;
  x: number;
  y: number;
  th: number;
  aErr: number;
  dErr: number;
  aPID: number;
  dPID: number;
  aKp: number;
  aKi: number;
  aKd: number;
  dKp: number;
  dKi: number;
  dKd: number;
  L: number;
  R: number;
}

/** PID parameters for angle control */
export interface AnglePIDParams {
  kp: number;
  ki: number;
  kd: number;
}

/** PID parameters for distance control */
export interface DistancePIDParams {
  kp: number;
  ki: number;
  kd: number;
}

/** Connection status */
export interface ConnectionStatus {
  connected: boolean;
  ip: string;
  cmd_port: number;
  data_port: number;
  last_telemetry: number | null;
}

/** WebSocket message types */
export type WSMessage =
  | { type: 'telemetry'; data: Telemetry }
  | { type: 'history'; data: Telemetry[] }
  | { type: 'status'; data: ConnectionStatus }
  | { type: 'param_change'; pid: 'angle' | 'distance'; params: AnglePIDParams | DistancePIDParams }
  | { type: 'ping' }
  | { type: 'buffer'; data: Telemetry[] };

/** Parameter bounds */
export const PARAM_BOUNDS = {
  angle: {
    kp: { min: 0, max: 200 },
    ki: { min: 0, max: 5 },
    kd: { min: 0, max: 5 },
  },
  distance: {
    kp: { min: 0, max: 5 },
    ki: { min: 0, max: 1 },
    kd: { min: 0, max: 2 },
  },
} as const;
