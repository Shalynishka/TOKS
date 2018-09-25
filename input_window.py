﻿import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QApplication, QLabel, QDialog, QGridLayout, QFrame, QTextEdit, QTextBrowser, QComboBox, QCheckBox)
from PyQt5.QtCore import (QObject, pyqtSignal)
import serial
import threading

# """
# Реализация COM-порта средствами serial
# """
# TODO Реализовать байт-стаффинг( на адресах отдельно, чтобы делать меньше мороки при формировании сообщений)
# TODO Формирование пакетов: хедер сформировать сразу, в него вставлять данные. По 7 байт чистой информации??
# TODO Второй поток-писатель? Пакеты из листа все равно отправлять надо по одному. Организовать ожидание обработки и приема

class Communicate(QObject):
    """
    Класс для создания своего сигнала о пришедшем сообщении
    """
    get_message = pyqtSignal()


class Input(QWidget):
    """
    Класс главного окна
    """
    def __init__(self):
        """Конструктор окна"""
        self.ser = serial.Serial()
        super().__init__()
        # End Flag
        self.end = False

        # Destination address
        self.d_address = chr(0)
        # Source address
        self.s_address = chr(0)

        self.start_flag = chr(0b10000001)
        self.fcs = chr(0b10101010)

        self.esc = chr(0b10000010)
        self.init_ui()

    def closeEvent(self, event):
        """Закрыть порт при закрытии приложения"""
        # закрытие порта
        self.end = True
        self.ser.close()

    def init_ui(self):
        """Окно для работы с портом
            Атрибуты:
                btn             кнопка отправки сообщения
                le_input        окно ввода сообщения

                le_output       окно выводящихся сообщений
                signal          сигнал пришедших сообщений
                lab_out         метка выводящихся сообщений

                lab_settings    метка настроек
                line            линия-разделитель

                btn_byte        кнопка смены размера байта
                box_byte        бокс выбора размеров байта

                btn_speed       кнопка смены размера скорости
                box_speed       бокс выбора значений скорости

                btn_stop_bits   кнопка смены стоп битов
                box_stop_bits   бокс выбора размеров стоп бита

                btn_parity      кнопка смены четности
                box_parity      бокс выбора четности

                btn_name        кнопка смены имени порта
                le_name         поле ввода имени
        """

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

        # end settings line
        # self.line_end = QFrame(self)
        # self.line_end.setObjectName('line2')
        # self.line_end.setGeometry(10, 255, 580, 255)
        # self.line_end.setFrameShape(QFrame.HLine)
        # self.line_end.setFrameShadow(QFrame.Sunken)

        # Destination address
        self.btn_d_address = QPushButton('Destination address', self)
        self.btn_d_address.move(20, 420)
        self.btn_d_address.clicked.connect(self.change_destination_address)

        self.le_d_address = QLineEdit(self)
        self.le_d_address.move(167, 423)
        self.le_d_address.setPlaceholderText('Destination address')
        self.le_d_address.setMaxLength(8)

        # Source address
        self.btn_s_address = QPushButton('Source address', self)
        self.btn_s_address.move(20, 470)
        self.btn_s_address.setFixedSize(121, 27)
        self.btn_s_address.clicked.connect(self.change_source_address)

        self.le_s_address = QLineEdit(self)
        self.le_s_address.move(167, 473)
        self.le_s_address.setPlaceholderText('Source address')
        self.le_s_address.setMaxLength(8)

        # Generate error
        self.lab_error = QLabel("To generate error", self)
        self.lab_error.move(370, 423)
        self.cbox_error = QCheckBox(self)
        self.cbox_error.move(500, 423)

        # Debug
        self.lab_debug = QLabel("Debug is here", self)
        self.lab_debug.move(20, 535)

        self.le_debug = QTextBrowser(self)
        self.le_debug.move(130, 520)
        self.le_debug.setFixedHeight(50)
        self.le_debug.setFixedWidth(450)

        self.setGeometry(300, 300, 600, 620)
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
        """Функция отправки сообщения"""
        if not self.ser.is_open:
            self.show_dialog('You need to open port!')
        else:
            try:
                text = self.le_input.toPlainText()
            except:
                self.show_dialog('You need to input text!')
            else:

                self.ser.write(text.encode('utf-8'))
                self.ser.rts = False
                self.le_input.setText('')

    def make_package(self, text):
        """ Функция формирования пакетов"""
        packs = []
        x = 0

        while x < len(text):
            data = ''
            for c in text[x:x + 7]:
                if c == self.start_flag:
                    data += self.esc + chr(ord(c) + 1)
                elif c == self.esc:
                    data += self.esc + chr(ord(c) + 1)
                else:
                    data += str(c)
            if data != '':
                packs.append(self.start_flag + self.d_address + self.s_address + data)
            x += 7
            if self.cbox_error.isTristate():
                packs[-1] += 'a'
            else:
                packs[-1] += self.fcs
        return packs

    def open_package(self, text):
        i = 0
        mes = ''
        while i < len(text):
            if text[i] == self.esc:
                c = chr(ord(text[i + 1]) - 1)
                print(c)
                mes += c
                i += 1
            else:
                mes += text[i]
            i += 1
        if mes[0] != self.start_flag:       # не флаг старта
            return ''
        elif mes[1] != self.s_address:        # не нам посылка
            return ''
        elif mes[-1] != self.fcs:             # ошибка флага контроля
            return ''
        else:
            return mes[3:-1]
        
    def change_byte_size(self):
        """функция изменения размера байта"""

        if not self.ser.is_open:
            self.ser.bytesize = int(self.box_byte.currentText())
        else:
            self.ser.close()
            self.ser.bytesize = int(self.box_byte.currentText())
            self.ser.open()

    def change_baudrate(self):
        """функция изменения скорости передачи"""
        if not self.ser.is_open:
            self.ser.baudrate = int(self.box_speed.currentText())
        else:
            self.ser.close()
            self.ser.baudrate = int(self.box_speed.currentText())
            self.ser.open()

    def change_stop_bits(self):
        """функция изменения числа стоп-битов"""
        d = {'1': serial.STOPBITS_ONE, '2': serial.STOPBITS_TWO, '1.5': serial.STOPBITS_ONE_POINT_FIVE}
        if not self.ser.is_open:
            self.ser.stopbits = d[self.box_stop_bits.currentText()[1:-1]]
        else:
            self.ser.close()
            self.ser.stopbits = d[self.box_stop_bits.currentText()[1:-1]]
            self.ser.open()

    def change_parity(self):
        """Функция изменения контроля четности"""
        d = {'e': serial.PARITY_EVEN, 'o': serial.PARITY_ODD, 'n': serial.PARITY_NONE}
        if not self.ser.is_open:
            self.ser.parity = d[self.box_parity.currentText()[1].lower()]
        else:
            self.ser.close()
            self.ser.parity = d[self.box_parity.currentText()[1].lower()]
            self.ser.open()

    def change_name(self):
        """Функция смены порта"""
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
        """Функция закрытия порта"""
        self.ser.rts = True
        self.ser.dtr = True
        self.ser.close()

    def get_address(self, adress):
        """ Функция преобразования символов в байт"""
        a = 0
        i = 0
        l = list(adress)
        l.reverse()
        for x in l:
            if x != '1' and x != '0':
                  self.show_dialog('You can use only \'1\' and \'0\' to set new adress!')
                  break
            a += int(x) * 2**i
            i += 1
        else:
            return a
        return 0

    def change_destination_address(self):
        # если адрес будет равен esc символу или флагу начала, создать строку из esc-символа и символа
        # код которого на 1 больше необходимого
        try:
            self.d_address = chr(self.get_address(self.le_d_address.text())) # .encode('utf-8')
            if self.d_address == self.start_flag or self.d_address == self.esc:
                self.d_address = self.esc + chr(ord(self.d_address) + 1)
        except:
            self.show_dialog('You need to input destination address!')
        # else:
        #     print(self.d_address)

    def change_source_address(self):
        # если адрес будет равен esc символу или флагу начала, создать строку из esc-символа и символа
        # код которого на 1 больше необходимого
        try:
            self.s_address = chr(self.get_address(self.le_s_address.text()))
            if self.s_address == self.start_flag or self.s_address == self.esc:
                self.s_address = self.esc + chr(ord(self.s_address) + 1)
        except:
            self.show_dialog('You need to input source address!')
        # else:
        #     print(self.s_address)

    def get_text(self):
        """Функция приема сообщений"""
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
        """Установка текста"""
        self.le_output.setPlainText(bytearray(self.ser.read(self.ser.in_waiting)).decode('utf-8'))


if __name__ != '__main__':
    app = QApplication(sys.argv)
    ex = Input()
    t = threading.Thread(target=ex.get_text)
    t.start()
    sys.exit(app.exec_())



# print(ord(esc) >> 4)
# second = 0b00001111 & ord(start_flag)
# print(second)
#
# print((ord(esc)), (second))
#
# first_answer = 0b11110000 & ord(esc)
# sec_an = 0b00001111 & second
# print(first_answer + sec_an)

# address = chr(0b10000001)
# print('address: ', (address))
# if address == start_flag:
#     print('dd')
#     address = esc + chr(0b00001111 & ord(start_flag))
# if address == esc:
#     address = esc + chr(0b00001111 & ord(esc))
#
# print('address: ', (address))
# print(type(address), len(address))
# print(type(esc))
#
# print('here: ', chr(ord(address[0]) & 0b11110000 + ord(address[1]) & 0b00001111))
#



# start_flag = chr(0b10000001)
# start_flag = '1'
# fcs = chr(0b10101010)
#
# # esc = chr(0b00000010) # 1000 0010
# esc = '2' # 1000 0010
# print(esc)
#
# s = '1234567123456712345'
# l = []
# x = 0
# while x < len(s):
#     data = ''
#     for c in s[x:x+7]:
#         if c == start_flag:
#             data += esc + chr(ord(c) + 1)
#         elif c == esc:
#             data += esc + chr(ord(c) + 1)
#         else:
#             data += str(c)
#     if data != '':
#         l.append(data)
#     x += 7
# print(l)
# mes = ''
# for x in l:
#
#     i = 0
#     while i < len(x):
#         if x[i] == esc:
#             c = chr(ord(x[i + 1]) - 1)
#             print(c)
#             mes += c
#             i += 1
#         else:
#             mes += x[i]
#         i += 1
#
# print(mes)
# start_flag = chr(0b10000001)
# fcs = chr(0b10101010)
# esc = chr(0b10000010)