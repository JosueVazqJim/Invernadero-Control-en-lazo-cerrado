import tkinter as tk
import customtkinter as ctk

#card para el controlador de lazo cerrado

class LazoCerrado:
	def __init__(self, master, mode_var, display, widgets, httpClient):
		self.master = master  # es el tk principal
		self.mode_var = mode_var
		self.httpClient = httpClient
		
		self.frame = tk.Frame(
			master, 
			bg="#ffffff", 
			highlightbackground="#dedede", 
			highlightthickness=2
		) # frame contenedor

		# Configurar el grid del frame
		self.frame.columnconfigure(0, weight=1)
		self.frame.columnconfigure(1, weight=1)
		self.frame.columnconfigure(2, weight=1)
		self.frame.rowconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)
		self.frame.rowconfigure(2, weight=1)
		self.frame.rowconfigure(3, weight=1)
		self.frame.rowconfigure(4, weight=1)
		self.frame.rowconfigure(5, weight=1)

		#radiobutton para el mode
		# radiobutton (visual only, sin lógica) - usar CTkRadioButton para estilo consistente
		# usar fg_color para que el indicador quede relleno al seleccionarlo
		self.radio_button = ctk.CTkRadioButton(
			self.frame,
			text="",
			font=("Arial", 12),
			text_color="#3d4a2c",
			variable=self.mode_var,
			value="cerrado",
			fg_color="#c2925a",
			hover_color="#d4a574",
			width=20,
			height=20
		)
		self.radio_button.grid(row=0, column=2, sticky="w", padx=20, pady=10)


		# Fila 0: Título
		self.labelT = tk.Label(
			self.frame, 
			text="Control de Lazo Cerrado", 
			font=("Arial", 22, "bold"), 
			bg="#ffffff", fg="#3d4a2c", 
			anchor="w", justify="left"
		)
		self.labelT.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

		# ---- Fila 1:  --
		self.label = tk.Label(
			self.frame, 
			text="🎯Temperatura Objetivo", 
			font=("Arial", 16, "bold"), 
			bg="#fefefe", 
			fg="#3d4a2c"
		)
		self.label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0,5))

		# ---- Fila 2: Mostrar valor del scale (encima del slider)
		self.temp_value = tk.StringVar(value="25 °C")
		self.temp_value_label = tk.Label(
			self.frame,
			textvariable=self.temp_value,
			font=("Arial", 48, "bold"),
			bg="#ffffff",
			fg="#c2925a"
		)
		self.temp_value_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(5,0))

		# ---- Fila 3: Slider (customtkinter) de 15 a 35
		# Usamos CTkSlider y actualizamos el label con el valor entero
		self.temp_slider = ctk.CTkSlider(
			self.frame,
			from_=15,
			to=35,
			number_of_steps=20,
			command=self.on_temp_slider,
			bg_color="#ffffff",
			button_color="#c2925a",
			progress_color="#d4a574",
			button_hover_color="#c2925a"
		)
		# Valor inicial
		try:
			self.temp_slider.set(25)
		except Exception:
			pass
		self.temp_slider.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0,0))

		#fila 4 label del ajuste rapido
		self.label_auto = tk.Label(
			self.frame, 
			text="Ajuste Rápido", 
			font=("Arial", 12), 
			bg="#fefefe", 
			fg="#71796c", 
			justify="left"
		)
		self.label_auto.grid(row=4, column=0, columnspan=2, sticky="w", padx=15)

		# ---- Fila 5: Botones de ajuste rápido y boton de aplicar
		self.frame_botones_ajuste = tk.Frame(self.frame, bg="#ffffff")
		self.frame_botones_ajuste.columnconfigure(0, weight=1)
		self.frame_botones_ajuste.columnconfigure(1, weight=1)
		self.frame_botones_ajuste.rowconfigure(0, weight=1)
		self.frame_botones_ajuste.grid(row=5, column=0, sticky="w", padx=20)
		self.boton_menos= ctk.CTkButton(
			self.frame_botones_ajuste,
			text="-1 °C",
			font=("Arial", 18),
			width=150,
			height=30,
			fg_color="#f0f0f0",
			hover_color="#e1dfdf",
			text_color="#57624c",
			command=self.decrease_temp
		)
		self.boton_menos.grid(row=0, column=0, sticky="e", padx=(0,10))

		self.boton_mas= ctk.CTkButton(
			self.frame_botones_ajuste,
			text="+1 °C",
			font=("Arial", 18),
			width=150,
			height=30,
			fg_color="#f0f0f0",
			hover_color="#e1dfdf",
			text_color="#57624c",
			command=self.increase_temp
		)
		self.boton_mas.grid(row=0, column=1, sticky="e", padx=(0,10))

		self.boton_aplicar= ctk.CTkButton(
			self.frame,
			text="Aplicar",
			font=("Arial", 18, "bold"),
			width=200,
			height=30,
			fg_color="#7a9461",
			hover_color="#57624c",
			text_color="white",
			command=self._on_aplicar
		)
		self.boton_aplicar.grid(row=5, column=1, sticky="e", padx=20)

		# Registrar traza para actualizar UI cuando cambie mode_var (ahora que
		# todos los widgets han sido creados)
		if self.mode_var is not None:
			try:
				self.mode_var.trace_add('write', lambda *a: self.on_mode_change())
			except Exception:
				try:
					self.mode_var.trace('w', lambda *a: self.on_mode_change())
				except Exception:
					pass
		# sincronizar estado inicial
		try:
			self.on_mode_change()
		except Exception:
			pass

	def _on_aplicar(self):
		# tomar valor actual del slider y enviar al servidor via httpClient si existe
		try:
			val = int(float(self.temp_slider.get()))
		except Exception:
			val = None
		if val is None:
			return
		# set local label
		try:
			self.temp_value.set(f"{val} °C")
		except Exception:
			pass
		# llamar al httpClient en hilo para no bloquear (preferir self.httpClient)
		try:
			client = None
			if hasattr(self, 'httpClient') and self.httpClient is not None:
				client = self.httpClient
			elif hasattr(self, 'master') and hasattr(self.master, 'httpClient'):
				client = self.master.httpClient
			if client is not None:
				import threading
				threading.Thread(target=lambda: client.set_goal_temp(val), daemon=True).start()
		except Exception:
			pass

	def on_temp_slider(self, value):
		# value puede ser float; mostrar como entero y con unidad
		try:
			val = int(float(value))
		except Exception:
			val = 25
		self.temp_value.set(f"{val} °C")

	def increase_temp(self):
		# Incrementa el slider en 1 grado, hasta el máximo
		try:
			current = int(float(self.temp_slider.get()))
		except Exception:
			current = 25
		new = min(current + 1, int(self.temp_slider._to)) if hasattr(self.temp_slider, '_to') else min(current + 1, 35)
		self.temp_slider.set(new)
		self.on_temp_slider(new)

	def decrease_temp(self):
		# Decrementa el slider en 1 grado, hasta el mínimo
		try:
			current = int(float(self.temp_slider.get()))
		except Exception:
			current = 25
		new = max(current - 1, int(self.temp_slider._from)) if hasattr(self.temp_slider, '_from') else max(current - 1, 15)
		self.temp_slider.set(new)
		self.on_temp_slider(new)

		# nuevo: manejar cambio de modo (activar/desactivar UI y cambiar color)
	def on_mode_change(self):
		mode = None if self.mode_var is None else self.mode_var.get()
		# si el modo es 'cerrado' esta tarjeta debe estar activa
		active = (mode == "cerrado")
		if active:
			self.enable_controls()
			# color cuando está activo
			self.frame.config(bg="#f6f9f0")
			self.labelT.config(bg="#f6f9f0")
			self.label.config(bg="#f6f9f0")
			self.temp_value_label.config(bg="#f6f9f0")
			# asegurar que el radio muestra el color de seleccionado
			if hasattr(self, 'radio_button'):
				try:
					self.radio_button.configure(fg_color="#c2925a")
				except Exception:
					pass
			self.frame_botones_ajuste.config(bg="#f6f9f0")
			self.label_auto.config(bg="#f6f9f0")
			
		else:
			self.disable_controls()
			# color cuando está inactivo
			self.frame.config(bg="#ffffff")
			self.labelT.config(bg="#ffffff")
			self.label.config(bg="#ffffff")
			self.temp_value_label.config(bg="#ffffff")
			# restablecer a color neutro cuando no está seleccionado
			if hasattr(self, 'radio_button'):
				try:
					self.radio_button.configure(fg_color="#d4d4d0")
				except Exception:
					pass
			self.frame_botones_ajuste.config(bg="#ffffff")
			self.label_auto.config(bg="#ffffff")

		# Nota: no aplicar estado inicial. Los controles estarán disponibles al iniciar.

	def enable_controls(self):
		# habilitar widgets; usar try/except por si el widget no soporta 'state'
		try:
			self.temp_slider.configure(state="normal")
		except Exception:
			pass
		for w in (self.boton_mas, self.boton_menos, self.boton_aplicar):
			try:
				w.configure(state="normal")
			except Exception:
				pass

	def disable_controls(self):
		# deshabilitar widgets y (opcional) apagar switch externo si existe
		try:
			self.temp_slider.configure(state="disabled")
		except Exception:
			pass
		for w in (self.boton_mas, self.boton_menos, self.boton_aplicar):
			try:
				w.configure(state="disabled")
			except Exception:
				pass

	

