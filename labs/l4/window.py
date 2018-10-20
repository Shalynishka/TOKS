import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QLabel, QDialog, QGridLayout, QFrame, QTextBrowser, QLineEdit)
from random import choice
from time import sleep
# """
# Реализация COM-порта средствами serial
# """

class Detector:
    def __init__(self, collision):
        # self.fifo = []
        self.mas = range(1, 11)
        self.slot_time = 0.1      # miliseconds (we will divide)
        self.collision = collision

    # def add_fifo(self, c):
    #     self.fifo.append(c)

    def make_block(self, mod=0):
        "0 - коллизия, 1 - занят канал"
        return choice(self.mas) % (3 + mod)

    # def lottery(self, k):
    #     return self.slot_time * choice(range(2**k + 1)) / 1000

    def alg(self):
        i = 0
        while i < 11:
            if self.make_block(1):       # проверка на занятость, счетчик не трогаем
                continue
            elif self.make_block():      # проверка на коллизию, делаем розыгрыш и инкрементируем счетчик
                sleep((lambda i: self.slot_time * choice(range(2**i + 1)) / 1000)(i)) # sleep(self.lottery(i))
                # print('X')
                self.collision()
                i += 1
                continue
            else:
                break
        else:
            # self.fifo.pop(0)
            return False
        return True          # self.fifo.pop(0)


class Input(QWidget):
    """
    Класс главного окна
    """

    def __init__(self):
        """Конструктор окна"""
        super().__init__()

        self.lab_in = QLabel("Input is here", self)
        self.lab_out = QLabel('Output is here', self)
        self.lab_debug = QLabel("Debug is here", self)

        self.le_input = QLineEdit(self)
        self.le_output = QTextBrowser(self)
        self.le_debug = QTextBrowser(self)

        self.line = QFrame(self)

        self.d = Detector(self.collision)

        self.init_ui()

    def text_changed(self, c):
        # c = self.le_input.text()
        if len(c) == 0:
            return
        args = self.d.alg()
        if args:
            self.le_output.setText(self.le_output.toPlainText() + c[-1])
        if len(c) != 1:
            self.le_input.setText(c[-1])

    def init_ui(self):
        self.lab_in.move(28, 37)

        self.le_input.move(130, 22)
        self.le_input.setFixedHeight(50)
        self.le_input.setFixedWidth(450)

        self.le_input.textEdited.connect(self.text_changed)

        # поле входящих сообщений
        self.le_output.move(130, 80)
        self.le_output.setFixedHeight(50)
        self.le_output.setFixedWidth(450)

        self.lab_out.move(28, 95)

        self.line.setObjectName('line')
        self.line.setGeometry(10, 127, 580, 127)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        # Debug
        self.lab_debug.move(20, 235)

        self.le_debug.move(130, 220)
        self.le_debug.setFixedHeight(50)
        self.le_debug.setFixedWidth(450)

        self.setGeometry(300, 300, 600, 320)
        self.setWindowTitle('Input dialog')
        self.show()

    def show_dialog(self, warning):
        dialog = QDialog(self)
        dialog.setWindowTitle('warning')

        label = QLabel(warning)
        label.sizeIncrement()

        ok = QPushButton('Ok')
        ok.clicked.connect(dialog.close)

        layout = QGridLayout()
        layout.addWidget(label)
        layout.addWidget(ok)

        dialog.setLayout(layout)

        dialog.show()

    def collision(self):
        self.le_debug.setText(self.le_debug.toPlainText() + ' ' + 'X')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Input()
    sys.exit(app.exec_())

