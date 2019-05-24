
from tkinter import *
from tkinter import font

class GenericFrame(Frame):
    class StatusBar(Frame):
        def __init__(self, frame, parent):
            parent.update()
            self.label = Label(frame, anchor=W, wraplength=parent.winfo_width()-1, justify=LEFT, bd=1, relief=FLAT)
            self.label.pack(side=LEFT, anchor=W, fill=X, expand=YES, pady=4)
            self.default_font = font.Font(font=self.label['font'])

        def set(self, format, *args):
            self.label.config(font=self.default_font, foreground="black", text=format % args)
            self.label.config(text=format % args)
            self.label.update_idletasks()

        def seterror(self, format, *args):
            self.boldify = font.Font(size=9,weight="bold")
            self.label.config(font=self.boldify, foreground="red", text=str(format) % args)
            self.label.update_idletasks()

        def setwarn(self, format, *args):
            self.boldify = font.Font(size=9,weight="bold")
            self.label.config(font=self.boldify, foreground="orange red4", text=str(format) % args)
            self.label.update_idletasks()

        def clear(self):
            self.label.config(text="")
            self.label.update_idletasks()




