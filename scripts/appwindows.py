
from tkinter import *
from tkinter import ttk, messagebox
import tkinter.font
from configReader import *
from genericframe import *
from tkinter.ttk import Treeview, Scrollbar, OptionMenu, Button
import time
import sys


class SearchApplication(GenericFrame):
    FAVICON = "../assets/favicon.ico"
    def __init__(self, parent=None, dbwindow=None):
        self.lastValue = None
        self.categoryOption = StringVar("")
        self.columnid = [ 'ProductDescription', 'ManufacturerName', 'ManufacturerPartNumber', 'DigiKeyPartNumber', 'Category' ]
        Frame.__init__(self, parent)
        self.pack()
        self.parent = parent
        self.dbwindow = dbwindow
        self.current_selection = None

        self.parent.title("Partlocater - Advanced Database Search")
        self.parent.iconbitmap(self.FAVICON)
        self.winframe = Frame(self)
        self.winframe.pack(side=TOP, fill=BOTH, expand=YES)
        self.searchLF = LabelFrame(self.winframe, text="Search")
        self.searchLF.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=6)
        self.searchLeftF = Frame(self.searchLF)
        self.searchLeftF.pack(side=LEFT, anchor=W)
        self.searchRightF = Frame(self.searchLF)
        self.searchRightF.pack(side=LEFT, anchor=N)

        self.catF = Frame(self.searchLeftF)
        self.catF.pack(side=TOP, anchor=W)
        self.catL = Label(self.catF, text='Category', width=22, anchor=W, justify=LEFT)
        self.catL.pack(side=LEFT, fill=X, expand=YES)
        self.cat = StringVar()
        self.catE = Entry(self.catF, textvariable=self.cat, width=50, state=DISABLED)
        self.catE.config(disabledbackground=self.catE.cget("bg"))
        self.catE.config(disabledforeground=self.catE.cget("fg"))
        self.catE.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.categoryOption = StringVar()
        self.cat.set("All")
        optionlist = ['All', 'All'] + Config().tables
        self.catM = OptionMenu(self.searchRightF, self.categoryOption, *optionlist, command=self.on_category)
        self.catM.pack(side=TOP, anchor=N, fill=X, expand=YES)

        self.manF = Frame(self.searchLeftF)
        self.manF.pack(side=TOP, anchor=W)
        self.manL = Label(self.manF, text='ManufacturerName', width=22, anchor=W, justify=LEFT)
        self.manL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.man = StringVar()
        self.manE = Entry(self.manF, width=50, textvariable=self.man)
        self.manE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.mpnF = Frame(self.searchLeftF)
        self.mpnF.pack(side=TOP, anchor=W)
        self.mpnL = Label(self.mpnF, text='ManufacturerPartNumber', width=22, anchor=W, justify=LEFT)
        self.mpnL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.mpn = StringVar()
        self.mpnE = Entry(self.mpnF, width=50, textvariable=self.mpn)
        self.mpnE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.spnF = Frame(self.searchLeftF)
        self.spnF.pack(side=TOP, anchor=W)
        self.spnL = Label(self.spnF, text='DigiKeyPartNumber', width=22, anchor=W, justify=LEFT)
        self.spnL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.spn = StringVar()
        self.spnE = Entry(self.spnF, width=50, textvariable=self.spn)
        self.spnE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.descF = Frame(self.searchLeftF)
        self.descF.pack(side=TOP, anchor=W)
        self.descL = Label(self.descF, text='ProductDescription', width=22, anchor=W, justify=LEFT)
        self.descL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.desc = StringVar()
        self.descE = Entry(self.descF, width=50, textvariable=self.desc)
        self.descE.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.descE.focus_force()

        self.findF = Frame(self.searchLeftF)
        self.findF.pack(side=TOP, anchor=E)
        self.findB = ttk.Button(self.findF, text="Find", width=6, command=lambda event=None: self.do_find(event))
        self.parent.bind("<Return>", self.do_find)
        self.findB.pack(side=LEFT, pady=4)
        self.clearB = ttk.Button(self.findF, text="Clear", width=6, command=self.on_clear_search)
        self.clearB.pack(side=LEFT, pady=4)

        self.partsLF = LabelFrame(self, text="Found Components")
        self.partsLF.pack(side=TOP, fill=X, expand=YES, pady=4, padx=6)
        self.partsF = Frame(self.partsLF);
        self.partsF.pack(side=TOP)
        self.partsTV = Treeview(self.partsF, selectmode=BROWSE, show='tree headings', columns=(self.columnid))
        self.partsTV.bind('<<TreeviewSelect>>', self.on_select_new_field)
        self.partsTV.bind('<Control-c>', self.on_copy_element)
        self.partsTV.column("#0", minwidth=0,width=18, stretch=NO)
        for t in self.columnid:
            self.partsTV.heading(t, text=Config().parameter[t])
        self.partsTV.column('Category', width=60)
        self.scrollbar = Scrollbar(self.partsF, orient='vertical', command=self.partsTV.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.partsTV.configure(yscroll=self.scrollbar.set)
        self.scrollbar.config(command=self.partsTV.yview)
        self.partsTV.pack(side=TOP, anchor=W, fill=X, expand=YES)
        self.partsTV.delete(*self.partsTV.get_children())

        self.partButtonF = Frame(self.partsLF)
        self.deletePartB = ttk.Button(self.partsLF, text="Delete Part from Database", command=self.on_delete, state=DISABLED)
        self.deletePartB.pack(side=RIGHT, anchor=W, expand=NO, pady=4, padx=6)
        self.partsB = ttk.Button(self.partsLF, text="Copy Selected To Part Find", command=self.on_copy, state=DISABLED)
        self.partsB.pack(side=RIGHT, anchor=W, expand=NO, pady=4, padx=6)
        self.partButtonF.pack(side=BOTTOM)
        
        self.element_labelframe = LabelFrame(self, text="Modify Name/Value")
        self.element_labelframe.pack(side=TOP, fill=X, expand=YES, pady=4, padx=6)
        self.element_frame = Frame(self.element_labelframe);
        self.element_frame.pack(side=TOP)

        self.element_name = StringVar()
        self.element_label = Label(self.element_frame, textvariable=self.element_name, width=30, anchor=W, justify=LEFT)
        self.element_label.pack(side=LEFT, anchor=W, fill=X, expand=YES, pady=4)
        self.element_value = StringVar()
        self.element_entry = Entry(self.element_frame, width=50, textvariable=self.element_value)
        self.element_entry.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.default_color = self.element_entry.cget('background')

        self.element_update = ttk.Button(self.element_frame, text="Update", command=self.on_update_element, state=DISABLED)
        self.element_update.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.element_cancel = ttk.Button(self.element_frame, text="Cancel", command=self.on_clear_element, state=DISABLED)
        self.element_cancel.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.statusLF = LabelFrame(self, text="Status")
        self.statusLF.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.statusF = Frame(self.statusLF);
        self.statusF.pack(side=TOP, fill=X, expand=YES, padx=6)
        self.status = self.StatusBar(self.statusF, self)

    def on_find(self):
        category = self.cat.get()
        searchlist = []
        collist = []
        searchstr = self.man.get()
        if not (validate(searchstr)):
            raise Exception("Invalid Manufacture Name")
        searchlist.append(searchstr)
        collist.append(Config().parameter['ManufacturerName'])
        searchstr = self.mpn.get()
        if not (validate(searchstr)):
            raise Exception("Invalid Manufacture Part Number")
        searchlist.append(searchstr)
        collist.append(Config().parameter['ManufacturerPartNumber'])
        searchstr = self.spn.get()
        if not (validate(searchstr)):
            raise Exception("Invalid Supplier Part Number")
        searchlist.append(searchstr)
        collist.append(Config().parameter['DigiKeyPartNumber'])
        searchstr = self.desc.get().split()
        if not (validate(searchstr)):
            raise Exception("Invalid Description")
        searchlist += searchstr
        collist.append(Config().parameter['ProductDescription'])
        select = "SELECT * FROM `" + Config().loaded_db.name + "`."
        where = "WHERE"
        like = ""
        i = 0
        for item in searchlist:
            if len(item) > 0:
                item = item.replace('%', '\%')
                item = item.replace('"', '')
                item = item.replace("'", "")
                if (i < 3):
                    like += where + " `" + collist[i] + "` LIKE '" + item + "%'"
                else:
                    like += where + " (`" + collist[i] + "` LIKE '" + item + "%' OR `" + collist[i] + "` LIKE '% " + item + "%')"
                where = " AND"
            i = i + 1 if (i < 3) else i
        self.partsTV.delete(*self.partsTV.get_children())
        count = 0
        if (category == "All"):
            result = []
            for table in Config().tables:
                qry = select + "`" + table + "` " + like
                result = Config().loaded_db.query(qry)
                for record in result:
                    v = []
                    spn = record[Config().parameter['DigiKeyPartNumber']]
                    count += 1
                    for id in self.columnid:
                        if (id == 'Category'):
                            v.append(table)
                        else:
                            v.append(record[Config().parameter[id]])
                    id = self.partsTV.insert('', 'end', iid=spn, text=spn, values=(v))
                    for params in record:
                        if record[params] is not None:
                            self.partsTV.insert(id, 'end', text=spn, values=(params,record[params]))
        else:
            qry = select + "`" + category + "` " + like
            result = Config().loaded_db.query(qry)
            for record in result:
                v = []
                count += 1
                spn = record[Config().parameter['DigiKeyPartNumber']]
                for id in self.columnid:
                    if (id == 'Category'):
                        v.append(category)
                    else:
                        v.append(record[Config().parameter[id]])
                id = self.partsTV.insert('', 'end', iid=spn, text=spn, values=(v))
                for params in record:
                    if record[params] is not None:
                        self.partsTV.insert(id, 'end', text=spn, values=(params,record[params]))
        self.status.set(("No" if count == 0 else str(count)) + " items found")

    def on_update_element(self):
        if self.current_selection is None:
            return
        item_name = self.partsTV.item(self.current_selection, "text")
        key = self.element_name.get()
        if (len(key) > 0):
            value = self.element_value.get()
            if not validate(value):
                self.status.seterror("Invalid value, must not have quotes")
                return
            element_parent = self.partsTV.parent(self.current_selection)
            tablename = self.partsTV.item(element_parent,"values")[self.columnid.index('Category')]
            partnumber = self.partsTV.item(element_parent,"values")[self.columnid.index('DigiKeyPartNumber')]
            setparam = "SET `" + key + "` = '" + value + "' "
            where = "WHERE `" + Config().parameter['DigiKeyPartNumber'] + "` = '" + partnumber + "'"
            qry = "UPDATE `" + Config().loaded_db.name + "`.`" + tablename + "` " + setparam + where
            try:
                Config().loaded_db.query(qry)
            except Exception as e:
                self.status.seterror("Database query failed: %s", e)
                return
            self.status.set("Changed " + key + " to " + value + " for part " + partnumber + ".")
            self.partsTV.set(self.current_selection,"#2",value)
            self.element_update.config(state=DISABLED)

    def on_clear_element(self):
        self.current_selection = None
        self.element_name.set("")
        self.element_value.set("")

    def on_clear_search(self):
        self.man.set("")
        self.mpn.set("")
        self.spn.set("")
        self.desc.set("")
        self.cat.set("All")
        self.categoryOption.set("All")
        self.partsTV.delete(*self.partsTV.get_children())
    
    def do_flash(self):
        current_color = self.element_entry.cget("background")
        if (current_color == self.default_color):
            self.element_entry.config(background="red")
        else:
            self.element_entry.config(background=self.default_color)
            return
        self.after(250, self.do_flash)

    def on_category(self, value):
        self.catE.config(state=NORMAL)
        self.cat.set(value)
        self.catE.config(state=DISABLED)

    def on_copy(self):
        selected = self.partsTV.selection()[0]
        key = self.partsTV.item(selected, "values")[self.columnid.index('DigiKeyPartNumber')]
        self.dbwindow.part_num_string.set(key)
        self.status.set("Part Number '" + key + "' copied to Part Find")

    def on_delete(self):
        selected = self.partsTV.selection()[0]
        key = self.partsTV.item(selected, "values")[self.columnid.index('DigiKeyPartNumber')]
        table = self.partsTV.item(selected, "values")[self.columnid.index('Category')]
        if messagebox.askokcancel("Delete", "Click OK if you really want to delete '" + key + "' from database?"):
            Config().loaded_db.query("DELETE FROM `" + table + "` WHERE `" + Config().parameter['DigiKeyPartNumber'] + "` = '" + key + "'")
            self.status.set("Part Number '" + key + "' deleted from database")

    def on_select_new_field(self, event):
        new_selection = self.partsTV.selection()[0]
        current_value = self.element_value.get()
        if (self.partsTV.parent(new_selection) != ''):
            if self.current_selection is None or self.partsTV.item(self.current_selection, "values")[1] == current_value:
                value = self.partsTV.item(new_selection, "values")[1]
                key = self.partsTV.item(new_selection, "values")[0]
                self.element_name.set(key)
                self.element_value.set(value)
                self.current_selection = new_selection
                self.partsB.config(state=DISABLED)
                self.deletePartB.config(state=DISABLED)
                self.element_update.config(state=NORMAL)
                self.element_cancel.config(state=NORMAL)
                self.status.set("Part Number '" + self.partsTV.item(self.current_selection,"text") + "' Selected")
            else:
                self.do_flash()
                self.do_flash()
                self.status.seterror("Modified Parameter Value not Saved - Update or Cancel")

        else:
           self.partsB.config(state=NORMAL)
           self.deletePartB.config(state=NORMAL)
           self.element_update.config(state=DISABLED)
           self.element_cancel.config(state=DISABLED)
           self.on_clear_element()
        
    def on_copy_element(self, event):
        try:
            selected = self.partsTV.selection()[0]
            val = self.partsTV.item(selected,"values")[(3 if self.partsTV.parent(selected) == '' else 1)]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(val)
            self.parent.update()
            self.status.set("Part Number '" + val + "' copied to clipboard")
        except:
            pass

    def do_find(self, event):
        try:
            self.on_find()
        except Exception as e:
            self.status.seterror(e)

class ManualAddApplication(GenericFrame):
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
                tablelist = ['Capacitors'] + Config().tables
                catmenu = OptionMenu(self.propframe[-1], self.catoption, *tablelist, command=self.on_category)
                catmenu.pack(side=TOP, anchor=N, fill=X, expand=YES)


        self.buttonframe = Frame(self.manualframe)
        self.buttonframe.pack(side=TOP, fill=X, expand=NO)
        self.clearButton = ttk.Button(self.buttonframe, text="Clear", command=self.do_clear, state=NORMAL, width=8)
        self.clearButton.pack(side=RIGHT, anchor=W, fill=X, expand=NO)
        self.commitButton = ttk.Button(self.buttonframe, text="Add", command=self.do_commit, state=NORMAL, width=8)
        self.commitButton.pack(side=RIGHT, anchor=W, fill=X, expand=NO)
        self.statusFrame = LabelFrame(self, text="Status")
        self.statusFrame.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.status = self.StatusBar(self.statusFrame, self)
        self.status.set("Set Category")

        self.pack(side=LEFT, fill=BOTH, expand=YES)

    def do_clear(self):
        for i in range(len(self.PROPLIST)):
            if i != self.CATEGORY_INDEX:
                self.propvalue[i].set("")
        self.propvalue[self.CATEGORY_INDEX].set("")
        self.catoption.set("Capacitors")
        self.status.set("Set Category")
        
        
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
            self.status.seterror("Category Not Defined")
            return
        table = part["Category"]
        part["Category"] = table.capitalize()
        Config().insert_part(table, part)
        self.status.set("Part %s added to database"%part['Supplier Part Number 1'])
         
    def on_category(self, value):
        self.catentry.config(state=NORMAL)
        self.propvalue[self.CATEGORY_INDEX].set(value)
        self.catentry.config(state=DISABLED)
        self.status.set("Category Set - add part information the click add")
        
