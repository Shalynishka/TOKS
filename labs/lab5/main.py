from kivy.app import App
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from token_ring import Token, UI

from threading import Thread
from time import sleep

Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 450)
info = ['Input is here', 'Output is here', 'Debug is here', 'Destination address', 'Source address']
names = ['[ref=monitor]Monitor[/ref]', 'Station 1', 'Station 2']

st = [UI(i, i) for i in ['', '']]
st.insert(0, UI('', '', True))

t = Token('', '')


class Input(TextInput):

    def keyboard_on_key_down(self, window, key, text, modifiers):
        if key[1] == "backspace":
            print(self.text)
            st[int(self.id[-1])].d = st[int(self.id[-1])].d[-1] if len(st[int(self.id[-1])].d) > 1 else ''
        TextInput.keyboard_on_key_down(self, window, key, text, modifiers)

    def insert_text(self, substring, from_undo=False):
        st[int(self.id[-1])].d += substring
        return super(Input, self).insert_text(substring, from_undo=from_undo)


class LimInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        print(substring)
        if len(self.text) >= 3 or not substring.isdigit():
            substring = ''
        else:
            if int(self.text + substring) > 257:
                substring = ''
                self.text = str(256)
            if self.id[:-1] == 'sa':
                st[int(self.id[-1])].sa = chr(int(self.text+substring))
            else:
                st[int(self.id[-1])].da = chr(int(self.text+substring))
        return super(LimInput, self).insert_text(substring, from_undo=from_undo)


class TokenApp(App):
    inputs = []
    outputs = []
    debugs = []
    sa = []
    da = []
    go = False
    end = False

    def start(self, *a):
        if not self.go:
            self.go = True
            print('hello', a)
            self.th = Thread(target=self.loop)
            self.th.start()

    def loop(self):
        i = 0
        global t
        while True:
            self.debugs[i].text = '*'
            print(str(t))
            sleep(2)

            t, c = st[i].alg(t)
            if c:
                self.outputs[i].text += c
            if self.end is True:
                break

            self.debugs[i].text = ''
            i += 1
            if i == 3:
                i = 0

    def stop(self, *largs):
        self.end = True

    def build(self):
            b = BoxLayout(spacing=10, padding=10)
            name_l = [Label(size_hint=(None, None), height='20dp', width='230dp') for i in range(3)]
            name_l[0].markup = True
            name_l[0].bind(on_ref_press=self.start)
            boxes = [BoxLayout(spacing=10, padding=10, orientation='vertical') for i in range(3)]
            self.inputs = [Input(id='i'+str(i)) for i in range(3)]
            self.outputs = [TextInput(size_hint_y=.5, is_focusable=False, id='o'+str(i)) for i in range(3)]
            self.debugs = [TextInput(size_hint_y=.5, disabled=True, is_focusable=False, id='d'+str(i)) for i in range(3)]
            sa_box = [GridLayout(cols=2, size_hint_y=.4, padding=4) for i in range(3)]
            da_box = [GridLayout(cols=2, size_hint_y=.4, padding=4) for i in range(3)]
            self.sa = [LimInput(size_hint=(.4, None), height='30dp', id='sa'+str(i)) for i in range(3)]
            self.da = [LimInput(size_hint=(.4, None), height='30dp', id='da' + str(i)) for i in range(3)]
            wind = [self.inputs, self.outputs, self.debugs, self.da, self.sa]
            for i in range(3):
                name_l[i].text = names[i]
                boxes[i].add_widget(name_l[i])
                for x in range(3):
                    lab = Label(size_hint=(None, None), height='20dp', width='90dp')
                    lab.text = info[x]
                    boxes[i].add_widget(lab)
                    boxes[i].add_widget(wind[x][i])
                da_box[i].add_widget(Label(size_hint_x=.6,  text=info[3]))
                da_box[i].add_widget(self.da[i])
                boxes[i].add_widget(da_box[i])
                sa_box[i].add_widget(Label(size_hint_x=.6, text=info[4]))
                sa_box[i].add_widget(self.sa[i])
                boxes[i].add_widget(sa_box[i])
                b.add_widget(boxes[i])
            return b


if __name__ == '__main__':
    TokenApp().run()
