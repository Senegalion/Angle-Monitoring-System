# Kod z zmieniającymi się zakresami na biodra i ramiona


from PythonClient import *
import cv2
import numpy as np
import mediapipe as mp
import csv
import os
import tkinter as tk


# Funkcja sprawdzająca, czy dwie liczby są takie same w określonym zakresie procentowym
def within_percent(a, b, percent):
    return abs(a - b) <= percent * max(abs(a), abs(b))


# # Funkcja do wprowadzania nazwy serii
def get_series_name():
    return input("Podaj nazwę serii: ")


# Nazwa pliku, do którego będą zapisywane dane
filename = 'dane_1.csv'

# Ustawienia MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

server = set_socket_server()
dan = [0, 0, 0, 0]  # Lista początkowa
i = 0  # Początkowy indeks
collecting_data = False
session_number = 1
series_name = ""

# Sprawdzanie numeru sesji
if os.path.exists(filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        if len(lines) > 1:
            last_session = lines[-1][0]
            session_number = int(last_session.split('_')[1]) + 1

# # Utworzenie lub otwarcie pliku CSV do zapisu danych
# csv_file = open(filename, mode='a', newline='')
# writer = csv.writer(csv_file)
# # Zapis nagłówków, jeśli plik jest nowy
# if os.stat(filename).st_size == 0:
#     writer.writerow(['SeriesName', 'Session', 'Y1', 'Y2', 'Y3', 'Y4'])

# Ustawienia szerokości i wysokości obrazu
# width = 1000  # Nowa szerokość obrazu
# height = 1000  # Nowa wysokość obrazu
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

cap = cv2.VideoCapture(1)

# Ustawienie szerokości i wysokości obrazu
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Przeskalowanie obrazu do wymiarów ekranu
    frame = cv2.resize(frame, (screen_width, screen_height))

    # Konwersja obrazu na RGB dla MediaPipe
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    # Odbieranie danych z serwera
    markers_list = recv_data(server)
    if markers_list:
        n1 = markers_list[2].id
        y1 = markers_list[2].y

        dan[i] = y1
        i = (i + 1) % 4
        print(dan)

        # Sprawdzenie dwóch pierwszych liczb (ramiona)
        same_first_two = within_percent(dan[0], dan[1], 0.07)
        # if same_first_two:
        #     # print("Pierwsze dwie liczby są takie same w zakresie +/- 15%")
        # else:
        #     print("Pierwsze dwie liczby nie są takie same w zakresie +/- 15%")

        # Sprawdzenie dwóch ostatnich liczb (biodra)
        same_last_two = within_percent(dan[2], dan[3], 0.07)
        # if same_last_two:
        #     print("Ostatnie dwie liczby są takie same w zakresie +/- 10%")
        # else:
        #     print("Ostatnie dwie liczby nie są takie same w zakresie +/- 10%")

        # Kolory kółek na podstawie warunków
        shoulder_color = (0, 255, 0) if same_first_two else (0, 0, 255)
        hip_color = (0, 255, 0) if same_last_two else (0, 0, 255)
    else:
        shoulder_color = (0, 0, 255)
        hip_color = (0, 0, 255)

    # Rysowanie na obrazku, jeśli wykryto punkty kluczowe
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Pozycje ramion i bioder
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        # Konwersja pozycji z NormalizedLandmark do pikseli
        image_height, image_width, _ = frame.shape
        left_shoulder_pos = (int(left_shoulder.x * image_width), int(left_shoulder.y * image_height))
        right_shoulder_pos = (int(right_shoulder.x * image_width), int(right_shoulder.y * image_height))
        left_hip_pos = (int(left_hip.x * image_width), int(left_hip.y * image_height))
        right_hip_pos = (int(right_hip.x * image_width), int(right_hip.y * image_height))

        # Rysowanie kółek na ramionach i biodrach
        cv2.circle(frame, left_shoulder_pos, 10, shoulder_color, -1)
        cv2.circle(frame, right_shoulder_pos, 10, shoulder_color, -1)
        cv2.circle(frame, left_hip_pos, 10, hip_color, -1)
        cv2.circle(frame, right_hip_pos, 10, hip_color, -1)

        # Rysowanie linii łączących punkty na ramionach i biodrach
        cv2.line(frame, left_shoulder_pos, right_shoulder_pos, shoulder_color, 6)
        cv2.line(frame, left_hip_pos, right_hip_pos, hip_color, 6)

    # Zapisywanie danych do pliku CSV, jeśli zbieranie jest włączone
    # if collecting_data:
    #     writer.writerow([series_name, f"{series_name}_{session_number}"] + dan)

    # # Wyświetlanie instrukcji na ekranie
    # cv2.putText(frame, f'Press "s" to start/stop data collection', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # cv2.putText(frame, f'Current Session: {series_name}_{session_number}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # if collecting_data:
    #     cv2.putText(frame, 'Collecting Data...', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # else:
    #     cv2.putText(frame, 'Not Collecting Data', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        collecting_data = not collecting_data
        if collecting_data:
            if series_name == "":
                series_name = get_series_name()
            session_number += 1

cap.release()
# csv_file.close()
cv2.destroyAllWindows()
