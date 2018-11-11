class Token:
    data = ''

    def __init__(self, da, sa):
        self.s = 'T'
        self.da = da
        self.sa = sa
        self.r = 'N'
        self.m = '0'

    def __str__(self):
        return 'sign:' + self.s + ' destination: ' + self.da + ' source: ' + self.sa + ' recognize: '\
                + self.r + ' monitor: ' + self.m + ' data: ' + self.data

    def sc(self):
        self.s = 'F' if self.s == 'T' else 'T'

    def da(self, a):
        self.da = a

    def sa(self, a):
        self.sa = a

    def rc(self):
        self.r = 'Y'

    def mc(self):
        self.m = 'M'

    def d(self, d):
        self.data = d[0]
        return d[1:]


class UI:
    data = '' # to send!

    def __init__(self, sa, da, m=False):
        self.da = da
        self.sa = sa
        self.mon = m

    @property
    def d(self):
        return self.data

    @d.setter
    def d(self, d):
        self.data = d

    def make_frame(self):
        t = Token(self.da, self.sa) # заполняем адресса
        t.sc()                       # маркер теперь кадр
        self.data = t.d(self.data)  # выдаем данные
        return t

    def alg(self, t):   # Алгоритм
        c = None
        if t.s == 'T':     # Если принят маркер
            if self.data:             # Если принят маркер и есть данные
                t = self.make_frame()
        # принят маркер, а данных нет. Толкнуть его дальше
        else:                             # принят кадр
            if self.mon:
                if t.m == '0':         # проводим проверку на монитор
                    t.mc()
                else:                  # проводим починку кольца
                    if self.data:               # если монитор-станция имеет данные к отправке - отправим
                        t = self.make_frame()
                    else:
                        t = Token('', '')       # нет данных, пускаем токен
                    return t, c        # остальные if не проверяются
            if self.sa == t.da:           # кадр нам
                c = t.data          # забираем данные
                t.rc()               # выставляем RECOGNIZED
            elif self.sa == t.sa:     # кадр наш
                if t.r == 'Y':       # наши данные дошли
                    if self.data:                   # если у нас есть еще данные - загружаем кадр и толкаем дальше
                        t = self.make_frame()       # выдаем данные
                    else:                           # иначе освободим маркер
                        t = Token('', '')
                # если данные не дошли, то ничего не делаем, т.е., толкаем дальше

        return t, c
