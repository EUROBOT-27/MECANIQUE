#!/usr/bin/env python3
"""Quick test to find available camera indices and test Camo Studio."""
import cv2
import time

print("Testing camera indices with different backends...")
print("(Camo Studio virtual cameras work best with MSMF backend)\n")

for i in range(10):  # Test 0-9
    print(f"\n{'='*60}")
    print(f"Testing camera index {i}...")
    print('='*60)
    
    for backend_name, backend in [("MSMF", cv2.CAP_MSMF), ("DSHOW", cv2.CAP_DSHOW)]:
        print(f"\n  Backend: {backend_name}")
        cap = cv2.VideoCapture(i, backend)
        
        if cap.isOpened():
            print(f"    ✓ Camera opened")
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            # Clear buffer (important for virtual cameras)
            for _ in range(30):
                cap.read()
            time.sleep(0.5)
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                mean_val = frame.mean()
                print(f"    ✓ Frame captured: {width}x{height}")
                print(f"    ✓ Mean pixel value: {mean_val:.2f}")
                
                if mean_val < 1.0:
                    print(f"    ⚠ WARNING: Frame is BLACK!")
                else:
                    print(f"    ✓ Frame has content - THIS ONE SHOULD WORK!")
                    print(f"\n    >>> Use: python calibrate_camera.py --camera {i}")
            else:
                print(f"    ✗ Failed to read frame")
            
            cap.release()
        else:
            print(f"    ✗ Failed to open")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
