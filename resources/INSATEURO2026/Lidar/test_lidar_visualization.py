#!/usr/bin/env python3
"""
YDLidar X2 Visualization Test Script

This script provides real-time visualization of YDLidar X2 data.
It displays the LiDAR scan data in a polar plot, showing detected obstacles
and their distances from the sensor.

Author: INSA Eurobot 2026 Team
License: See LICENSE file
"""

import argparse
import sys
import time
import platform
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from collections import deque
import threading
import queue

try:
    import serial
except ImportError:
    serial = None

# Try to import official YDLIDAR python wrapper (preferred for real hardware)
try:
    import ydlidar
    _HAS_YDLIDAR = True
except Exception:
    ydlidar = None
    _HAS_YDLIDAR = False


class YDLidarX2Simulator:
    """Simulator for testing when hardware is not connected."""
    
    def __init__(self):
        self.running = False
        self.angle = 0
        
    def connect(self):
        print("📡 Simulator Mode: No hardware detected")
        return True
    
    def disconnect(self):
        pass
    
    def start_scan(self):
        self.running = True
        
    def stop_scan(self):
        self.running = False
    
    def get_scan(self):
        """Generate simulated scan data."""
        if not self.running:
            return []
        
        # Simulate a scan with some obstacles
        scan_data = []
        num_points = 360
        
        for i in range(num_points):
            angle = i
            
            # Simulate some obstacles at different positions
            base_distance = 3000  # 3 meters default
            
            # Create a rectangular room with some obstacles
            if 45 <= angle <= 135:  # Front-right quadrant
                distance = 2000 + np.random.normal(0, 50)
            elif 135 <= angle <= 225:  # Back quadrants
                distance = 4000 + np.random.normal(0, 50)
            elif 225 <= angle <= 315:  # Front-left quadrant
                distance = 2500 + np.random.normal(0, 50)
            else:  # Front
                distance = 1500 + np.random.normal(0, 50)
            
            # Add some random obstacles (simulate other robots or objects)
            if 80 <= angle <= 100:
                distance = min(distance, 800 + np.random.normal(0, 30))
            if 260 <= angle <= 280:
                distance = min(distance, 1200 + np.random.normal(0, 30))
            
            # Add noise
            distance = max(120, min(10000, distance))  # Clamp to valid range
            quality = np.random.randint(10, 15)
            
            scan_data.append((angle, distance, quality))
        
        time.sleep(0.1)  # Simulate 10Hz scan rate
        return scan_data


class YDLidarX2:
    """Driver for YDLidar X2 hardware.

    Uses the official `ydlidar` python wrapper if available for reliable
    scanning on all platforms. Falls back to a basic serial stub otherwise.
    """

    def __init__(self, port='COM9', baudrate=115200, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.running = False
        self.scan_thread = None
        self.scan_queue = queue.Queue(maxsize=10)

        # SDK objects
        self._use_sdk = _HAS_YDLIDAR
        self._laser = None

        # Serial fallback
        self.serial_conn = None

    def connect(self):
        """Connect to the LiDAR device."""
        if self._use_sdk and ydlidar is not None:
            try:
                # Initialize OS-specific hooks
                ydlidar.os_init()

                self._laser = ydlidar.CYdLidar()
                # Configure device options
                self._laser.setlidaropt(ydlidar.LidarPropSerialPort, self.port, len(self.port))
                self._laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, self.baudrate, 4)
                # YDLIDAR X2 is a triangle measurement type and serial device
                self._laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE, 4)
                self._laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL, 4)
                # Reasonable defaults; the SDK will clamp to supported values
                self._laser.setlidaropt(ydlidar.LidarPropScanFrequency, 7.0, 8)
                self._laser.setlidaropt(ydlidar.LidarPropSampleRate, 3, 4)
                self._laser.setlidaropt(ydlidar.LidarPropSingleChannel, True, 4)
                self._laser.setlidaropt(ydlidar.LidarPropIntensities, False, 4)

                if not self._laser.initialize():
                    print("✗ Failed to initialize YDLidar via SDK — check port/permissions")
                    return False
                if not self._laser.turnOn():
                    print("✗ Failed to start motor/scan via SDK")
                    return False

                print(f"✓ Connected to YDLidar X2 (SDK) on {self.port}")
                # Start background reading thread
                self.running = True
                self.scan_thread = threading.Thread(target=self._read_scans_sdk, daemon=True)
                self.scan_thread.start()
                return True
            except Exception as e:
                print(f"✗ SDK connection error: {e}")
                # If SDK fails, try serial fallback if available
                self._use_sdk = False

        # Fallback: basic serial open (no real parsing implemented)
        if serial is None:
            print("✗ pyserial not installed and SDK unavailable. Run: pip install -r requirements.txt")
            return False
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print(f"✓ Connected to YDLidar X2 on {self.port} (RAW serial)")
            return True
        except Exception as e:
            print(f"✗ Failed to open serial port {self.port}: {e}")
            return False

    def disconnect(self):
        """Disconnect from the LiDAR device."""
        try:
            self.stop_scan()
        except Exception:
            pass

        if self._use_sdk and self._laser is not None:
            try:
                self._laser.turnOff()
                self._laser.disconnect()
            except Exception:
                pass
            print("✓ Disconnected from YDLidar X2 (SDK)")
            self._laser = None

        if self.serial_conn and getattr(self.serial_conn, "is_open", False):
            try:
                self.serial_conn.close()
            except Exception:
                pass
            print("✓ Disconnected from YDLidar X2 (RAW serial)")

    def start_scan(self):
        """Start the LiDAR scanning."""
        if self._use_sdk and self._laser is not None:
            # Already turned on and thread started in connect(); nothing else to do
            print("✓ Started scanning (SDK)")
            return

        if not self.serial_conn or not getattr(self.serial_conn, "is_open", False):
            print("✗ Not connected to LiDAR")
            return

        self.running = True
        # Send start scan command (protocol-specific; may vary by model)
        try:
            self.serial_conn.write(bytes([0xA5, 0x60]))
        except Exception:
            pass

        # Start reading thread (will warn that parser is not implemented)
        self.scan_thread = threading.Thread(target=self._read_scans_serial_stub, daemon=True)
        self.scan_thread.start()
        print("✓ Started scanning (RAW serial)")

    def stop_scan(self):
        """Stop the LiDAR scanning."""
        self.running = False
        if self.scan_thread:
            try:
                self.scan_thread.join(timeout=2.0)
            except Exception:
                pass
            self.scan_thread = None

        if self._use_sdk and self._laser is not None:
            try:
                self._laser.turnOff()
            except Exception:
                pass
            print("✓ Stopped scanning (SDK)")
            return

        if self.serial_conn and getattr(self.serial_conn, "is_open", False):
            try:
                # Send stop scan command
                self.serial_conn.write(bytes([0xA5, 0x65]))
            except Exception:
                pass
            print("✓ Stopped scanning (RAW serial)")

    # --- SDK-based reading ---
    def _read_scans_sdk(self):
        """Background thread to read scan data using YDLIDAR SDK."""
        while self.running and self._laser is not None:
            try:
                scan = ydlidar.LaserScan()
                if self._laser.doProcessSimple(scan):
                    # Convert to (angle_deg, distance_mm, quality)
                    count = len(scan.ranges)
                    if count == 0:
                        continue
                    angle = scan.angle_min
                    data = []
                    for i in range(count):
                        r_m = scan.ranges[i]
                        if r_m <= 0.0 or np.isinf(r_m) or np.isnan(r_m):
                            angle += scan.angle_increment
                            continue
                        angle_deg = np.degrees(angle)
                        # Normalize to 0-360
                        angle_deg = (angle_deg + 360.0) % 360.0
                        distance_mm = int(r_m * 1000.0)
                        # Not all models provide intensity via simple API; set nominal quality
                        quality = 15
                        data.append((angle_deg, distance_mm, quality))
                        angle += scan.angle_increment

                    if data:
                        try:
                            self.scan_queue.put_nowait(data)
                        except queue.Full:
                            try:
                                _ = self.scan_queue.get_nowait()
                                self.scan_queue.put_nowait(data)
                            except Exception:
                                pass
                else:
                    # Avoid busy loop if no data
                    time.sleep(0.005)
            except Exception as e:
                # Log once per second at most
                print(f"Error reading scan (SDK): {e}")
                time.sleep(0.1)

    # --- Serial fallback (not fully implemented) ---
    def _read_scans_serial_stub(self):
        """Reads from serial port but informs that parsing is not implemented.

        This preserves previous behavior but clarifies why no points appear.
        """
        warned = False
        while self.running:
            try:
                if not warned:
                    print("⚠ Using raw-serial mode without a parser — no points will be shown.\n"
                          "  Install the SDK (pip install ydlidar) or run with --simulator.")
                    warned = True
                # Drain some bytes to avoid blocking
                _ = self.serial_conn.read(256)
                time.sleep(0.02)
            except Exception as e:
                print(f"Error reading (RAW serial): {e}")
                time.sleep(0.05)

    def get_scan(self):
        """Get the latest scan data."""
        try:
            return self.scan_queue.get_nowait()
        except queue.Empty:
            return []


class LidarVisualizer:
    """Real-time visualization of LiDAR data."""
    
    def __init__(self, lidar, scan_rate=10, save_data=None):
        self.lidar = lidar
        self.scan_rate = scan_rate
        self.save_data = save_data
        self.paused = False
        self.data_buffer = deque(maxlen=1)  # Keep only latest scan
        
        # Setup the plot
        self.fig = plt.figure(figsize=(12, 10))
        self.fig.canvas.manager.set_window_title('YDLidar X2 Visualization - Eurobot 2026')
        
        # Create subplots
        self.ax_polar = plt.subplot(2, 2, 1, projection='polar')
        self.ax_cartesian = plt.subplot(2, 2, 2)
        self.ax_distance = plt.subplot(2, 2, 3)
        self.ax_info = plt.subplot(2, 2, 4)
        
        self._setup_plots()
        
        # Statistics
        self.scan_count = 0
        self.start_time = time.time()
        
    def _setup_plots(self):
        """Setup the plot layouts."""
        # Polar plot
        self.ax_polar.set_title('Polar View (Top-Down)', pad=20, fontsize=12, fontweight='bold')
        self.ax_polar.set_theta_zero_location('N')
        self.ax_polar.set_theta_direction(-1)
        self.ax_polar.set_ylim(0, 10000)  # 10 meters max
        self.ax_polar.set_rticks([2000, 4000, 6000, 8000, 10000])
        self.ax_polar.set_yticklabels(['2m', '4m', '6m', '8m', '10m'])
        self.ax_polar.grid(True, alpha=0.3)
        
        # Add danger zone circle (e.g., 30cm)
        danger_circle = Circle((0, 0), 300, transform=self.ax_polar.transData._b,
                              color='red', alpha=0.1, label='Danger Zone')
        
        # Cartesian plot
        self.ax_cartesian.set_title('Cartesian View (X-Y)', fontsize=12, fontweight='bold')
        self.ax_cartesian.set_xlabel('X Distance (mm)')
        self.ax_cartesian.set_ylabel('Y Distance (mm)')
        self.ax_cartesian.set_xlim(-10000, 10000)
        self.ax_cartesian.set_ylim(-10000, 10000)
        self.ax_cartesian.grid(True, alpha=0.3)
        self.ax_cartesian.set_aspect('equal')
        
        # Add robot position marker
        self.ax_cartesian.plot(0, 0, 'ro', markersize=10, label='Robot')
        self.ax_cartesian.legend(loc='upper right')
        
        # Distance histogram
        self.ax_distance.set_title('Distance Distribution', fontsize=12, fontweight='bold')
        self.ax_distance.set_xlabel('Distance (m)')
        self.ax_distance.set_ylabel('Number of Points')
        self.ax_distance.grid(True, alpha=0.3, axis='y')
        
        # Info panel
        self.ax_info.axis('off')
        self.info_text = self.ax_info.text(0.1, 0.5, '', fontsize=10, 
                                           verticalalignment='center',
                                           family='monospace')
        
        plt.tight_layout()
    
    def _update_info_panel(self, scan_data):
        """Update the information panel."""
        elapsed_time = time.time() - self.start_time
        fps = self.scan_count / elapsed_time if elapsed_time > 0 else 0
        
        num_points = len(scan_data)
        if num_points > 0:
            distances = [d for _, d, _ in scan_data]
            min_dist = min(distances)
            max_dist = max(distances)
            avg_dist = np.mean(distances)
        else:
            min_dist = max_dist = avg_dist = 0
        
        info = f"""
╔════════════════════════════════════════╗
║      YDLidar X2 - Live Statistics     ║
╠════════════════════════════════════════╣
║ Status:      {'⏸ PAUSED' if self.paused else '▶ RUNNING'}                      ║
║ Scan Count:  {self.scan_count:<6d}                     ║
║ Scan Rate:   {fps:>6.1f} Hz                   ║
║ Data Points: {num_points:<6d}                     ║
║                                        ║
║ Distance Statistics:                   ║
║   Min:  {min_dist/1000:>6.2f} m                       ║
║   Max:  {max_dist/1000:>6.2f} m                       ║
║   Avg:  {avg_dist/1000:>6.2f} m                       ║
║                                        ║
║ Controls:                              ║
║   Space : Pause/Resume                 ║
║   S     : Save snapshot                ║
║   R     : Reset                        ║
║   Q/Esc : Quit                         ║
╚════════════════════════════════════════╝

Application: Eurobot 2026
Team: INSA Eurobot Team
"""
        self.info_text.set_text(info)
    
    def update(self, frame):
        """Update function for animation."""
        if self.paused:
            return
        
        # Get latest scan data
        scan_data = self.lidar.get_scan()
        if not scan_data:
            return
        
        self.scan_count += 1
        self.data_buffer.append(scan_data)
        
        # Extract data
        angles = np.array([np.deg2rad(angle) for angle, _, _ in scan_data])
        distances = np.array([distance for _, distance, _ in scan_data])
        
        # Update polar plot
        self.ax_polar.clear()
        self._setup_polar_plot()
        self.ax_polar.scatter(angles, distances, c=distances, cmap='jet', 
                             s=2, alpha=0.6, vmin=0, vmax=10000)
        
        # Update cartesian plot
        self.ax_cartesian.clear()
        self._setup_cartesian_plot()
        x = distances * np.sin(angles)
        y = distances * np.cos(angles)
        self.ax_cartesian.scatter(x, y, c=distances, cmap='jet', 
                                 s=2, alpha=0.6, vmin=0, vmax=10000)
        self.ax_cartesian.plot(0, 0, 'ro', markersize=10, label='Robot')
        
        # Update distance histogram
        self.ax_distance.clear()
        self._setup_distance_plot()
        self.ax_distance.hist(distances / 1000, bins=50, range=(0, 10),
                             color='steelblue', alpha=0.7, edgecolor='black')
        
        # Update info panel
        self._update_info_panel(scan_data)
        
        # Save data if requested
        if self.save_data and self.scan_count == 1:
            self._save_scan_data(scan_data)
    
    def _setup_polar_plot(self):
        """Setup polar plot after clear."""
        self.ax_polar.set_title('Polar View (Top-Down)', pad=20, fontsize=12, fontweight='bold')
        self.ax_polar.set_theta_zero_location('N')
        self.ax_polar.set_theta_direction(-1)
        self.ax_polar.set_ylim(0, 10000)
        self.ax_polar.set_rticks([2000, 4000, 6000, 8000, 10000])
        self.ax_polar.set_yticklabels(['2m', '4m', '6m', '8m', '10m'])
        self.ax_polar.grid(True, alpha=0.3)
    
    def _setup_cartesian_plot(self):
        """Setup cartesian plot after clear."""
        self.ax_cartesian.set_title('Cartesian View (X-Y)', fontsize=12, fontweight='bold')
        self.ax_cartesian.set_xlabel('X Distance (mm)')
        self.ax_cartesian.set_ylabel('Y Distance (mm)')
        self.ax_cartesian.set_xlim(-10000, 10000)
        self.ax_cartesian.set_ylim(-10000, 10000)
        self.ax_cartesian.grid(True, alpha=0.3)
        self.ax_cartesian.set_aspect('equal')
    
    def _setup_distance_plot(self):
        """Setup distance plot after clear."""
        self.ax_distance.set_title('Distance Distribution', fontsize=12, fontweight='bold')
        self.ax_distance.set_xlabel('Distance (m)')
        self.ax_distance.set_ylabel('Number of Points')
        self.ax_distance.grid(True, alpha=0.3, axis='y')
    
    def _save_scan_data(self, scan_data):
        """Save scan data to CSV file."""
        try:
            with open(self.save_data, 'w') as f:
                f.write('angle_deg,distance_mm,quality\n')
                for angle, distance, quality in scan_data:
                    f.write(f'{angle},{distance},{quality}\n')
            print(f"✓ Saved scan data to {self.save_data}")
        except Exception as e:
            print(f"✗ Failed to save data: {e}")
    
    def on_key_press(self, event):
        """Handle keyboard events."""
        if event.key == ' ':  # Space
            self.paused = not self.paused
            print(f"{'⏸ Paused' if self.paused else '▶ Resumed'}")
        elif event.key == 's':  # Save
            if self.data_buffer:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'lidar_snapshot_{timestamp}.csv'
                self._save_scan_data(self.data_buffer[-1])
        elif event.key == 'r':  # Reset
            self.scan_count = 0
            self.start_time = time.time()
            print("↻ Reset statistics")
        elif event.key in ['q', 'escape']:  # Quit
            plt.close(self.fig)
    
    def run(self):
        """Start the visualization."""
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Start animation
        interval = 1000 / self.scan_rate  # milliseconds
        ani = animation.FuncAnimation(self.fig, self.update, 
                                     interval=interval, blit=False)
        
        print("\n" + "="*50)
        print("  YDLidar X2 Visualization - Eurobot 2026")
        print("="*50)
        print("\nControls:")
        print("  Space    : Pause/Resume")
        print("  S        : Save snapshot")
        print("  R        : Reset statistics")
        print("  Q or Esc : Quit")
        print("\nClose the window or press Q to exit.\n")
        
        plt.show()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='YDLidar X2 Visualization for Eurobot 2026',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --port /dev/ttyUSB0
  %(prog)s --scan-rate 10 --save-data scan.csv
        """
    )
    
    parser.add_argument('--port', default=None,
                       help='Serial port for LiDAR (default: auto-detect on your platform)')
    parser.add_argument('--baudrate', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    parser.add_argument('--scan-rate', type=int, default=10,
                       help='Target scan rate in Hz (default: 10)')
    parser.add_argument('--save-data', type=str,
                       help='Save scan data to CSV file')
    parser.add_argument('--simulator', action='store_true',
                       help='Use simulator mode (no hardware required)')
    
    args = parser.parse_args()
    
    # Helper: try to auto-detect a likely LiDAR serial port when none provided
    def _auto_detect_port():
        try:
            from serial.tools import list_ports
        except Exception:
            return None

        ports = list(list_ports.comports())
        if not ports:
            return None

        # Known CP210x USB-UART bridge often used by YDLidar X2 (VID: 0x10C4, PID: 0xEA60)
        for c in ports:
            try:
                if c.vid and c.pid and (c.vid == 0x10C4 and c.pid == 0xEA60):
                    return c.device
            except Exception:
                pass

        # Try to find ports mentioning 'ydlidar' or 'yd' in description
        for c in ports:
            desc = (c.description or '').lower()
            if 'ydlidar' in desc or 'yd' in desc or 'cp210' in desc or 'silicon' in desc:
                return c.device

        # Fallback: if only one port present, return it
        if len(ports) == 1:
            return ports[0].device

        return None

    # Initialize LiDAR
    if args.simulator:
        print("🔧 Starting in SIMULATOR mode...")
        lidar = YDLidarX2Simulator()
    else:
        # Pick port: CLI value > auto-detect > sensible platform default
        detected_port = args.port
        if not detected_port:
            detected_port = _auto_detect_port()

        if not detected_port:
            if os.name == 'nt' or platform.system().lower().startswith('win'):
                detected_port = 'COM9'
            else:
                detected_port = '/dev/ttyUSB0'

        print(f"🔧 Connecting to YDLidar X2 on {detected_port}...")
        lidar = YDLidarX2(port=detected_port, baudrate=args.baudrate)
    
    # Try to connect
    if not lidar.connect():
        print("\n⚠ Hardware not detected. Switching to SIMULATOR mode...")
        print("   (To use real hardware, ensure it's connected and you have permissions)")
        lidar = YDLidarX2Simulator()
        lidar.connect()
    
    try:
        # Start scanning
        lidar.start_scan()
        
        # Create and run visualizer
        visualizer = LidarVisualizer(lidar, scan_rate=args.scan_rate, 
                                     save_data=args.save_data)
        visualizer.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print("\n🔌 Shutting down...")
        lidar.stop_scan()
        lidar.disconnect()
        print("✓ Done")


if __name__ == '__main__':
    main()
