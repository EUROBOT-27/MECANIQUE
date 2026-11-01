# Docker Deployment Guide

This directory contains Docker configuration for the Computer Vision project, optimized for both production deployment and development environments.

## 🐳 Quick Start

### Production Deployment
```bash
# Build and run the production container
docker-compose up --build computer-vision

# Or run in detached mode
docker-compose up -d computer-vision
```

### Development Environment
```bash
# Start development container with code mounting
docker-compose --profile dev up computer-vision-dev

# Enter the development container
docker exec -it computer_vision_dev bash
```

## 📁 Files Overview

### `dockerfile`
Multi-stage Docker build optimized for computer vision applications:
- **Stage 1 (Builder)**: Installs all build dependencies and Python packages
- **Stage 2 (Runtime)**: Minimal runtime image with only necessary libraries
- **Features**:
  - OpenCV with full video codec support
  - YOLO/Ultralytics optimization
  - Non-root user for security
  - Health checks
  - Camera device access

### `.dockerignore`
Optimizes build context by excluding:
- Development files (IDE configs, logs)
- Large datasets and training artifacts
- Python cache and virtual environments
- Documentation and test files

### `docker-compose.yml`
Provides two service configurations:
- **computer-vision**: Production service with resource limits
- **computer-vision-dev**: Development service with code mounting

### `requirements.txt`
Optimized dependencies with version pinning:
- Headless OpenCV for container environments
- Platform-specific packages (ARM64 support)
- Conditional ROS dependencies for Linux

## 🚀 Build and Run Options

### Build Only
```bash
docker build -t computer-vision:latest .
```

### Run with Custom Command
```bash
# Run color detection task
docker run --rm --device=/dev/video0 computer-vision:latest \
  python "first_version(yolo+model_keras+opencv)/task1_color_detection/color_detection_ver1.py"

# Run ROS service
docker run -d --name cv-service --network host --device=/dev/video0 \
  computer-vision:latest
```

### Development Mode
```bash
# Mount code for live development
docker run -it --rm -v $(pwd):/app --device=/dev/video0 \
  computer-vision:latest bash
```

## 🔧 Configuration

### Environment Variables
- `PYTHONPATH=/app`: Python module resolution
- `OPENCV_LOG_LEVEL=ERROR`: Reduce OpenCV logging
- `PYTHONUNBUFFERED=1`: Real-time Python output
- `QT_QPA_PLATFORM=offscreen`: Headless GUI backend

### Camera Access
The container requires camera device access:
```bash
# Linux
--device=/dev/video0:/dev/video0

# Windows (with Docker Desktop)
--device=/dev/video0
```

### Volume Mounts
- `./models:/app/models:ro`: Model files (read-only)
- `./logs:/app/logs:rw`: Application logs
- `.:/app:rw`: Development code mounting

## 🔍 Troubleshooting

### Camera Not Working
```bash
# Check camera availability
ls -la /dev/video*

# Test camera in container
docker run --rm --device=/dev/video0 computer-vision:latest \
  python -c "import cv2; cap = cv2.VideoCapture(0); print(f'Camera working: {cap.isOpened()}')"
```

### Memory Issues
```bash
# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

### Permission Errors
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./logs ./models
```

### Model Loading Issues
```bash
# Verify model paths inside container
docker exec computer_vision_service ls -la /app/models/
docker exec computer_vision_service python -c "from ultralytics import YOLO; print('YOLO working')"
```

## 📊 Resource Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 5GB

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 4GB+
- **Storage**: 10GB+
- **GPU**: NVIDIA GPU with CUDA support (optional)

## 🔒 Security Features

- Non-root user execution
- Minimal base image
- Security options enabled
- Resource limits enforced
- Health checks implemented

## 📈 Performance Optimization

1. **Multi-stage build**: Reduces final image size
2. **Headless OpenCV**: Optimized for server environments
3. **Version pinning**: Ensures reproducible builds
4. **Layer caching**: Optimized Dockerfile layer order
5. **Resource limits**: Prevents resource exhaustion

## 🐛 Health Monitoring

The container includes built-in health checks:
```bash
# Check container health
docker ps
docker inspect computer_vision_service --format='{{.State.Health.Status}}'

# View health check logs
docker inspect computer_vision_service --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```