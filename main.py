import pyautogui
import keyboard
import time

print("Cliquez à l’endroit souhaité, puis appuyez 3 fois sur ESPACE pour commencer.")

# --- Capture du clic ---
clic_capture = False
x = y = None

while not clic_capture:
    if pyautogui.mouseDown():  # Si l’utilisateur clique
        x, y = pyautogui.position()
        clic_capture = True
        print(f"Coordonnées capturées : ({x}, {y})")

# --- Attente de 3 espaces pour démarrer ---
start_space_count = 0
print("Appuyez 3 fois sur ESPACE pour démarrer.")

while start_space_count < 3:
    if keyboard.is_pressed("space"):
        start_space_count += 1
        print(f"Espace ({start_space_count}/3)")
        time.sleep(0.4)  # anti-rebond

print("Programme démarré. Clic automatique en cours...")
print("Appuyez 3 fois sur ESPACE pour arrêter.")

# --- Boucle de clic automatique ---
stop_space_count = 0
interval = 0.5  # intervalle de clic en secondes

while True:
    pyautogui.click(x, y)
    time.sleep(interval)

    if keyboard.is_pressed("space"):
        stop_space_count += 1
        print(f"Espace ({stop_space_count}/3) pour arrêt")
        time.sleep(0.4)

    if stop_space_count >= 3:
        print("Programme arrêté.")
        break
