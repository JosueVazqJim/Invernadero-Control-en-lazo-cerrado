import tkinter as tk
from PIL import Image, ImageTk   # << Necesitas instalar pillow (pip install pillow)

# ImageManager: carga y cambia imagen según estados
class ImageManager:
	def __init__(self, parent, base_path):
		self.parent = parent
		self.base_path = base_path
		self._img_originals = {}
		self._img_tk = None

		# label para mostrar la imagen
		self.label = tk.Label(parent, bg=parent.cget("bg"))
		self.label.pack(fill="both", expand=True)

		# bind para redimensionar cuando cambie el tamaño del frame
		parent.bind("<Configure>", lambda e: self._redraw())

	def _load(self, name):
		# cachea la imagen PIL original (sin redimensionar)
		if name in self._img_originals:
			return self._img_originals[name]
		try:
			path = f"{self.base_path}/{name}"
			img = Image.open(path).convert("RGBA")
		except Exception as e:
			# fallback: imagen vacía pequeña
			img = Image.new("RGBA", (100, 100), (255,255,255,0))
		self._img_originals[name] = img
		return img

	def choose_image_name(self, luz_on, vent_on):
		if luz_on and vent_on:
			return "focos_ventiladores_ON.png"
		if luz_on:
			return "focos_ON.png"
		if vent_on:
			return "ventiladores_ON.png"
		return "focos_ventiladores_OFF.png"

	def update_states(self, luz_on, vent_on):
		# setea la imagen apropiada y redibuja
		name = self.choose_image_name(luz_on, vent_on)
		self._current = name
		self._redraw()

	def _redraw(self):
		orig = getattr(self, "_current", "focos_ventiladores_OFF.png")
		img_orig = self._load(orig)
		# tamaño disponible dentro del frame (restar padding)
		w = max(1, int(self.parent.winfo_width() * 1.2))  # Aumenta el ancho un 20%
		h = max(1, int(self.parent.winfo_height() * 1.1)) # Mantiene el alto igual
		ow, oh = img_orig.size
		ratio = min(w/ow, h/oh)
		new_w = max(1, int(ow * ratio))
		new_h = max(1, int(oh * ratio))
		resized = img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
		self._img_tk = ImageTk.PhotoImage(resized)
		self.label.config(image=self._img_tk)
