import serial
import time
import tkinter as tk
from tkinter import messagebox
import threading
from screeninfo import get_monitors

class CountdownApp:
    
    def __init__(self, root):


        with open('COM.txt', 'r') as file:
            comPort = file.read()

        self.score_one_digit = 0
        self.score_two_digit = 0
        self.score_one_txt = "00"
        self.score_two_txt = "00"
        
        self.root = root
        self.root.title("Cuenta Regresiva")
        self.root.geometry("1000x600")
        self.root.configure(background='black')

        self.running = False
        self.total_time = 0
        self.fullscreen = False
        self.setup_time = 60
        self.stop_pressed_times = 0

        self.arduino = serial.Serial(comPort, 9600, timeout=2)
        time.sleep(2) 
        self.listen_to_arduino()


        # Frame contenedor para centrar los elementos
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True, padx=0, pady=0)
        self.container.configure(background="black")

        # Etiqueta con el tiempo
        self.label = tk.Label(self.container, text="00:00", background='black',fg='#f3f3f3')
        self.label.configure(justify="right")
        self.label.pack(pady=0, ipady=0)
        #self.label.place(x=0, y=0)
        #self.label.grid(row=0, column=0, columnspan=2, sticky="n", pady=0)

        second_row_frame = tk.Frame(self.container, bg='black')
        second_row_frame.pack()

        self.score_one = tk.Label(second_row_frame, text=self.score_one_txt, bg='black',fg='#ff1a00')
        self.non_score = tk.Label(second_row_frame, text="1", bg='black',fg='black')
        self.score_two = tk.Label(second_row_frame, text=self.score_two_txt, bg='black',fg='#00e5ff')
        
        self.score_one.pack(side="left", padx=25)
        #self.score_one.place(x=130, y=70)
        self.non_score.pack(side="left", padx=25)
        self.score_two.pack(side="left", padx=25)
        #self.score_two.place(x=200, y=70)
        #self.score_one.grid(row=1, column=0, sticky="e", pady=0)
        #self.non_score.grid(row=1, column=1, sticky="w", pady=0)
        #self.score_two.grid(row=1, column=1, sticky="w", pady=0)


        # Botón de pantalla completa
        self.fullscreen_button = tk.Button(self.container, text="Pantalla Completa", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(pady=10)

        # Evento para redimensionar los números según el tamaño de la ventana
        self.root.bind("<Configure>", self.resize_text)

    def listen_to_arduino(self):
        def check_serial():
            while True:
                if self.arduino.in_waiting > 0:
                    signal = self.arduino.readline().decode().strip()
                    match signal:
                        case "START":
                            self.start()
                        case "STOP":
                            self.reset()
                        case "SCORE_ONE_UP":
                            self.score_two_up()
                        case "SCORE_ONE_DOWN":
                            self.score_two_down()
                        case "SCORE_TWO_UP":
                            self.score_one_up()
                        case "SCORE_TWO_DOWN":
                            self.score_one_down()
                        case "MORE_MINUTES":
                            self.more_minutes()
                        case "LESS_MINUTES":
                            self.less_minutes()
                        case "FULL_SCREEN":
                            self.toggle_fullscreen()
                            print("toggoling to full screen")
                            #self.root.attributes("-fullscreen", self.fullscreen)
                            #self.fullscreen_button.configure(text="")
                        case "Received":
                            print("Received")
                    
                    #if signal == "START":
                    #    self.start()  # Start the countdown when the button is pressed
                    
                time.sleep(0.1)
        threading.Thread(target=check_serial, daemon=True).start()

    def start(self):
        if not self.running:
            try:
                # Convertir la entrada a segundos
                minutes = self.setup_time
                seconds = 00
                self.total_time = minutes * 60 + seconds
                if self.total_time <= 0:
                    messagebox.showerror("Error", "Ingresa un tiempo válido.")
                    return
                self.running = True
                self.update_clock()
            except ValueError:
                messagebox.showerror("Error", "Ingresa valores numéricos válidos.")
        self.stop_pressed_times = 0

    def reset(self):
        if self.stop_pressed_times == 3:
            self.setup_time = 60
            self.label.config(text="60:00")
            self.stop_pressed_times = 0
            self.score_one_digit = 0
            self.score_one_txt = self.score_to_string(self.score_one_digit)
            self.score_one.configure(text=self.score_one_txt)
            self.score_two_digit = 0
            self.score_two_txt = self.score_to_string(self.score_two_digit)
            self.score_two.configure(text=self.score_two_txt)
        self.running = False
        minutes = self.setup_time
        seconds = 00
        self.total_time = minutes * 60 + seconds
        self.label.config(text=f"{self.setup_time:02}:00")
        #self.label.config(text="00:00")
        #self.setup_time = 60
        self.stop_pressed_times = self.stop_pressed_times + 1
        self.score_one_digit = 0
        self.score_one_txt = self.score_to_string(self.score_one_digit)
        self.score_one.configure(text=self.score_one_txt)
        self.score_two_digit = 0
        self.score_two_txt = self.score_to_string(self.score_two_digit)
        self.score_two.configure(text=self.score_two_txt)
    
    def score_one_up(self):
        self.score_one_digit = self.score_one_digit + 1
        self.score_one_txt = self.score_to_string(self.score_one_digit)
        print("score_one_up_test")
        self.score_one.configure(text=self.score_one_txt)
        self.arduino.write(("A" + '\n').encode('utf-8'))
        time.sleep(0.5)
        response = None
        if self.arduino.in_waiting > 0:  # Check if there's any data coming from Arduino
            response = self.arduino.readline().decode('utf-8').strip()
        print("Arduino replied:", response)
        #self.arduino.write(("A\n").encode())
        #self.arduino.write(b"\n")
        self.stop_pressed_times = 0
    
    def score_one_down(self):
        if self.score_one_digit > 0:
            self.score_one_digit = self.score_one_digit - 1
        self.score_one_txt = self.score_to_string(self.score_one_digit)
        self.score_one.configure(text=self.score_one_txt)
       
        print("score_one_down_test")
        self.stop_pressed_times = 0

    def score_two_up(self):
        self.score_two_digit = self.score_two_digit + 1
        self.score_two_txt = self.score_to_string(self.score_two_digit)
        self.score_two.configure(text=self.score_two_txt)
        print("score_two_up_test")
        self.arduino.write(("A" + '\n').encode('utf-8'))
        time.sleep(0.5)
        response = None
        if self.arduino.in_waiting > 0:  # Check if there's any data coming from Arduino
            response = self.arduino.readline().decode('utf-8').strip()
        print("Arduino replied:", response)
        #self.arduino.write(("A\n").encode())
        #self.arduino.write(b"\n")
        self.stop_pressed_times = 0
    
    def score_two_down(self):
        if self.score_two_digit > 0:
            self.score_two_digit = self.score_two_digit - 1
        self.score_two_txt = self.score_to_string(self.score_two_digit)
        self.score_two.configure(text=self.score_two_txt)
        print("score_two_down_test")
        self.stop_pressed_times = 0
    
    def more_minutes(self):
        if self.setup_time >= 61:
            self.setup_time = 0
        self.setup_time += 1
        self.label.config(text=f"{self.setup_time:02}:00")
        print("adding more minutes")
        self.stop_pressed_times = 0
    
    def less_minutes(self):
        if self.setup_time >= 61:
            self.setup_time = 0
        if self.setup_time > 0:
            self.setup_time = self.setup_time - 1
            self.label.config(text=f"{self.setup_time:02}:00")
        print("resting minutes")
        self.stop_pressed_times = 0
        

    def score_to_string(self, digit):
        if digit < 10:
            return f"0{digit}"
        else:
            return str(digit)


    def toggle_fullscreen(self):
        #self.start()
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        if self.fullscreen:
            self.fullscreen_button.config(text="Salir de Pantalla Completa")
        else:
            self.fullscreen_button.config(text="Pantalla Completa")
        self.resize_text(None)

    def resize_text(self, event):
        # Obtener el tamaño actual de la ventana 
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Ajustar el tamaño de la fuente basado en el tamaño de la ventana
        font_size = int(min(width, height) * 0.35)  # Elige un factor adecuado para ajustar el tamaño
        self.label.config(font=("Digital Dismay", font_size))

        score_font_size = int(min(width, height) * 0.55)  # Elige un factor adecuado para ajustar el tamaño
        self.score_one.config(font=("Digital Dismay", score_font_size))
        self.score_one.tkraise()
        self.non_score.config(font=("Digital Dismay", score_font_size))
        self.score_two.config(font=("Digital Dismay", score_font_size))
        self.score_two.tkraise()

        
        #self.label.pack_configure(pady=int(height * 0.05))
        #self.second_row_frame.pack_configure(pady=int(height * 0.15))

    def update_clock(self):
        if self.running and self.total_time > 0:
            self.total_time -= 1
            minutes = self.total_time // 60
            seconds = self.total_time % 60
            self.label.config(text=f"{minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_clock)
        elif self.total_time == 0 and self.running:
            self.running = False
            self.arduino.write(b"B")
            #self.arduino.write(b"\n")
            #messagebox.showinfo("Tiempo Finalizado", "¡La cuenta regresiva ha terminado!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()
