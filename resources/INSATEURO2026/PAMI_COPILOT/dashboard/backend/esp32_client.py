"""Async TCP client for ESP32 telnet communication."""
import asyncio
import json
import time
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class ESP32Config:
    """ESP32 connection configuration."""
    ip: str = "192.168.1.127"
    cmd_port: int = 23
    data_port: int = 24
    reconnect_delay: float = 2.0
    max_reconnect_delay: float = 30.0


class ESP32Client:
    """Async TCP client for ESP32 telnet ports."""
    
    def __init__(self, config: ESP32Config, on_telemetry: Callable[[dict], None]):
        self.config = config
        self.on_telemetry = on_telemetry
        self._cmd_reader: Optional[asyncio.StreamReader] = None
        self._cmd_writer: Optional[asyncio.StreamWriter] = None
        self._data_reader: Optional[asyncio.StreamReader] = None
        self._data_writer: Optional[asyncio.StreamWriter] = None
        self._running = False
        self._connected = False
        self._reconnect_delay = config.reconnect_delay
        self._last_telemetry_time: Optional[float] = None
        
    @property
    def connected(self) -> bool:
        return self._connected
    
    @property
    def last_telemetry_time(self) -> Optional[float]:
        return self._last_telemetry_time
    
    async def connect(self) -> bool:
        """Connect to both ESP32 ports."""
        try:
            # Connect to command port (23)
            self._cmd_reader, self._cmd_writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.ip, self.config.cmd_port),
                timeout=5.0
            )
            print(f"[ESP32] Connected to command port {self.config.cmd_port}")
            
            # Connect to data port (24)
            self._data_reader, self._data_writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.ip, self.config.data_port),
                timeout=5.0
            )
            print(f"[ESP32] Connected to data port {self.config.data_port}")
            
            self._connected = True
            self._reconnect_delay = self.config.reconnect_delay
            return True
            
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            print(f"[ESP32] Connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close all connections."""
        self._running = False
        self._connected = False
        
        for writer in [self._cmd_writer, self._data_writer]:
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass
        
        self._cmd_reader = self._cmd_writer = None
        self._data_reader = self._data_writer = None
        print("[ESP32] Disconnected")
    
    async def send_command(self, command: str) -> bool:
        """Send command to ESP32 via port 23."""
        if not self._connected or not self._cmd_writer:
            print(f"[ESP32] Cannot send command, not connected")
            return False
        
        try:
            cmd = command.strip() + "\n"
            self._cmd_writer.write(cmd.encode())
            await self._cmd_writer.drain()
            print(f"[ESP32] Sent: {command}")
            return True
        except Exception as e:
            print(f"[ESP32] Send error: {e}")
            self._connected = False
            return False
    
    async def set_angle_pid(self, kp: float, ki: float, kd: float) -> bool:
        """Set angle PID parameters."""
        return await self.send_command(f"KA {kp} {ki} {kd}")
    
    async def set_distance_pid(self, kp: float, ki: float, kd: float) -> bool:
        """Set distance PID parameters."""
        return await self.send_command(f"KD {kp} {ki} {kd}")
    
    async def _read_telemetry_loop(self):
        """Read telemetry data from port 24."""
        buffer = ""
        
        while self._running and self._data_reader:
            try:
                data = await asyncio.wait_for(
                    self._data_reader.read(1024),
                    timeout=2.0
                )
                
                if not data:
                    print("[ESP32] Data connection closed")
                    break
                
                buffer += data.decode('utf-8', errors='ignore')
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            telemetry = json.loads(line)
                            telemetry['timestamp'] = time.time()
                            self._last_telemetry_time = telemetry['timestamp']
                            self.on_telemetry(telemetry)
                        except json.JSONDecodeError:
                            pass  # Skip malformed JSON
                            
            except asyncio.TimeoutError:
                continue  # No data, keep waiting
            except Exception as e:
                print(f"[ESP32] Telemetry read error: {e}")
                break
        
        self._connected = False
    
    async def run(self):
        """Main loop with auto-reconnect."""
        self._running = True
        
        while self._running:
            if not self._connected:
                print(f"[ESP32] Connecting to {self.config.ip}...")
                
                if await self.connect():
                    # Start telemetry reader
                    await self._read_telemetry_loop()
                else:
                    # Exponential backoff
                    print(f"[ESP32] Retry in {self._reconnect_delay}s...")
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 1.5,
                        self.config.max_reconnect_delay
                    )
            else:
                await asyncio.sleep(0.1)
    
    async def stop(self):
        """Stop the client."""
        self._running = False
        await self.disconnect()
