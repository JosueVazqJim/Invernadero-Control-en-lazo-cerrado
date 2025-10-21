import requests

class HTTPClient:
	def __init__(self, ip):
		self.ip = ip
		self.base_url = f"http://{self.ip}"

	# helper GET
	def _get(self, path, params=None, timeout=3):
		url = f"{self.base_url}{path}"
		try:
			resp = requests.get(url, params=params, timeout=timeout)
			resp.raise_for_status()
			return resp
		except Exception as e:
			print(f"HTTP GET error {url} params={params}: {e}")
			return None

	# ---  endpoints de temp.ino para actuadores ---
	def ventilador_on(self):
		"""Enciende ventilador (manual)."""
		resp = self._get("/ventilador/on")
		return resp.text if resp is not None else None

	def ventilador_off(self):
		"""Apaga ventilador (manual)."""
		resp = self._get("/ventilador/off")
		return resp.text if resp is not None else None

	def foco_on(self):
		"""Enciende foco (manual)."""
		resp = self._get("/foco/on")
		return resp.text if resp is not None else None

	def foco_off(self):
		"""Apaga foco (manual)."""
		resp = self._get("/foco/off")
		return resp.text if resp is not None else None

	def ventilador_timer(self, seconds):
		"""Activa temporizador de ventilador. seconds: int (segundos)."""
		try:
			secs = int(seconds)
			if secs < 0:
				raise ValueError("seconds must be non-negative")
		except Exception as e:
			print("Invalid seconds for ventilador_timer:", e)
			return None
		# usa query param "tiempo" que temp.ino espera
		resp = self._get("/ventilador/temporizador", params={"tiempo": str(secs)})
		return resp.text if resp is not None else None

	def ventilador_timer_stop(self):
		"""Detiene temporizador de ventilador."""
		resp = self._get("/ventilador/temporizador/pause")
		return resp.text if resp is not None else None

	def foco_timer(self, seconds):
		"""Activa temporizador de foco. seconds: int (segundos)."""
		try:
			secs = int(seconds)
			if secs < 0:
				raise ValueError("seconds must be non-negative")
		except Exception as e:
			print("Invalid seconds for foco_timer:", e)
			return None
		resp = self._get("/foco/temporizador", params={"tiempo": str(secs)})
		return resp.text if resp is not None else None
	
	def foco_timer_stop(self):
		"""Detiene temporizador de foco."""
		resp = self._get("/foco/temporizador/pause")
		return resp.text if resp is not None else None

	def get_estado(self):
		"""Obtiene estado JSON del dispositivo (temperatura, actuadores, timers...)."""
		resp = self._get("/estado")
		if resp is None:
			return None
		try:
			return resp.json()
		except Exception:
			# fallback: texto bruto si no es JSON
			return resp.text

	def set_goal_temp(self, temp):
		"""Establece temperatura objetivo (0-60). Devuelve respuesta del servidor."""
		try:
			t = int(temp)
		except Exception as e:
			print("Invalid temp value for set_goal_temp:", e)
			return None
		if t < 0 or t > 60:
			print("Temperature out of range (0-60)")
			return None
		resp = self._get("/goalTemp", params={"temp": str(t)})
		return resp.text if resp is not None else None

	# método existente con nombre inapropiado (mantengo para compatibilidad)
	def pussyDestruction(self):
		resp = self._get("/destruction")
		return resp.text if resp is not None else None
# ...existing code...