import ui.frmMain as main_form
from PySide6.QtWidgets import QMainWindow, QApplication


class MyAppName(QMainWindow, main_form.Ui_frmMain):
    def __init__(self, parent=None):
        super(MyAppName, self).__init__(parent)
        self.setupUi(self)

        self.btnTryMe.clicked.connect(self.try_me)

        self.show()

    def try_me(self):
        self.txtOutput.setText("Thanks for trying me!")


def refresh():
    QApplication.processEvents()
