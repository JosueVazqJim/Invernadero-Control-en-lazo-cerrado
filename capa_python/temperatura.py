import tkinter as tk


#temperatura, sera insertado en la interfaz principal
class Temperatura:
	def __init__(self, master):
		self.master = master  # es el tk principal
		self.frame = tk.Frame(
			master, 
			bg="#ffffff", 
			highlightbackground="#dedede", 
			highlightthickness=2
		) 

		# Configurar el grid del frame
		self.frame.columnconfigure(0, weight=1)
		self.frame.rowconfigure(0, weight=1)
		self.frame.rowconfigure(1, weight=1)


		# Fila 0: Título
		self.label = tk.Label(
			self.frame, 
			text="🌡️Temperatura Actual", 
			font=("Arial", 22, "bold"), 
			bg="#ffffff", fg="#3d4a2c", 
			anchor="w", justify="left"
		)
		self.label.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

		# Fila 1: Temperatura
		self.temperatura_label = tk.Label(
			self.frame, 
			text="25 °C",  # Aquí se mostraría la temperatura real
			font=("Arial", 56, "bold"), 
			bg="#ffffff", fg="#c2925a"
		)
		self.temperatura_label.grid(row=1, column=0, sticky="nsew")
