import tkinter as tk
import requests

esp32_ip = "10.174.36.199"

def Close_Window():
    cuadro.destroy()


def actualizar_tiempo(color, valor):
    try:
        response = requests.get(f"http://{esp32_ip}/set/{color}?t={valor}")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# ----------------- Funciones LED -----------------
def controlar_led(color, accion):
    try:
        response = requests.get(f"http://{esp32_ip}/led/{color}/{accion}")
        print(response.text)
        actualizar_visual(color, accion)  # Actualiza el semáforo visual
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def Encender_Todos():
    for color in ["verde", "amarillo", "rojo"]:
        controlar_led(color, "on")

def Apagar_Todos():
    for color in ["verde", "amarillo", "rojo"]:
        controlar_led(color, "off")

def Iniciar_Secuencia():
    global secuencia_activa
    secuencia_activa = True
    #secuencia_leds()  # Inicia la secuencia
    try:
        response = requests.get(f"http://{esp32_ip}/led/secuencia/on")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def Pausar_Secuencia():
    global secuencia_activa
    secuencia_activa = False
    #Apagar_Todos()  # Apaga todos los LEDs
    try:
        response = requests.get(f"http://{esp32_ip}/led/secuencia/off")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# FUNCION QUE ENCIENDE EL SEMAFORO VIRTUAL
secuencia_activa = False  # Bandera para controlar la secuencia

def actualizar_visual(color, estado):
    if color == "verde":
        semaforo_canvas.itemconfig(led_verde, fill="green" if estado=="on" else "gray")
    elif color == "amarillo":
        semaforo_canvas.itemconfig(led_amarillo, fill="yellow" if estado=="on" else "gray")
    elif color == "rojo":
        semaforo_canvas.itemconfig(led_rojo, fill="red" if estado=="on" else "gray")

def secuencia_leds():
    global secuencia_activa
    if not secuencia_activa:
        return

    # Encender Verde
    controlar_led("verde", "on")
    controlar_led("amarillo", "off")
    controlar_led("rojo", "off")
    cuadro.after(scale_verde.get(), siguiente_amarillo)  # Espera tiempo del slider verde

def siguiente_amarillo():
    if not secuencia_activa:
        return
    controlar_led("verde", "off")
    controlar_led("amarillo", "on")
    controlar_led("rojo", "off")
    cuadro.after(scale_amarillo.get(), siguiente_rojo)  # Espera tiempo del slider amarillo

def siguiente_rojo():
    if not secuencia_activa:
        return
    controlar_led("verde", "off")
    controlar_led("amarillo", "off")
    controlar_led("rojo", "on")
    cuadro.after(scale_rojo.get(), secuencia_leds)  # Repetir la secuencia


#  ------------------------------------------                   VISTA DE LA INTERFAS

# ----------------- Ventana Principal -----------------
cuadro = tk.Tk()
cuadro.title("Control de Semáforo ESP32")
cuadro.geometry("800x500")
cuadro.configure(bg="#2c3e50")

# ----------------- Frames -----------------
control_frame = tk.Frame(cuadro, bg="#34495e", padx=20, pady=20)
control_frame.pack(side=tk.LEFT, fill=tk.Y)

slider_frame = tk.Frame(cuadro, bg="#2c3e50", padx=20, pady=20)
slider_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Canvas para semáforo
semaforo_canvas = tk.Canvas(slider_frame, width=100, height=300, bg="black")
semaforo_canvas.pack(pady=20)

# Dibujar los círculos (LEDs) apagados inicialmente
led_verde = semaforo_canvas.create_oval(20, 220, 80, 280, fill="gray")
led_amarillo = semaforo_canvas.create_oval(20, 120, 80, 180, fill="gray")
led_rojo = semaforo_canvas.create_oval(20, 20, 80, 80, fill="gray")

# ----------------- Botones LED -----------------
tk.Label(control_frame, text="Control Individual", fg="white", bg="#34495e", font=("Arial", 14, "bold")).pack(pady=10)

btns = [
    ("Encender Verde", "verde", "on", "green"),
    ("Apagar Verde", "verde", "off", "gray"),
    ("Encender Amarillo", "amarillo", "on", "yellow"),
    ("Apagar Amarillo", "amarillo", "off", "gray"),
    ("Encender Rojo", "rojo", "on", "red"),
    ("Apagar Rojo", "rojo", "off", "gray"),
]

for text, color, accion, bgc in btns:
    tk.Button(control_frame, text=text, bg=bgc, fg="black", font=("Arial", 12), 
              width=15, command=lambda c=color, a=accion: controlar_led(c, a)).pack(pady=5)

# ----------------- Botones Generales -----------------
tk.Label(control_frame, text="Control General", fg="white", bg="#34495e", font=("Arial", 14, "bold")).pack(pady=20)
tk.Button(control_frame, text="Encender Todos", bg="green", fg="white", font=("Arial", 12), width=15, command=Encender_Todos).pack(pady=5)
tk.Button(control_frame, text="Apagar Todos", bg="red", fg="white", font=("Arial", 12), width=15, command=Apagar_Todos).pack(pady=5)
tk.Button(control_frame, text="Iniciar Secuencia", bg="#27ae60", fg="white", font=("Arial", 12), width=15, command=Iniciar_Secuencia).pack(pady=5)
tk.Button(control_frame, text="Pausar Secuencia", bg="#c0392b", fg="white", font=("Arial", 12), width=15, command=Pausar_Secuencia).pack(pady=5)
tk.Button(control_frame, text="Cerrar", bg="gray", fg="white", font=("Arial", 12), width=15, command=Close_Window).pack(pady=30)

# ----------------- Sliders -----------------
tk.Label(slider_frame, text="Ajuste de Tiempos (ms)", fg="white", bg="#2c3e50", font=("Arial", 16, "bold")).pack(pady=10)

# Crear sliders y guardarlos en variables globales
tk.Label(slider_frame, text="LED ROJO", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=10)
scale_rojo = tk.Scale(slider_frame, from_=500, to=10000, orient=tk.HORIZONTAL, length=300, 
                      command=lambda val: actualizar_tiempo("rojo", val))
scale_rojo.set(2000)
scale_rojo.pack(pady=10)

tk.Label(slider_frame, text="LED AMARILLO", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=10)
scale_amarillo = tk.Scale(slider_frame, from_=500, to=10000, orient=tk.HORIZONTAL, length=300, 
                          command=lambda val: actualizar_tiempo("amarillo", val))
scale_amarillo.set(2000)
scale_amarillo.pack(pady=10)

tk.Label(slider_frame, text="LED VERDE", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=10)
scale_verde = tk.Scale(slider_frame, from_=500, to=10000, orient=tk.HORIZONTAL, length=300, 
                       command=lambda val: actualizar_tiempo("verde", val))
scale_verde.set(2000)
scale_verde.pack(pady=10)

cuadro.mainloop()
