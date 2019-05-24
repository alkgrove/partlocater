# -*- coding: utf-8 -*-

from tkinter import *
import platform
from configReader import *


class AboutApplication(Frame):
    FAVICON = "../assets/favicon.ico"
    LOGO = "../assets/logo.gif"
    LED_ON = "../assets/ledon.gif"
    LED_OFF = "../assets/ledoff.gif"

    def annoyingLED(self):
        if self.led_state:
            self.led.config(image=self.off)
            self.led_state = 0
        else:
            self.led.config(image=self.on)
            self.led_state = 1
        self.after(250, self.annoyingLED)

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("About Partlocater")
        self.parent.iconbitmap(self.FAVICON)

        self.pack()
        self.logo = PhotoImage(file=self.LOGO)
        self.on = PhotoImage(file=self.LED_ON)
        self.off = PhotoImage(file=self.LED_OFF)
        self.led_state = 0

        self.top_frame = Frame(self, background="white")
        self.top_frame.pack(side=TOP, fill=X, expand=YES)
        self.label = Label(self.top_frame, relief='flat', background='white', image=self.logo)
        self.label.pack(side=LEFT, fill=X, expand=YES, padx=4, pady=4)
        self.led = Label(self.top_frame, relief='flat', background='white', image=self.off)
        self.led.pack(side=RIGHT, padx=4, pady=4)
        
        self.frame = Frame(self, background="white")
        self.frame.pack(fill=X, expand=YES)
        self.text = Text(self.frame, relief='flat', wrap=WORD, width=64, height=16)
        self.text.pack(side=TOP, fill=X, expand=YES, padx=4, pady=4)
        self.text.tag_configure('title', font=('Segoe UI Semibold', 36, 'bold'), justify='center')
        self.text.tag_configure('author', font=('Segoe UI', 12, 'normal italic'), justify='center')
        self.text.tag_configure('copyright', font=('Segoe UI', 8, 'normal'), justify='center')
        self.text.tag_configure('plain', font=('Segoe UI', 10, 'normal'), justify='left')
        self.text.tag_configure('legal', font=('Segoe UI', 3, 'normal'), justify='left')
        
        self.text.insert(END, "Partlocater", 'title')
        self.text.insert(END, "\nby Alex Alkire & Bob Alkire", 'author')
        self.text.insert(END, "\nCopyright 2019, Alkgrove\n\n", 'copyright')
        self.text.insert(END, "Partlocater queries a Digi-Key part number for component parameters saving ", 'plain')
        self.text.insert(END, "that data in a Mariadb database. The parameter values can be modified ", 'plain')
        self.text.insert(END, "before they are written to the database.", 'plain')
        self.text.insert(END, "\nThis software is BSD-3-Clause license\n", 'plain')
        self.text.insert(END, "https://opensource.org/licenses/BSD-3-Clause\n", 'plain')
        self.text.insert(END,
                         "Legal is still complaining there the 3pt fonts are still legible. Add to buglist", 'legal')
        self.text.config(state=DISABLED)
        self.annoyingLED()


class SystemInfoApplication(Frame):        
    FAVICON = "../assets/favicon.ico"

    def __init__(self, parent=None, cfg=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.iconbitmap(self.FAVICON)
        self.parent.title("Partlocater - System Information")
        self.cfg = cfg
        self.pack()
        self.frame = Frame(self, background="white")
        self.frame.pack(fill=X, expand=YES)
        self.text = Text(self.frame, relief='flat', wrap=WORD, width=64, height=16)
        self.text.pack(side=TOP, fill=X, expand=YES, padx=4, pady=4)
        self.text.tag_configure('title', font=('Segoe UI Semibold', 12, 'bold'), justify='left')
        self.text.tag_configure('plain', font=('Segoe UI', 10, 'normal'), justify='left')
        self.text.insert(END, "System Information", 'title')
        self.text.insert(END, "\n\nPartlocater: Revision " + Config().REVISION, 'plain')
        self.text.insert(END, "\nLanguage: Python " + platform.python_version(), 'plain')
        self.text.insert(END, "\nOS: " + platform.uname()[0] + " " + platform.uname()[2], 'plain')
        self.text.insert(END, "\nProcessor: " + platform.processor(), 'plain')
        self.text.insert(END, "\nHostname: " + platform.node(), 'plain')
        self.text.insert(END, "\nCurrent Directory: " + os.getcwd(), 'plain')
        self.text.insert(END, "\nConfiguration File: " + self.cfg.cfg_filename, 'plain')
        if cfg.log_filename is not None:
            self.text.insert(END, "\nLog File: " + os.path.abspath(self.cfg.log_filename), 'plain')
        if self.cfg is not None and self.cfg.loaded_db is not None:
            self.text.insert(END, "\nDatabase Connector Version: " + self.cfg.loaded_db.get_connector_version(),
                             'plain')
            self.text.insert(END, "\nDatabase Version: " + self.cfg.loaded_db.get_database_version(), 'plain')
            tables, rows = self.cfg.loaded_db.get_count()
            self.text.insert(END, "\nDatabase Name: " + self.cfg.loaded_db.name + " (" + str(tables) + " Categories " +
                             str(rows) + " Total Entries)", 'plain')
            self.text.insert(END, "\nToken Database Name: " + self.cfg.loaded_metadb.name, 'plain')
            try:
                token_info = self.cfg.loaded_metadb.get_latest_token()
                expires = int(((token_info['timestamp'] + timedelta(seconds=int(token_info['expires_in'])))
                               - datetime.now()).total_seconds())
                hr = expires//3600
                minutes = int((expires - (hr * 3600))/60)
                if hr == 0:
                    if minutes == 0:
                        expired = "expired"
                    else:
                        expired = ""
                elif hr == 1:
                    expired = "1 hour"
                else:
                    expired = str(hr) + " hours"
                if minutes == 1:
                    expired += " 1 minute"
                else:
                    expired += " " + str(minutes) + " minutes"
                self.text.insert(END, "\nLast Token: " + token_info['timestamp'].ctime() +
                                 " Expires in " + expired, 'plain')
            except Exception as e:
                Config().log_write(e)


class HelpApplication(Frame):
    FAVICON = "../assets/favicon.ico"
    HELP = "../assets/help.txt"
       
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.tag_form = re.compile(r"^\.([a-z0-9]+)$")
        self.parent = parent
        self.parent.title("Partlocater - Help")
        self.parent.iconbitmap(self.FAVICON)

        self.pack(side=LEFT, fill=BOTH, expand=YES)
        self.frame = Frame(self, background="white")
        self.frame.pack(side=LEFT, fill=BOTH, expand=YES)
        self.text = Text(self.frame, relief='flat', wrap=WORD)
        self.text.pack(side=LEFT, fill=BOTH, expand=YES, padx=4, pady=4)
        self.scrollbar = Scrollbar(self.frame, orient='vertical', command=self.text.yview)
        self.scrollbar.pack(side=RIGHT, anchor=E, fill=Y, expand=YES)
        self.text.configure(yscroll=self.scrollbar.set)
        self.text.tag_configure('title', font=('Segoe UI Semibold', 16, 'bold'), justify='center')
        self.text.tag_configure('h1', font=('Segoe UI Semibold', 14, 'bold'), justify='left')
        self.text.tag_configure('h2', font=('Segoe UI Semibold', 12, 'bold'), justify='left')
        self.text.tag_configure('plain', font=('Segoe UI', 10, 'normal'), justify='left')
        self.text.tag_configure('indent', font=('Segoe UI', 10, 'normal'), justify='left', lmargin2=50)
        self.tag = 'plain'
        try:
            fp = open(self.HELP, "r")
            for lines in fp:
                tag = re.match(self.tag_form, lines)
                if tag is not None:
                    self.tag = tag.group(1)
                else:
                    self.text.insert(END, lines, self.tag)
            fp.close()
        except Exception as e:
            self.text.insert(END, str(e))
