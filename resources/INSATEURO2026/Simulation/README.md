# Robot Path Simulation

A comprehensive 2D robot path planning and simulation environment built with Python and Pygame. This interactive simulation allows you to plan robot trajectories, visualize paths, and simulate realistic robot movement with customizable physics parameters.

## 🚀 Features

### Interactive Path Planning
- **Click-to-Navigate**: Click anywhere on the map to set target coordinates
- **Real-time Coordinates**: Mouse position displayed in millimeters (mm)
- **Multi-Waypoint Paths**: Create complex trajectories with multiple waypoints
- **Visual Path Display**: Arrows show planned trajectory between waypoints
- **Undo Functionality**: Remove waypoints with a single click

### Advanced Robot Control
- **4-Level Parameter Control**: 
  - Linear Velocity (0-3 levels)
  - Angular Velocity (0-3 levels) 
  - Linear Acceleration (0-3 levels)
  - Angular Acceleration (0-3 levels)
- **Precision Angle Control**: Interactive wheel for exact angle setting (0-360°)
- **Direction Toggle**: Switch between forward and backward movement
- **Manual Positioning**: Drag robot to any position on the map

### Realistic Path Execution
- **Smooth Movement**: Physics-based acceleration and velocity
- **Automatic Path Following**: Robot follows planned waypoints sequentially
- **Real-time Control**: Play, pause, and reset functionality
- **Visual Feedback**: Live robot orientation and position updates

### Data Management
- **Path Export**: Save trajectories to JSON format
- **Coordinate Conversion**: Seamless pixel-to-millimeter mapping
- **Session Persistence**: Maintain paths between simulation runs

## 📋 Prerequisites

- **Python 3.x**
- **Pygame library**
- **Required Assets**:
  - `ensi_map.png` - Map background image
  - `my_robot.png` - Robot sprite image

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/INSATEURO2026/Simulation.git
cd Simulation
```

2. **Install dependencies**:
```bash
pip install pygame
```

3. **Verify assets**: Ensure these files are present:
   - `ensi_map.png` (map background)
   - `my_robot.png` (robot sprite)
   - `new_sim.py` (main simulation)

## 🎮 Usage

### Starting the Simulation
```bash
python new_sim.py
```
*The simulation launches in fullscreen mode*

### Control Interface (Left Panel)

#### Parameter Sliders
- **Linear Velocity**: Controls forward/backward speed (4 levels: 0-3)
- **Angular Velocity**: Controls rotation speed (4 levels: 0-3)
- **Linear Acceleration**: Controls movement acceleration (4 levels: 0-3)
- **Angular Acceleration**: Controls rotational acceleration (4 levels: 0-3)

#### Input Fields
- **Target X**: Manual X-coordinate entry (millimeters)
- **Target Y**: Manual Y-coordinate entry (millimeters)  
- **Target Angle**: Direct angle input (degrees)

#### Interactive Controls
- **Angle Wheel**: Visual angle selector - drag the red knob around the circle
- **Direction Toggle**: 
  - 🟢 Green = Forward movement
  - 🔴 Red = Backward movement

#### Action Buttons
- **Validate**: Add current settings as a waypoint to the path
- **UNDO**: Remove the most recent waypoint
- **Save**: Export complete path to `path_points.json`
- **PLAY ▶️**: Begin automatic path execution
- **PAUSE ⏸️**: Halt robot movement
- **RESET 🔄**: Return robot to starting position

### Map Interaction (Right Panel)

#### Mouse Controls
- **Left Click**: Set target coordinates and move robot instantly
- **Drag Robot**: Click and hold robot to reposition manually
- **Coordinate Display**: Real-time mouse position in mm

#### Keyboard Shortcuts
- **ESC**: Exit fullscreen mode

## 📐 Coordinate System

The simulation uses a metric coordinate system:

- **Map Dimensions**: 1800mm × 1200mm
- **Origin (0,0)**: Bottom-left corner
- **X-Axis**: Left → Right (0 to 1800mm)
- **Y-Axis**: Bottom → Top (0 to 1200mm)
- **Angles**: 0° = East, 90° = North, 180° = West, 270° = South

## 📁 Project Structure

```
Simulation/
├── new_sim.py              # Main simulation application
├── ensi_map.png           # Map background image
├── my_robot.png           # Robot sprite image
├── README.md              # Documentation (this file)
├── LICENSE                # License information
└── path_points.json       # Generated path data (after saving)
```

## 🔧 Technical Architecture

### Core Classes

| Class | Purpose |
|-------|---------|
| `Robot` | Handles movement, rendering, and path following logic |
| `Slider4State` | 4-position parameter control slider |
| `InputBox` | Text input fields for coordinate entry |
| `ToggleSwitch` | Binary direction control switch |
| `Button` | Interactive action buttons |
| `AngleWheel` | Circular angle selection control |

### Path Data Format

Saved paths use JSON format with waypoint arrays:
```json
[
  [x_mm, y_mm, angle_degrees, is_forward, linear_vel, angular_vel, linear_acc, angular_acc],
  [450.5, 600.2, 90.0, true, 2, 1, 3, 0],
  ...
]
```

### Performance Specifications

- **Frame Rate**: 60 FPS for smooth animation
- **Screen Resolution**: 1080×720 pixels (fullscreen)
- **Control Panel**: 300px width
- **Map Area**: 780px width (auto-scaled)
- **Movement Speed**: 2 pixels/frame
- **Rotation Speed**: 3 degrees/frame

## 🎨 Customization

### Custom Maps
1. Replace `ensi_map.png` with your map image
2. Update coordinate scaling in code if dimensions differ from 1800×1200mm
3. Map will auto-scale to fit available display area

### Robot Appearance
1. Replace `my_robot.png` with custom sprite
2. Adjust `robot_scale_factor` (currently 0.1) for size
3. Robot automatically rotates to show orientation

### Parameter Tuning
Modify these variables in `new_sim.py`:
- `movement_speed`: Robot movement rate
- `rotation_speed`: Robot rotation rate  
- Scale factors for display sizing

## 🐛 Troubleshooting

### Common Issues

**🖼️ Images Not Loading**
- Verify `ensi_map.png` and `my_robot.png` exist in project directory
- Check file permissions and formats (PNG supported)

**📦 Pygame Import Error**
```bash
pip install pygame
# or
pip install --upgrade pygame
```

**🖥️ Fullscreen Problems**
- Press `ESC` to exit fullscreen
- Try running on different display if issues persist

**💾 Path Save Issues**
- Check write permissions in project directory
- Ensure sufficient disk space
- Close other applications using the directory

**⚡ Performance Issues**
- Reduce map image size if experiencing lag
- Close unnecessary applications
- Check system requirements

## 🚀 Advanced Features

### Path Planning Strategies
- **Sequential Waypoints**: Plan step-by-step movements
- **Loop Paths**: Create closed-loop trajectories  
- **Complex Maneuvers**: Combine forward/backward movements
- **Precision Positioning**: Use coordinate inputs for exact placement

### Simulation Modes
- **Interactive Mode**: Real-time path creation and editing
- **Playback Mode**: Watch planned paths execute automatically
- **Manual Mode**: Direct robot control via dragging

## 🔮 Future Enhancements

### Planned Features
- [ ] **Obstacle Detection**: Add collision avoidance
- [ ] **Multi-Robot Support**: Simulate multiple robots simultaneously  
- [ ] **Path Optimization**: Automatic trajectory smoothing
- [ ] **Hardware Integration**: Connect to real robots
- [ ] **Advanced Physics**: Momentum, friction, and inertia simulation
- [ ] **Custom Map Editor**: Built-in map creation tools
- [ ] **Sensor Simulation**: Virtual sensors and data logging
- [ ] **3D Visualization**: Upgrade to 3D simulation environment

### Community Contributions
- Obstacle course templates
- Robot behavior algorithms
- Custom UI themes
- Performance optimizations

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add docstrings for new functions and classes
- Test thoroughly before submitting
- Update documentation for new features

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/INSATEURO2026/Simulation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/INSATEURO2026/Simulation/discussions)
- **Documentation**: This README and inline code comments

---

**Built with ❤️ for robotics education and research**

*For the latest updates and detailed documentation, visit our [GitHub repository](https://github.com/INSATEURO2026/Simulation)*
