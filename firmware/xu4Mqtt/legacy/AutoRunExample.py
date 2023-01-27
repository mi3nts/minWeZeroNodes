import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout

from cps.click_counter import ClickCounter


class Window(QWidget):
    sig_print_counter = pyqtSignal(int)

    def __init__(self, parent=None):
        """Create label and StringVar holding its text"""
        super().__init__(parent)
        self.cps_label = QLabel()
        self.cps_label.setText("0 cps")
        self.resize(100, 100)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.cps_label)
        self.setLayout(layout)
        self.sig_print_counter.connect(self.print_counter)

    @pyqtSlot(int)
    def print_counter(self, count):
        """Thread safe label text set"""
        self.cps_label.setText(f"{count} cps")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    # Create and start counter
    click_counter = ClickCounter(window.sig_print_counter.emit)
    click_counter.start()

    app.exec()
    # Qt app is over, cancel click_counter
    click_counter.cancel()