import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox


class SwitchTimer:
    def __init__(self, parent, httpClient=None, device=None):
        # Variables
        self.texto_timer = tk.StringVar(value="Inactivo")
        self.estado_timer = tk.IntVar(value=0)
        # Variable que indica que el timer fue confirmado y está realmente corriendo
        self.confirmed = tk.IntVar(value=0)
        self.remaining = 0
        self.running = False
        # http client y dispositivo ('foco' o 'ventilador') opcionales
        self.httpClient = httpClient
        self.device = device

        # Frame principal
        self.frame = tk.Frame(parent, bg="#fefefe")
        self.frame.pack(anchor="w", padx=20, pady=10, fill="x")

        # Switch a la izquierda
        self.switch = ctk.CTkSwitch(
            self.frame,
            textvariable=self.texto_timer,
            text_color="#3d4a2c",
            font=("Arial", 16),
            fg_color="#d4d4d0",
            switch_width=70,
            switch_height=32,
            progress_color="#7a9461",
            button_color="#ffffff",
            variable=self.estado_timer,
            onvalue=1,
            offvalue=0,
            command=self.toggle
        )
        self.switch.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Frame para los entries de tiempo a la derecha
        self.time_frame = tk.Frame(self.frame, bg="#fefefe")
        self.time_frame.grid(row=0, column=1, padx=(20, 0), pady=5, sticky="w")

        # Variables del tiempo
        self.hour = tk.StringVar(value="00")
        self.minute = tk.StringVar(value="00")
        self.second = tk.StringVar(value="00")

        tk.Label(self.time_frame, text="⏰", bg="#fefefe", font=("Arial", 16)).pack(side="left", padx=(0,0))

        # Entries
        self.hour_entry = tk.Entry(self.time_frame, width=3, font=("Arial", 14), textvariable=self.hour)
        self.hour_entry.pack(side="left")
        tk.Label(self.time_frame, text=":", bg="#fefefe", font=("Arial", 14)).pack(side="left")
        self.minute_entry = tk.Entry(self.time_frame, width=3, font=("Arial", 14), textvariable=self.minute)
        self.minute_entry.pack(side="left")
        tk.Label(self.time_frame, text=":", bg="#fefefe", font=("Arial", 14)).pack(side="left")
        self.second_entry = tk.Entry(self.time_frame, width=3, font=("Arial", 14), textvariable=self.second)
        self.second_entry.pack(side="left")

    def toggle(self):
        if self.estado_timer.get() == 1:
            # Validar el tiempo antes de iniciar
            try:
                total = int(self.hour.get())*3600 + int(self.minute.get())*60 + int(self.second.get())
            except ValueError:
                messagebox.showwarning("Error", "Introduce un tiempo válido (números enteros)")
                self.estado_timer.set(0)
                return

            # Requerir un tiempo mayor que 0
            if total <= 0:
                messagebox.showwarning("Error", "El tiempo debe ser mayor que 0")
                self.estado_timer.set(0)
                return

            # Actualizar remaining con el tiempo ingresado (permite extender o reiniciar la cuenta)
            self.remaining = total

            # Confirmar que el timer realmente se inició (ayuda a evitar reacciones prematuras)
            self.confirmed.set(1)

            # Si hay un httpClient, avisar al dispositivo remoto
            try:
                if self.httpClient is not None and self.device is not None:
                    # enviar petición para arrancar temporizador remoto en segundos (en hilo)
                    import threading
                    def _call_start():
                        try:
                            if self.device == 'ventilador':
                                self.httpClient.ventilador_timer(self.remaining)
                            elif self.device == 'foco':
                                self.httpClient.foco_timer(self.remaining)
                        except Exception:
                            pass
                    threading.Thread(target=_call_start, daemon=True).start()
            except Exception:
                pass

            # Bloquear los entries mientras corre el timer
            self.hour_entry.config(state="readonly")
            self.minute_entry.config(state="readonly")
            self.second_entry.config(state="readonly")

            self.texto_timer.set("Activo")
            self.running = True
            self.run_countdown()

        else:
            # Pausar y desbloquear los entries
            self.running = False
            self.texto_timer.set("Inactivo")
            self.hour_entry.config(state="normal")
            self.minute_entry.config(state="normal")
            self.second_entry.config(state="normal")
            # Al pausar o apagar el timer, confirmed debe quedar a 0
            self.confirmed.set(0)

            # Si tenemos httpClient y device, pedir detener temporizador remoto
            try:
                if self.httpClient is not None and self.device is not None:
                    import threading
                    def _call_stop():
                        try:
                            if self.device == 'ventilador':
                                self.httpClient.ventilador_timer_stop()
                            elif self.device == 'foco':
                                self.httpClient.foco_timer_stop()
                        except Exception:
                            pass
                    threading.Thread(target=_call_stop, daemon=True).start()
            except Exception:
                pass

    def run_countdown(self):
        if self.running and self.remaining > 0:
            hrs, rem = divmod(self.remaining, 3600)
            mins, secs = divmod(rem, 60)
            self.hour.set(f"{hrs:02d}")
            self.minute.set(f"{mins:02d}")
            self.second.set(f"{secs:02d}")

            self.remaining -= 1
            self.frame.after(1000, self.run_countdown)

        elif self.running and self.remaining == 0:
            # Timer terminó
            self.running = False
            self.texto_timer.set("Inactivo")
            self.estado_timer.set(0)

            # Desbloquear entries
            self.hour_entry.config(state="normal")
            self.minute_entry.config(state="normal")
            self.second_entry.config(state="normal")

            # Asegurar que los entries muestren 00:00:00 al terminar
            self.hour.set("00")
            self.minute.set("00")
            self.second.set("00")

            # Garantizar remaining en 0
            self.remaining = 0

            # Confirmado -> 0 ya que terminó
            self.confirmed.set(0)

            messagebox.showinfo("Fin", "⏰ ¡Tiempo agotado!")