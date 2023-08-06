from PySide2.QtCore import QTimer
from PySide2.QtWidgets import *
from pynvml import *
import cupy
import psutil
import sys

class CPUloadBar(QProgressBar):
	def __init__(self, parent=None):
		QProgressBar.__init__(self, parent)
		self.t = QTimer()
		self.t.timeout.connect(self.update)
		self.t.start(500)

	def update(self):
		self.setValue(psutil.cpu_percent())
		#self.setFormat("CPU: %p%")
		self.setFormat("CPU")


class ramBar(QProgressBar):
	def __init__(self, parent=None):
		QProgressBar.__init__(self, parent)
		self.t = QTimer()
		self.t.timeout.connect(self.update)
		self.t.start(500)

	def update(self):
		mem = psutil.virtual_memory()
		used = round(mem.used / (1024 * 1024*1024),1)
		total = round(mem.total / (1024 * 1024*1024),1)
		s = "RAM: " + str(used) + " / " + str(total) + " GB"
		self.setValue(100 * used / total)
		if used/total > 0.95:
			print("OUT OF RAM!")
			sys.exit()
		self.setFormat(s)


class GPUloadBar(QProgressBar):
	def __init__(self, parent=None):
		QProgressBar.__init__(self, parent)
		self.t = QTimer()
		self.t.timeout.connect(self.update)
		self.t.start(500)
		nvmlInit()
		self.gpu = nvmlDeviceGetHandleByIndex(0)

	def update(self):
		info = nvmlDeviceGetUtilizationRates(self.gpu)
		self.setValue(info.gpu)
		#self.setFormat("GPU: %p%")
		self.setFormat("GPU")


class GPUmemBar(QProgressBar):
	def __init__(self, parent=None):
		QProgressBar.__init__(self, parent)
		self.t = QTimer()
		self.t.timeout.connect(self.update)
		self.t.start(500)
		self.mempool = cupy.get_default_memory_pool()
		nvmlInit()
		self.gpu = nvmlDeviceGetHandleByIndex(0)

	def update(self):
		info = nvmlDeviceGetMemoryInfo(self.gpu)
		used = round((info.used - self.mempool.total_bytes() + self.mempool.used_bytes()) / (1024 * 1024*1024),1)
		total = round(info.total / (1024 * 1024*1024),1)
		s = "VRAM: " + str(used) + " / " + str(total) + " GB"
		self.setValue(100 * used / total)
		self.setFormat(s)
