import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QApplication, QLabel, QDialog, QGridLayout, QFrame, QTextEdit, QTextBrowser, QComboBox)
from PyQt5.QtCore import (QObject, pyqtSignal)
import serial
import threading

"""
Реализация COM-порта средствами serial
"""
 
class Communicate(QObject):
    get_message = pyqtSignal()

class Input(QWidget):
    def __init__(self):
        self.ser = serial.Serial()
        self.name = ''
        super().__init__()
        self.end = False

        self.init_ui()

    def closeEvent(self, event):
        # закрытие порта
        self.end = True
        self.ser.close()

    def init_ui(self):
        # Окно для работы с портом

        # Отправить сообщение
        self.btn = QPushButton('Send', self)
        self.btn.move(20, 33)
        self.btn.clicked.connect(self.send)

        self.le_input = QTextEdit(self)
        self.le_input.move(130, 22)
        self.le_input.setFixedHeight(50)
        self.le_input.setFixedWidth(450)
        # self.le_input.setPlainText('asdasdasd')

        # поле входящих сообщений
        self.le_output = QTextBrowser(self)
        self.le_output.move(130, 80)
        self.le_output.setFixedHeight(50)
        self.le_output.setFixedWidth(450)

        self.signal = Communicate()
        self.signal.get_message.connect(self.set_text)
        # self.le_output.setDisabled(True)
        # self.le_output.

        self.lab_out = QLabel('Output is here', self)
        self.lab_out.move(28, 95)

        # настройки
        self.lab_settings = QLabel('Settings', self)
        self.lab_settings.move(275, 170)

        self.line = QFrame(self)
        self.line.setObjectName('line')
        self.line.setGeometry(10, 127, 580, 127)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        # byte
        self.btn_byte = QPushButton('Byte size', self)
        self.btn_byte.move(20, 220)
        self.btn_byte.clicked.connect(self.change_byte_size)

        self.box_byte = QComboBox(self)
        self.box_byte.setObjectName('Byte size')
        self.box_byte.setFixedWidth(92)
        self.box_byte.addItems([' 5 ', ' 6 ', ' 7 ', ' 8 '])
        self.box_byte.move(20, 270)

        # speed
        self.btn_speed = QPushButton('Baudrate', self)
        self.btn_speed.move(167, 220)
        self.btn_speed.clicked.connect(self.change_baudrate)

        self.box_speed = QComboBox(self)
        self.box_speed.setFixedWidth(92)
        self.box_speed.setObjectName('Baudrate')
        self.box_speed.addItems(['50', '75', '110', '134', '150', '200', '300', '600', '1200', '1800', '2400',
                                 '4800', '9600', '19200', '38400', '57600', '115200'])
        self.box_speed.move(167, 270)

        # stop bits
        self.btn_stop_bits = QPushButton('Stop bits num', self)
        self.btn_stop_bits.move(314, 220)
        self.btn_stop_bits.clicked.connect(self.change_stop_bits)

        self.box_stop_bits = QComboBox(self)
        self.box_stop_bits.setFixedWidth(92)
        self.box_stop_bits.setObjectName('Stop bits')
        self.box_stop_bits.addItems([' 1 ', ' 1.5 ', ' 2 '])
        self.box_stop_bits.move(314, 270)

        # parity
        self.btn_parity = QPushButton('Parity', self)
        self.btn_parity.move(480, 220)
        self.btn_parity.clicked.connect(self.change_parity)

        self.box_parity = QComboBox(self)
        self.box_parity.setFixedWidth(92)
        self.box_parity.setObjectName('Parity')
        self.box_parity.addItems([' None ', ' Odd ', ' Even '])
        self.box_parity.move(480, 270)

        # close port
        self.btn_close = QPushButton('Close port', self)
        self.btn_close.move(167, 320)
        self.btn_close.setFixedWidth(239)
        self.btn_close.clicked.connect(self.close_port)

        # end settings line
        # self.line_end = QFrame(self)
        # self.line_end.setObjectName('line2')
        # self.line_end.setGeometry(10, 255, 580, 255)
        # self.line_end.setFrameShape(QFrame.HLine)
        # self.line_end.setFrameShadow(QFrame.Sunken)

        # open name
        self.btn_name = QPushButton('Open port', self)
        self.btn_name.move(20, 370)
        self.btn_name.clicked.connect(self.change_name)

        self.le_name = QLineEdit(self)
        self.le_name.move(130, 373)
        self.le_name.setFixedWidth(442)
        self.le_name.setPlaceholderText('Input port name')

        self.setGeometry(300, 300, 600, 420)
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


        #dialog.setGeometry(350, 350, 250, 100)
        dialog.show()

    def send(self):
        # функция отправки сообщения
        if not self.ser.is_open:
            self.show_dialog('You need to open port!')
        else:
            try:
                text = self.le_input.toPlainText()
            except:
                self.show_dialog('You need to input text!')
            else:
                # print(text)
                # print('rts-', self.ser.rts)
                # print('cts-', self.ser.cts)
                # print('dtr-', self.ser.dtr)
                # print('dsr-', self.ser.dsr)
                self.ser.write(text.encode('utf-8'))
                self.ser.rts = False
                self.le_input.setText('')

    def change_byte_size(self):
        # функция изменения размера байта

        if not self.ser.is_open:
            self.ser.bytesize = int(self.box_byte.currentText())
        else:
            self.ser.close()
            self.ser.bytesize = int(self.box_byte.currentText())
            self.ser.open()

    def change_baudrate(self):
        # функция изменения скорости передачи
        if not self.ser.is_open:
            self.ser.baudrate = int(self.box_speed.currentText())
        else:
            self.ser.close()
            self.ser.baudrate = int(self.box_speed.currentText())
            self.ser.open()

    def change_stop_bits(self):
        # функция изменения числа стоп-битов
        d = {'1': serial.STOPBITS_ONE, '2': serial.STOPBITS_TWO, '1.5': serial.STOPBITS_ONE_POINT_FIVE}
        if not self.ser.is_open:
            self.ser.stopbits = d[self.box_stop_bits.currentText()[1:-1]]
        else:
            self.ser.close()
            self.ser.stopbits = d[self.box_stop_bits.currentText()[1:-1]]
            self.ser.open()

    def change_parity(self):
        # функция изменения контроля четности
        d = {'e': serial.PARITY_EVEN, 'o': serial.PARITY_ODD, 'n': serial.PARITY_NONE}
        if not self.ser.is_open:
            self.ser.parity = d[self.box_parity.currentText()[1].lower()]
        else:
            self.ser.close()
            self.ser.parity = d[self.box_parity.currentText()[1].lower()]
            self.ser.open()

    def change_name(self):
        try:
            text = self.le_name.text()
        except:
            self.show_dialog('You need to input port name!')
        else:
            try:
                if not self.ser.is_open: self.ser.close()
                self.ser = serial.Serial(port=text)
                self.name = text
                self.ser.rts = True
                self.ser.dtr = True
            except:
                self.show_dialog('Could not open port with name \"{}\"!'.format(text))

    def close_port(self):
        # закрыть порт
        self.ser.rts = True
        self.ser.dtr = True
        self.ser.close()

    def get_text(self):
        # функция приема сообщений
        while True:
            try:
                if self.end is True:
                    break
                if self.ser.is_open:
                    if not self.ser.cts and self.ser.dsr and self.ser.dtr:
                        self.signal.get_message.emit()
                        self.ser.dtr = False
                    if not self.ser.dsr:
                        self.ser.rts = True
                    if not self.ser.dtr and self.ser.rts:
                        self.ser.dtr = True
            except:
                print('problem with thread')

    def set_text(self):
        self.le_output.setPlainText(bytearray(self.ser.read(self.ser.in_waiting)).decode('utf-8'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Input()
    t = threading.Thread(target=ex.get_text)
    t.start()
    sys.exit(app.exec_())
