import h5py

with h5py.File(r'C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\task2_number_detection\digits.h5', 'r') as f:
    print(list(f.keys()))
