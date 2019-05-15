
from tkinter import *
from tkinter import font
from tkinter.ttk import OptionMenu
from configReader import *
from partdb import *

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

class ManualAddApplication(Frame):
    FAVICON = "../assets/favicon.ico"
    PROPLIST = ['Category', 'Manufacturer', 'Manufacturer Part Number', 
        'Supplier 1', 'Supplier Part Number 1', 'Description', 'Footprint Ref', 
        'Library Ref']
    CATEGORY_INDEX = 0
    SPN_INDEX = 4
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("Partlocater - Manual Add")

        self.parent.iconbitmap(self.FAVICON)
         
        self.manualframe = LabelFrame(self, text="Add Component")
        self.manualframe.pack(side=TOP, fill=BOTH, expand=YES, pady=4, padx=4)
        self.propframe = []
        self.propvalue = []
        self.PROPLIST += Config().include
        for item in self.PROPLIST:
            self.propframe.append(Frame(self.manualframe))
            self.propframe[-1].pack(side=TOP, fill=X, expand=YES)
            proplabel = Label(self.propframe[-1], anchor=E, text=item, width=20)
            proplabel.pack(side=LEFT, anchor=E, fill=X, expand=YES, pady=4)
            self.propvalue.append(StringVar())
            if item != "Category":
                propentry = Entry(self.propframe[-1], textvariable=self.propvalue[-1], state=NORMAL, width=30)
                propentry.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=4)
            else:
                self.catentry = Entry(self.propframe[-1], textvariable=self.propvalue[-1], state=DISABLED, width=40)
                self.catentry.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=4)
                self.catoption = StringVar()
                catmenu = OptionMenu(self.propframe[-1], self.catoption, *Config().tables, command=self.on_category)
                catmenu.pack(side=TOP, anchor=N, fill=X, expand=YES)


        self.buttonframe = Frame(self.manualframe)
        self.buttonframe.pack(side=TOP, fill=X, expand=NO)
        self.clearButton = Button(self.buttonframe, text="Clear", command=self.do_clear, state=ACTIVE, width=8)
        self.clearButton.pack(side=RIGHT, anchor=W, fill=X, expand=NO)
        self.commitButton = Button(self.buttonframe, text="Add", command=self.do_commit, state=ACTIVE, width=8)
        self.commitButton.pack(side=RIGHT, anchor=W, fill=X, expand=NO)

        self.pack(side=LEFT, fill=BOTH, expand=YES)

    def do_clear(self):
        for i in range(len(self.PROPLIST)):
            if i != self.CATEGORY_INDEX:
                self.propvalue[i].set("")
        
    def get_part(self):
        part = {}
        for i in range(len(self.PROPLIST)):
            str = self.propvalue[i].get()
            if str:
                if not validate(str):
                    raise self.PROPLIST[i] + " not valid"
                part[self.PROPLIST[i]] = str
        if 'Supplier Part Number 1' not in part:
            raise "Supplier Part Number must be defined"
        return part
 
        
    def do_commit(self):
        try:
            part = self.get_part()
        except Exception as e:
            Config().log_write(e)
            Config().status.seterror(e)
            return
        if "Category" not in part:
            Config().status.seterror("Category Not Defined")
            return
        table = part["Category"]
        part["Category"] = table.capitalize()
        Config().insert_part(table, part)
        if Config().status is not None:
            Config().status.set("Part %s added to database"%part['Supplier Part Number 1'])
        
            
    def on_category(self, value):
        self.catentry.config(state=NORMAL)
        self.propvalue[self.CATEGORY_INDEX].set(value)
        self.catentry.config(state=DISABLED)
