"""Pydantic models for the tuning dashboard."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RobotState(str, Enum):
    IDLE = "IDLE"
    HOLD = "HOLD"
    ANGLE_TUNE = "ANGLE_TUNE"
    DIST_TUNE = "DIST_TUNE"
    RUN_WAYPOINT = "RUN_WAYPOINT"


class Telemetry(BaseModel):
    """Telemetry data from ESP32."""
    timestamp: float
    state: str
    x: float
    y: float
    th: float  # theta in radians
    aErr: float  # angle error
    dErr: float  # distance error
    aPID: float  # angle PID output
    dPID: float  # distance PID output
    aKp: float
    aKi: float
    aKd: float
    dKp: float
    dKi: float
    dKd: float
    L: int  # left encoder ticks
    R: int  # right encoder ticks


class AnglePIDParams(BaseModel):
    """Angle PID parameters with validation."""
    kp: float = Field(ge=0, le=200, description="Proportional gain")
    ki: float = Field(ge=0, le=5, description="Integral gain")
    kd: float = Field(ge=0, le=5, description="Derivative gain")


class DistancePIDParams(BaseModel):
    """Distance PID parameters with validation."""
    kp: float = Field(ge=0, le=5, description="Proportional gain")
    ki: float = Field(ge=0, le=1, description="Integral gain")
    kd: float = Field(ge=0, le=2, description="Derivative gain")


class ConnectionStatus(BaseModel):
    """ESP32 connection status."""
    connected: bool
    ip: str
    cmd_port: int = 23
    data_port: int = 24
    last_telemetry: Optional[float] = None


class ParamUpdateResponse(BaseModel):
    """Response after parameter update."""
    success: bool
    message: str
    applied_params: Optional[dict] = None


class BufferConfig(BaseModel):
    """Configuration for telemetry buffer."""
    history_seconds: int = Field(default=60, ge=10, le=300, description="History duration in seconds")
