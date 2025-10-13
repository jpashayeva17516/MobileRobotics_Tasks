import numpy as np
import matplotlib.pyplot as plt

# === Adjustable parameters ===
WHEEL_BASE = 5.6  # distance (cm) between wheels - adjust to your robot
WHEEL_SPEED_SCALE = 0.2  # scaling factor to convert motor speed to cm/s

# === Load data ===
filename = "movement_log.txt"

data = np.loadtxt(filename, delimiter=",")
time = data[:, 0]
reflection = data[:, 1]
left_speed = data[:, 2]
right_speed = data[:, 3]
grey_count = data[:, 4]

# === Compute robot trajectory ===
dt = np.diff(time, prepend=time[0])
x, y, theta = [0.0], [0.0], 0.0  # start position and heading

for i in range(1, len(time)):
    v_l = left_speed[i] * WHEEL_SPEED_SCALE
    v_r = right_speed[i] * WHEEL_SPEED_SCALE
    v = (v_r + v_l) / 2.0
    omega = (v_r - v_l) / WHEEL_BASE

    theta += omega * dt[i]
    x.append(x[-1] + v * np.cos(theta) * dt[i])
    y.append(y[-1] + v * np.sin(theta) * dt[i])

x, y = np.array(x), np.array(y)

# === Plot trajectory ===
plt.figure(figsize=(8, 8))
plt.plot(x, y, linewidth=2, color='blue', label='Robot Path')
plt.scatter(x[0], y[0], c='green', s=80, label='Start')
plt.scatter(x[-1], y[-1], c='red', s=80, label='End')

# Mark points where grey lines were detected
for i in range(1, len(grey_count)):
    if grey_count[i] > grey_count[i - 1]:
        plt.scatter(x[i], y[i], c='orange', s=60, label=f'Grey {int(grey_count[i])}')

plt.title("EV3 Line Follower Track Reconstruction")
plt.xlabel("X position (cm)")
plt.ylabel("Y position (cm)")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.show()