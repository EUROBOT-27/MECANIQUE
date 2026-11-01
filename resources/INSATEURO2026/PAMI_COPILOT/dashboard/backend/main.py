"""FastAPI backend for the tuning dashboard."""
import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Set, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from models import (
    AnglePIDParams,
    DistancePIDParams,
    ConnectionStatus,
    ParamUpdateResponse,
    BufferConfig,
)
from esp32_client import ESP32Client, ESP32Config
from data_buffer import TelemetryBuffer


# Global state
esp32_client: Optional[ESP32Client] = None
telemetry_buffer: TelemetryBuffer = TelemetryBuffer(history_seconds=60, sample_rate_hz=10)
websocket_clients: Set[WebSocket] = set()
esp32_task: Optional[asyncio.Task] = None


async def broadcast_telemetry(data: dict):
    """Broadcast telemetry to all connected WebSocket clients."""
    if not websocket_clients:
        return
    
    message = json.dumps({"type": "telemetry", "data": data})
    disconnected = set()
    
    for ws in websocket_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    
    # Clean up disconnected clients
    websocket_clients.difference_update(disconnected)


def on_telemetry(data: dict):
    """Callback when telemetry is received from ESP32."""
    telemetry_buffer.add(data)
    # Schedule broadcast on the event loop
    asyncio.create_task(broadcast_telemetry(data))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global esp32_client, esp32_task
    
    # Startup
    config = ESP32Config()
    esp32_client = ESP32Client(config, on_telemetry)
    esp32_task = asyncio.create_task(esp32_client.run())
    print("[Server] Starting ESP32 client...")
    
    yield
    
    # Shutdown
    print("[Server] Shutting down...")
    if esp32_client:
        await esp32_client.stop()
    if esp32_task:
        esp32_task.cancel()
        try:
            await esp32_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Tuning Dashboard API",
    description="Real-time PID tuning visualization and control",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== WebSocket Endpoint ==============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time telemetry streaming."""
    await websocket.accept()
    websocket_clients.add(websocket)
    print(f"[WS] Client connected. Total: {len(websocket_clients)}")
    
    try:
        # Send current connection status
        status = get_connection_status()
        await websocket.send_text(json.dumps({"type": "status", "data": status.model_dump()}))
        
        # Send buffered history
        history = telemetry_buffer.get_all()
        if history:
            await websocket.send_text(json.dumps({"type": "history", "data": history}))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Handle client messages (e.g., commands)
                data = json.loads(message)
                await handle_ws_message(websocket, data)
            except asyncio.TimeoutError:
                # Send ping to keep alive
                await websocket.send_text(json.dumps({"type": "ping"}))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        websocket_clients.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(websocket_clients)}")


async def handle_ws_message(websocket: WebSocket, data: dict):
    """Handle incoming WebSocket messages from clients."""
    msg_type = data.get("type")
    
    if msg_type == "pong":
        pass  # Keepalive response
    elif msg_type == "get_buffer":
        # Client requests buffer data
        from_ts = data.get("from", 0)
        to_ts = data.get("to", time.time())
        buffer_data = telemetry_buffer.get_range(from_ts, to_ts)
        await websocket.send_text(json.dumps({"type": "buffer", "data": buffer_data}))


# ============== REST Endpoints ==============

def get_connection_status() -> ConnectionStatus:
    """Get current ESP32 connection status."""
    if esp32_client:
        return ConnectionStatus(
            connected=esp32_client.connected,
            ip=esp32_client.config.ip,
            cmd_port=esp32_client.config.cmd_port,
            data_port=esp32_client.config.data_port,
            last_telemetry=esp32_client.last_telemetry_time,
        )
    return ConnectionStatus(connected=False, ip="")


@app.get("/api/status", response_model=ConnectionStatus)
async def api_status():
    """Get ESP32 connection status."""
    return get_connection_status()


@app.get("/api/params")
async def api_get_params():
    """Get current PID parameters from latest telemetry."""
    latest = telemetry_buffer.get_latest()
    if not latest:
        raise HTTPException(status_code=503, detail="No telemetry data available")
    
    return {
        "angle": {"kp": latest["aKp"], "ki": latest["aKi"], "kd": latest["aKd"]},
        "distance": {"kp": latest["dKp"], "ki": latest["dKi"], "kd": latest["dKd"]},
        "timestamp": latest["timestamp"],
    }


@app.post("/api/params/angle", response_model=ParamUpdateResponse)
async def api_set_angle_pid(params: AnglePIDParams):
    """Set angle PID parameters."""
    if not esp32_client or not esp32_client.connected:
        raise HTTPException(status_code=503, detail="ESP32 not connected")
    
    success = await esp32_client.set_angle_pid(params.kp, params.ki, params.kd)
    
    if success:
        # Broadcast param change to all clients
        await broadcast_param_change("angle", params.model_dump())
        return ParamUpdateResponse(
            success=True,
            message=f"Angle PID set to Kp={params.kp}, Ki={params.ki}, Kd={params.kd}",
            applied_params=params.model_dump(),
        )
    else:
        return ParamUpdateResponse(
            success=False,
            message="Failed to send command to ESP32",
            applied_params=None,
        )


@app.post("/api/params/distance", response_model=ParamUpdateResponse)
async def api_set_distance_pid(params: DistancePIDParams):
    """Set distance PID parameters."""
    if not esp32_client or not esp32_client.connected:
        raise HTTPException(status_code=503, detail="ESP32 not connected")
    
    success = await esp32_client.set_distance_pid(params.kp, params.ki, params.kd)
    
    if success:
        # Broadcast param change to all clients
        await broadcast_param_change("distance", params.model_dump())
        return ParamUpdateResponse(
            success=True,
            message=f"Distance PID set to Kp={params.kp}, Ki={params.ki}, Kd={params.kd}",
            applied_params=params.model_dump(),
        )
    else:
        return ParamUpdateResponse(
            success=False,
            message="Failed to send command to ESP32",
            applied_params=None,
        )


async def broadcast_param_change(pid_type: str, params: dict):
    """Broadcast parameter change to all WebSocket clients."""
    message = json.dumps({"type": "param_change", "pid": pid_type, "params": params})
    disconnected = set()
    
    for ws in websocket_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    
    websocket_clients.difference_update(disconnected)


@app.get("/api/buffer")
async def api_get_buffer(
    from_ts: float = Query(default=0, description="Start timestamp"),
    to_ts: float = Query(default=None, description="End timestamp"),
    last_seconds: float = Query(default=None, description="Get last N seconds"),
):
    """Get buffered telemetry data."""
    if last_seconds is not None:
        return {"data": telemetry_buffer.get_last_n_seconds(last_seconds)}
    
    if to_ts is None:
        to_ts = time.time()
    
    return {"data": telemetry_buffer.get_range(from_ts, to_ts)}


@app.get("/api/buffer/config", response_model=BufferConfig)
async def api_get_buffer_config():
    """Get current buffer configuration."""
    return BufferConfig(history_seconds=telemetry_buffer.history_seconds)


@app.post("/api/buffer/config", response_model=BufferConfig)
async def api_set_buffer_config(config: BufferConfig):
    """Set buffer configuration (history duration)."""
    telemetry_buffer.history_seconds = config.history_seconds
    return BufferConfig(history_seconds=telemetry_buffer.history_seconds)


@app.post("/api/command/{cmd}")
async def api_send_command(cmd: str, value: float = Query(default=None)):
    """Send a command to ESP32 (S, H, A, D, R)."""
    if not esp32_client or not esp32_client.connected:
        raise HTTPException(status_code=503, detail="ESP32 not connected")
    
    valid_commands = {"S", "H", "A", "D", "R"}
    cmd = cmd.upper()
    
    if cmd not in valid_commands:
        raise HTTPException(status_code=400, detail=f"Invalid command. Valid: {valid_commands}")
    
    if value is not None and cmd in {"A", "D"}:
        command = f"{cmd} {value}"
    else:
        command = cmd
    
    success = await esp32_client.send_command(command)
    return {"success": success, "command": command}


# ============== Health Check ==============

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
