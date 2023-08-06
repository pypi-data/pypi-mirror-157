from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout

import spective_systembars

if __name__ == '__main__':
	app = QApplication()

	w = QWidget()
	w.setLayout(QVBoxLayout())

	bars = [spective_systembars.CPUloadBar(),spective_systembars.ramBar(),spective_systembars.GPUloadBar(),spective_systembars.GPUmemBar()]

	for b in bars:
		w.layout().addWidget(b)

	w.show()
	app.exec_()

