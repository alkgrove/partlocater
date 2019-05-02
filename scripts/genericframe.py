
from tkinter import *
from tkinter import font

class GenericFrame(Frame):
    class StatusBar(Frame):
        def __init__(self, frame, parent):
            parent.update()
            self.label = Label(frame, anchor=W, wraplength=parent.winfo_width()-1, justify=LEFT, bd=1, relief=FLAT)
            self.label.pack(side=LEFT, anchor=W, fill=X, expand=YES, pady=4)
            self.defaultfont = font.Font(font=self.label['font'])

        def set(self, format, *args):
            self.label.config(font=self.defaultfont, foreground="black", text=format % args)
            self.label.config(text=format % args)
            self.label.update_idletasks()

        def seterror(self, format, *args):
            self.boldify = font.Font(size=9,weight="bold")
            self.label.config(font=self.boldify, foreground="red", text=str(format) % args)
            self.label.update_idletasks()

        def clear(self):
            self.label.config(text="")
            self.label.update_idletasks()
