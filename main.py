import time
import tkinter as tk
import numpy as np
import pandas as pd
from PIL import Image, ImageTk, ImageDraw

# Constants
ACCEPTABLE_TIME = 1
THRESHOLD_ANGLE_CHANGE = 1.0
THRESHOLD_DISTANCE_CHANGE = 10.0

# Global variables
last_alert_times = [time.time()] * 6
alert_states = [''] * 6
last_angles = [None] * 6
last_points = None
use_simulated_data = True

# Main window for image
image_window = tk.Tk()
image_window.title("Angle Monitoring System - Image")
image_window.geometry("500x500+100+100")  # Position the window at (100, 100)

# Secondary window for table
table_window = tk.Toplevel()
table_window.title("Angle Monitoring System - Table")
table_window.geometry("500x500+610+100")  # Position the window at (610, 100)

image_path = "image.webp"
person_image = Image.open(image_path)
person_image = person_image.resize((400, 400))
person_photo = ImageTk.PhotoImage(person_image)
image_label = tk.Label(image_window, image=person_photo)
image_label.pack(padx=20, pady=20)

mapping_matrix = {
    "neck": [200, 60],
    "shoulder": [68, 134],
    "elbow": [105, 193],
    "hand": [173, 194],
    "hips": [82, 249],
    "knee": [209, 251],
    "heel": [186, 387],
    "toes": [245, 387],
    "table": [230, 180]
}

def highlight_points(image, points, color):
    draw = ImageDraw.Draw(image)
    for point in points:
        x, y = mapping_matrix[point]
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
    return image

def update_image(points_of_the_body, alert_states):
    global person_image, person_photo, image_label
    person_image = Image.open(image_path)
    person_image = person_image.resize((400, 400))

    if alert_states[0]:
        person_image = highlight_points(person_image, ["shoulder", "elbow", "hand"], 'red')
    if alert_states[1]:
        person_image = highlight_points(person_image, ["heel", "knee", "hips"], 'red')
    if alert_states[2]:
        person_image = highlight_points(person_image, ["toes", "heel", "knee"], 'red')
    if alert_states[3]:
        person_image = highlight_points(person_image, ["shoulder", "hips", "knee"], 'red')

    person_photo = ImageTk.PhotoImage(person_image)
    image_label.configure(image=person_photo)
    image_label.image = person_photo

def get_alert(value, acceptable_range, index):
    global last_alert_times, alert_states
    current_time = time.time()
    if value < acceptable_range[0] or value > acceptable_range[1]:
        if current_time - last_alert_times[index] >= ACCEPTABLE_TIME:
            last_alert_times[index] = current_time
            alert_states[index] = '●'
        return alert_states[index]
    else:
        alert_states[index] = ''
        return ''

def calculate_alpha1(points_of_the_body):
    shoulder = np.array(points_of_the_body[1])
    elbow = np.array(points_of_the_body[2])
    hand = np.array(points_of_the_body[3])

    vector_elbow_shoulder = shoulder - elbow
    vector_elbow_hand = hand - elbow

    cosine_alpha1 = np.dot(vector_elbow_shoulder, vector_elbow_hand) / (
            np.linalg.norm(vector_elbow_shoulder) * np.linalg.norm(vector_elbow_hand))

    alpha1 = np.arccos(cosine_alpha1) * (180 / np.pi)

    return round(alpha1, 2)

def calculate_alpha2(points_of_the_body):
    heel = np.array(points_of_the_body[6])
    knee = np.array(points_of_the_body[5])
    hips = np.array(points_of_the_body[4])

    vector_knee_heel = heel - knee
    vector_knee_hips = hips - knee

    cosine_alpha2 = np.dot(vector_knee_heel, vector_knee_hips) / (
            np.linalg.norm(vector_knee_heel) * np.linalg.norm(vector_knee_hips))

    alpha2 = np.arccos(cosine_alpha2) * (180 / np.pi)

    return round(alpha2, 2)

def calculate_alpha3(points_of_the_body):
    knee = np.array(points_of_the_body[5])
    heel = np.array(points_of_the_body[6])
    toes = np.array(points_of_the_body[7])

    vector_heel_knee = knee - heel
    vector_heel_toes = toes - heel

    cosine_alpha3 = np.dot(vector_heel_knee, vector_heel_toes) / (
            np.linalg.norm(vector_heel_knee) * np.linalg.norm(vector_heel_toes))

    alpha3 = np.arccos(cosine_alpha3) * (180 / np.pi)

    return round(alpha3, 2)

def calculate_alpha4(points_of_the_body):
    shoulder = np.array(points_of_the_body[1])
    hips = np.array(points_of_the_body[4])
    knee = np.array(points_of_the_body[5])

    vector_hips_shoulder = shoulder - hips
    vector_hips_knee = knee - hips

    cosine_alpha4 = np.dot(vector_hips_shoulder, vector_hips_knee) / (
            np.linalg.norm(vector_hips_shoulder) * np.linalg.norm(vector_hips_knee))

    alpha4 = np.arccos(cosine_alpha4) * (180 / np.pi)

    return round(alpha4, 2)

def calculate_curvature(points_of_the_body):
    neck = np.array(points_of_the_body[0])
    shoulder = np.array(points_of_the_body[1])
    hips = np.array(points_of_the_body[4])

    collinear = np.allclose(0, np.cross(shoulder - neck, hips - neck))

    if not collinear:
        deviation_angle = 90
        return deviation_angle

    vector_hips_shoulder = shoulder - hips
    deviation_angle = np.arctan2(vector_hips_shoulder[1], vector_hips_shoulder[0]) * (180 / np.pi)

    return round(deviation_angle, 2)

def calculate_angles(points_of_the_body):
    angles = [
        calculate_alpha1(points_of_the_body),
        calculate_alpha2(points_of_the_body),
        calculate_alpha3(points_of_the_body),
        calculate_alpha4(points_of_the_body),
        points_of_the_body[8][2] - points_of_the_body[2][2],  # Δh
        calculate_curvature(points_of_the_body)
    ]
    return angles

def filter_data(new_points):
    global last_points, THRESHOLD_DISTANCE_CHANGE
    if last_points is None:
        last_points = new_points
        return new_points

    filtered_points = []
    for last, new in zip(last_points, new_points):
        if np.linalg.norm(np.array(new) - np.array(last)) > THRESHOLD_DISTANCE_CHANGE:
            filtered_points.append(new)
        else:
            filtered_points.append(last)

    last_points = filtered_points
    return filtered_points

def simulate_optitrack_data():
    new_points = np.array(points) + np.random.normal(0, 5, np.array(points).shape)
    visualize_table(new_points, acceptable_ranges)
    image_window.after(1000, simulate_optitrack_data)

def visualize_table(points_used_to_calculate_angles, acceptable_ranges_of_the_points):
    global last_angles, THRESHOLD_ANGLE_CHANGE

    filtered_points = filter_data(points_used_to_calculate_angles)
    angles = calculate_angles(filtered_points)

    if last_angles is None or None in last_angles:
        last_angles = angles

    data = {
        'Nazwa': ['α1', 'α2', 'α3', 'α4', 'Δh', 'krzywizna'],
        'Wartości': angles,
        'Akceptowalny zakres': acceptable_ranges_of_the_points,
        'Alert': [get_alert(value, range_, i) for i, (value, range_) in
                  enumerate(zip(angles, acceptable_ranges_of_the_points))]
    }

    angle_changes = [abs(new - last) > THRESHOLD_ANGLE_CHANGE for new, last in zip(angles, last_angles)]
    if any(angle_changes):
        last_angles = angles

    df = pd.DataFrame(data)

    text_widget.delete('1.0', tk.END)
    text_widget.insert(tk.END, df.to_string(index=False))

    update_image(filtered_points, alert_states)

# Tkinter text widget for table window
text_widget = tk.Text(table_window, height=30, width=50)
text_widget.pack(padx=20, pady=20)

# Initial points and acceptable ranges
points = [
    [0, 0, 95],  # neck
    [0, 0, 85],  # shoulder
    [10, 0, 60],  # elbow
    [50, 0, 65],  # hand
    [0, 0, 40],  # hips
    [50, 0, 40],  # knee
    [50, 0, 0],  # heel
    [75, 0, 56],  # toes
    [30, 0, 60]  # table
]
acceptable_ranges = [[90, 105], [90, 105], [75, 90], [90, 105], [0, 5], [-30, 5]]

if use_simulated_data:
    simulate_optitrack_data()
else:
    def update_with_static_data():
        visualize_table(points, acceptable_ranges)
        image_window.after(1000, update_with_static_data)
    update_with_static_data()

image_window.mainloop()
