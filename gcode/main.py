import matplotlib.pyplot as plt
import re
import math

# --- Lettura e parsing GCode ---
filename = "abc.nc"
with open(filename, "r") as f:
    lines = f.readlines()

all_paths = []
current_path = []

for line in lines:
    line = line.strip()
    if line.startswith("G01") or line.startswith("G1"):
        coords = re.findall(r'X([-+]?[0-9]*\.?[0-9]+)\s*Y([-+]?[0-9]*\.?[0-9]+)', line)
        if coords:
            x, y = map(float, coords[0])
            current_path.append([x, y])
    elif line.startswith("G00") or line.startswith("G0"):
        if current_path:
            all_paths.append(current_path)
            current_path = []
if current_path:
    all_paths.append(current_path)

# --- Inizio da [0,0] ---
blue_path = [[0, 0]]

# --- Funzione per trovare path più vicino ---
def find_nearest_path(blue, paths):
    min_dist = float('inf')
    nearest_path_index = -1
    nearest_blue_idx = -1
    nearest_path_point_idx = -1
    for i, path in enumerate(paths):
        for j, (px, py) in enumerate(path):
            for k, (bx, by) in enumerate(blue):
                dist = math.hypot(px - bx, py - by)
                if dist < min_dist:
                    min_dist = dist
                    nearest_path_index = i
                    nearest_path_point_idx = j
                    nearest_blue_idx = k
    return nearest_path_index, nearest_path_point_idx, nearest_blue_idx

# --- Ciclo: aggiungi tutti i path uno per volta ---
while all_paths:
    nearest_idx, path_point_idx, blue_idx = find_nearest_path(blue_path, all_paths)
    nearest_path = all_paths.pop(nearest_idx)
    rotated_path = nearest_path[path_point_idx:] + nearest_path[:path_point_idx]


    rotated_path.append(rotated_path[0])
    pth=blue_path[:blue_idx+1]

    # Unisci i percorsi
    blue_path = blue_path[:blue_idx+1] + rotated_path  + blue_path[blue_idx:]

# --- Torna a 0,0 alla fine ---
if blue_path[-1] != [0,0]:
    blue_path.append([0,0])

# --- Visualizzazione finale ---
plt.figure(figsize=(10,10))
xs, ys = zip(*blue_path)
plt.plot(xs, ys, color='blue', linewidth=2)
plt.scatter([0], [0], color='red', s=50, label='0,0 inizio/fine')
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.title("Percorso unito (partenza da 0,0)")
plt.show()

# --- Salvataggio G-code risultato ---
output_filename = "abc_risultato.nc"

with open(output_filename, "w") as f:
    # Accensione mandrino/laser (opzionale)
    f.write("M3 S1000\n")

    # Partenza da 0,0
    f.write(f"G0 X{blue_path[0][0]} Y{blue_path[0][1]}\n")

    # Scrivi tutti i punti del percorso
    for point in blue_path[1:]:
        x, y = point
        f.write(f"G1 X{x} Y{y}\n")

    # Spegnimento mandrino/laser
    f.write("M5\n")

print(f"G-code salvato in: {output_filename}")



