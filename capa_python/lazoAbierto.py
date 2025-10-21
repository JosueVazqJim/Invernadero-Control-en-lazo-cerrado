import tkinter as tk
import customtkinter as ctk
import switchTimer as st

#card para el controlador de lazo abierto

class LazoAbierto:
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
		self.frame.rowconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)
		self.frame.rowconfigure(2, weight=1)

		#radiobutton para el mode
		# radiobutton (visual only, sin lógica) - usar CTkRadioButton para estilo consistente
		# usar fg_color para que el indicador quede relleno al seleccionarlo
		self.radio_button = ctk.CTkRadioButton(
			self.frame,
			text="",
			font=("Arial", 12),
			text_color="#3d4a2c",
			variable=self.mode_var,
			value="abierto",
			fg_color="#c2925a",
			hover_color="#d4a574",
			width=20,
			height=20
		)
		self.radio_button.grid(row=0, column=1, columnspan=2, sticky="e")

		# Nota: registrar traza e inicializar el modo al final del constructor,
		# después de crear todos los widgets (para evitar accesos a atributos no inicializados).

		# Fila 0: Título
		self.label = tk.Label(
			self.frame, 
			text="Control de Lazo Abierto", 
			font=("Arial", 22, "bold"), 
			bg="#ffffff", fg="#3d4a2c", 
			anchor="w", justify="left"
		)
		self.label.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

		# ---- Fila 1: Card 1 ----
		self.card1 = tk.Frame(
			self.frame, 
			bg="#fefefe", 
			highlightbackground="#e1dfdf", 
			highlightthickness=1, 
			bd=0, 
			relief="ridge"
		)
		self.card1.grid(row=1, column=0, sticky="nsew", padx=20, pady=10, ipadx=10, ipady=10)

		tk.Label(
			self.card1, 
			text="💡Iluminación", 
			font=("Arial", 16, "bold"), 
			bg="#fefefe", 
			fg="#3d4a2c"
		).pack(anchor="w", padx=10, pady=5)

		# Variable para el texto dinámico
		self.texto_luz = tk.StringVar(value="Apagado")

		# Variable para el estado ON/OFF
		self.estado_luz = tk.IntVar(value=0)

		self.switch_luz = ctk.CTkSwitch(
			self.card1,
			textvariable=self.texto_luz,          # << usamos StringVar aquí
			text_color="#3d4a2c",
			font=("Arial", 18),
			fg_color="#d4d4d0",
			switch_width=70,
			switch_height=32,
			progress_color="#d4a574",
			button_color="#ffffff",
			variable=self.estado_luz,             # << controla el estado
			onvalue=1,
			offvalue=0
		)
		self.switch_luz.configure(command=self.toggle_luz)
		self.switch_luz.pack(anchor="w", padx=10, pady=5)
		
		tk.Label(
			self.card1, 
			text="Timer Automático", 
			font=("Arial", 12), 
			bg="#fefefe", 
			fg="#71796c", 
			justify="left"
		).pack(anchor="w", padx=15, pady=5)

		# # Variable para el texto dinámico
		# self.texto_timer_luz = tk.StringVar(value="Inactivo")

		# # Variable para el estado ON/OFF
		# self.estado_timer_luz = tk.IntVar(value=0)

		# self.switch_timer_luz = ctk.CTkSwitch(
		# 	self.card1,
		# 	textvariable=self.texto_timer_luz,          # << usamos StringVar aquí
		# 	text_color="#3d4a2c",
		# 	font=("Arial", 16),
		# 	fg_color="#3d4a2c",
		# 	switch_width=70,
		# 	switch_height=32,
		# 	progress_color="#7a9461",
		# 	button_color="#ffffff",
		# 	variable=self.estado_timer_luz,             # << controla el estado
		# 	onvalue=1,
		# 	offvalue=0,
		# )
		# self.switch_timer_luz.configure(command=self.toggle_timer_luz)
		# self.switch_timer_luz.pack(anchor="w", padx=60, pady=5)
		self.switch_timer_luz = st.SwitchTimer(self.card1, httpClient=self.httpClient, device='foco')
		self.switch_timer_luz.frame.pack(anchor="w", padx=60, pady=5)
		# conectar cambios del estado del timer para controlar el switch principal
		try:
			# trace_add si está disponible
			self.switch_timer_luz.confirmed.trace_add('write', lambda *a: self._on_timer_luz_change())
		except Exception:
			# compatibilidad con trace
			try:
				self.switch_timer_luz.confirmed.trace('w', lambda *a: self._on_timer_luz_change())
			except Exception:
				pass
		


		# ---- Fila 2: Card 2 ----
		self.card2 = tk.Frame(
			self.frame, 
			bg="#fefefe", 
			highlightbackground="#e1dfdf", 
			highlightthickness=1, 
			bd=0, 
			relief="ridge"
		)
		self.card2.grid(row=2, column=0, sticky="nsew", padx=20, pady=10, ipadx=10, ipady=10)

		tk.Label(
			self.card2, 
			text="🍃 Ventilación", 
			font=("Arial", 16, "bold"), 
			bg="#fefefe", 
			fg="#3d4a2c"
		).pack(anchor="w")

		# Variable para el texto dinámico
		self.texto_ventilacion = tk.StringVar(value="Apagado")

		# Variable para el estado ON/OFF
		self.estado_ventilacion = tk.IntVar(value=0)

		self.switch_ventilacion = ctk.CTkSwitch(
			self.card2,
			textvariable=self.texto_ventilacion,          # << usamos StringVar aquí
			text_color="#3d4a2c",
			font=("Arial", 18),
			fg_color="#d4d4d0",
			switch_width=70,
			switch_height=32,
			progress_color="#d4a574",
			button_color="#ffffff",
			variable=self.estado_ventilacion,             # << controla el estado
			onvalue=1,
			offvalue=0
		)
		self.switch_ventilacion.configure(command=self.toggle_ventilacion)
		self.switch_ventilacion.pack(anchor="w", padx=10, pady=5)

		tk.Label(
			self.card2, 
			text="Timer Automático", 
			font=("Arial", 12), 
			bg="#fefefe", 
			fg="#71796c", 
			justify="left"
		).pack(anchor="w", padx=15, pady=5)

		# # Variable para el texto dinámico
		# self.texto_timer_ventilacion = tk.StringVar(value="Inactivo")

		# # Variable para el estado ON/OFF
		# self.estado_timer_ventilacion = tk.IntVar(value=0)

		# self.switch_timer_ventilacion = ctk.CTkSwitch(
		# 	self.card2,
		# 	textvariable=self.texto_timer_ventilacion,          # << usamos StringVar aquí
		# 	text_color="#3d4a2c",
		# 	font=("Arial", 16),
		# 	fg_color="#d4d4d0",
		# 	switch_width=70,
		# 	switch_height=32,
		# 	progress_color="#7a9461",
		# 	button_color="#ffffff",
		# 	variable=self.estado_timer_ventilacion,             # << controla el estado
		# 	onvalue=1,
		# 	offvalue=0,
		# )
		# self.switch_timer_ventilacion.configure(command=self.toggle_timer_ventilacion)
		# self.switch_timer_ventilacion.pack(anchor="w", padx=60, pady=5)
		self.switch_timer_ventilacion = st.SwitchTimer(self.card2, httpClient=self.httpClient, device='ventilador')
		self.switch_timer_ventilacion.frame.pack(anchor="w", padx=60, pady=5)
		# conectar cambios del estado del timer de ventilacion
		try:
			self.switch_timer_ventilacion.confirmed.trace_add('write', lambda *a: self._on_timer_vent_change())
		except Exception:
			try:
				self.switch_timer_ventilacion.confirmed.trace('w', lambda *a: self._on_timer_vent_change())
			except Exception:
				pass

		# Asegurarnos de que el texto del switch individual refleje cambios programáticos
		try:
			self.estado_luz.trace_add('write', lambda *a: self._update_texto_luz())
		except Exception:
			try:
				self.estado_luz.trace('w', lambda *a: self._update_texto_luz())
			except Exception:
				pass

		try:
			self.estado_ventilacion.trace_add('write', lambda *a: self._update_texto_vent())
		except Exception:
			try:
				self.estado_ventilacion.trace('w', lambda *a: self._update_texto_vent())
			except Exception:
				pass

		# Nota: no aplicar estado inicial. Los controles estarán disponibles al iniciar.
		
		# Registrar la traza de mode_var y sincronizar el estado inicial ahora que
		# todos los widgets han sido creados
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

	# Puedes conectar un comando
	def toggle_luz(self):
		if self.estado_luz.get() == 1:
			self.texto_luz.set("Encendido")
			# petición al dispositivo
			try:
				if self.httpClient is not None:
					self.httpClient.foco_on()
			except Exception:
				pass
		else:
			self.texto_luz.set("Apagado")
			try:
				if self.httpClient is not None:
					self.httpClient.foco_off()
			except Exception:
				pass
			
	def toggle_ventilacion(self):
		if self.estado_ventilacion.get() == 1:
			self.texto_ventilacion.set("Encendido")
			try:
				if self.httpClient is not None:
					self.httpClient.ventilador_on()
			except Exception:
				pass
		else:
			self.texto_ventilacion.set("Apagado")
			try:
				if self.httpClient is not None:
					self.httpClient.ventilador_off()
			except Exception:
				pass

	def toggle_timer_luz(self):
		if self.estado_timer_luz.get() == 1 :
			self.texto_timer_luz.set("Activo")
		else:
			self.texto_timer_luz.set("Inactivo")

	def toggle_timer_ventilacion(self):
		if self.estado_timer_ventilacion.get() == 1:
			self.texto_timer_ventilacion.set("Activo")
		else:
			self.texto_timer_ventilacion.set("Inactivo")

	# nuevo: manejar cambio de modo (activar/desactivar UI y cambiar color)
	def on_mode_change(self):
		mode = None if self.mode_var is None else self.mode_var.get()
		# si el modo es 'abierto' esta tarjeta debe estar activa
		active = (mode == "abierto")
		if active:
			self.enable_controls()
			# color cuando está activo
			self.frame.config(bg="#f6f9f0")
			if hasattr(self, 'label'):
				self.label.config(bg="#f6f9f0")
			# asegurar que el radio muestra el color de seleccionado
			if hasattr(self, 'radio_button'):
				try:
					self.radio_button.configure(fg_color="#c2925a")
				except Exception:
					pass
		else:
			self.disable_controls()
			# color cuando está inactivo
			self.frame.config(bg="#ffffff")
			if hasattr(self, 'label'):
				self.label.config(bg="#ffffff")
			# restablecer a color neutro cuando no está seleccionado
			if hasattr(self, 'radio_button'):
				try:
					self.radio_button.configure(fg_color="#d4d4d0")
				except Exception:
					pass

	def enable_controls(self):
		# habilitar sólo los widgets que existan en esta clase (switches, timers, etc.)
		widgets = []
		# switches
		if hasattr(self, 'switch_luz'):
			widgets.append(self.switch_luz)
		if hasattr(self, 'switch_ventilacion'):
			widgets.append(self.switch_ventilacion)

		# timers (SwitchTimer instances) — habilitar su switch y sus entries si existen
		for timer_attr in ('switch_timer_luz', 'switch_timer_ventilacion'):
			timer = getattr(self, timer_attr, None)
			if timer is not None:
				if hasattr(timer, 'switch'):
					widgets.append(timer.switch)
				for e_name in ('hour_entry', 'minute_entry', 'second_entry'):
					entry = getattr(timer, e_name, None)
					if entry is not None:
						try:
							entry.config(state='normal')
						except Exception:
							pass

		# aplicar state normal a los widgets recopilados
		for w in widgets:
			try:
				w.configure(state='normal')
			except Exception:
				try:
					w.config(state='normal')
				except Exception:
					pass

	def disable_controls(self):
		# Apagar switches principales del lazo abierto y deshabilitarlos
		if hasattr(self, 'estado_luz'):
			try:
				self.estado_luz.set(0)
			except Exception:
				pass
		if hasattr(self, 'switch_luz'):
			try:
				self.switch_luz.configure(state='disabled')
			except Exception:
				pass

		if hasattr(self, 'estado_ventilacion'):
			try:
				self.estado_ventilacion.set(0)
			except Exception:
				pass
		if hasattr(self, 'switch_ventilacion'):
			try:
				self.switch_ventilacion.configure(state='disabled')
			except Exception:
				pass

		# Para cada SwitchTimer: pausar sin resetear remaining, desactivar su switch y dejar entradas en readonly
		for timer_attr in ('switch_timer_luz', 'switch_timer_ventilacion'):
			timer = getattr(self, timer_attr, None)
			if timer is not None:
				# pausar timer (no resetear remaining)
				try:
					timer.running = False
					# desactivar visualmente el switch del timer
					if hasattr(timer, 'estado_timer'):
						try:
							# dejar en 0 (switch visual apagado)
							timer.estado_timer.set(0)
						except Exception:
							pass
				except Exception:
					pass
				# deshabilitar switch widget si existe
				if hasattr(timer, 'switch'):
					try:
						timer.switch.configure(state='disabled')
					except Exception:
						pass
				# dejar las entradas en readonly para indicar pausa
				for e_name in ('hour_entry', 'minute_entry', 'second_entry'):
					entry = getattr(timer, e_name, None)
					if entry is not None:
						try:
							entry.config(state='readonly')
						except Exception:
							pass

	def _on_timer_luz_change(self):
		# Si el timer de luz se activa (estado_timer == 1), encender y bloquear el switch de luz
		try:
			val = int(self.switch_timer_luz.estado_timer.get())
		except Exception:
			val = 0
		if val == 1:
			# apagar switch individual (si estaba encendido) y bloquearlo mientras corre el timer
			try:
				self.estado_luz.set(0)
			except Exception:
				pass
			try:
				self.switch_luz.configure(state='disabled')
			except Exception:
				pass
		else:
			# timer apagado: desbloquear switch para control manual (no lo encendemos automáticamente)
			try:
				self.switch_luz.configure(state='normal')
			except Exception:
				pass

	def _on_timer_vent_change(self):
		# Si el timer de ventilacion se activa (estado_timer == 1), encender y bloquear el switch de ventilacion
		try:
			val = int(self.switch_timer_ventilacion.estado_timer.get())
		except Exception:
			val = 0
		if val == 1:
			# apagar switch individual de ventilacion y bloquearlo mientras corre el timer
			try:
				self.estado_ventilacion.set(0)
			except Exception:
				pass
			try:
				self.switch_ventilacion.configure(state='disabled')
			except Exception:
				pass
		else:
			# timer apagado: desbloquear switch para control manual (no lo encendemos automáticamente)
			try:
				self.switch_ventilacion.configure(state='normal')
			except Exception:
				pass

	def _update_texto_luz(self):
		try:
			if int(self.estado_luz.get()) == 1:
				self.texto_luz.set("Encendido")
			else:
				self.texto_luz.set("Apagado")
		except Exception:
			pass

	def _update_texto_vent(self):
		try:
			if int(self.estado_ventilacion.get()) == 1:
				self.texto_ventilacion.set("Encendido")
			else:
				self.texto_ventilacion.set("Apagado")
		except Exception:
			pass

 	


	