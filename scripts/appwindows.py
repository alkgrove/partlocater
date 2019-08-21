
from tkinter import ttk, messagebox
from configReader import *
from genericframe import *
from partdb import *
from tkinter.ttk import Treeview, Scrollbar, OptionMenu, Button


class SearchApplication(GenericFrame):
    FAVICON = "../assets/favicon.ico"

    def __init__(self, parent=None, app_window=None):
        self.lastValue = None
        self.category_option = StringVar("")
        self.column_id = ['ProductDescription', 'ManufacturerName',
                          'ManufacturerPartNumber', 'DigiKeyPartNumber', 'Category']
        Frame.__init__(self, parent)
        self.pack()
        self.parent = parent
        self.app_window = app_window
        self.current_selection = None

        self.parent.title("Partlocater - Advanced Database Search")
        self.parent.iconbitmap(self.FAVICON)
        self.win_frame = Frame(self)
        self.win_frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.searchLF = LabelFrame(self.win_frame, text="Search")
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
        self.category_option = StringVar()
        self.cat.set("All")
        option_list = ['All', 'All'] + Config().tables
        self.catM = OptionMenu(self.searchRightF, self.category_option, *option_list, command=self.on_category)
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
        self.partsF = Frame(self.partsLF)
        self.partsF.pack(side=TOP)
        self.partsTV = Treeview(self.partsF, selectmode=BROWSE, show='tree headings', columns=self.column_id)
        self.partsTV.bind('<<TreeviewSelect>>', self.on_select_new_field)
        self.partsTV.bind('<Control-c>', self.on_copy_element)
        self.partsTV.column("#0", minwidth=0, width=18, stretch=NO)
        for t in self.column_id:
            self.partsTV.heading(t, text=Config().parameter[t])
        self.partsTV.column('Category', width=60)
        self.scrollbar = Scrollbar(self.partsF, orient='vertical', command=self.partsTV.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.partsTV.configure(yscroll=self.scrollbar.set)
        self.scrollbar.config(command=self.partsTV.yview)
        self.partsTV.pack(side=TOP, anchor=W, fill=X, expand=YES)
        self.partsTV.delete(*self.partsTV.get_children())

        self.part_buttonF = Frame(self.partsLF)
        self.delete_partB = ttk.Button(self.partsLF, text="Delete Part from Database", command=self.on_delete,
                                       state=DISABLED)
        self.delete_partB.pack(side=RIGHT, anchor=W, expand=NO, pady=4, padx=6)
        self.partsB = ttk.Button(self.partsLF, text="Copy Selected To Part Find", command=self.on_copy, state=DISABLED)
        self.partsB.pack(side=RIGHT, anchor=W, expand=NO, pady=4, padx=6)
        self.part_buttonF.pack(side=BOTTOM)
        
        self.element_labelframe = LabelFrame(self, text="Modify Name/Value")
        self.element_labelframe.pack(side=TOP, fill=X, expand=YES, pady=4, padx=6)
        self.element_frame = Frame(self.element_labelframe)
        self.element_frame.pack(side=TOP)

        self.element_name = StringVar()
        self.element_label = Label(self.element_frame, textvariable=self.element_name, width=30, anchor=W, justify=LEFT)
        self.element_label.pack(side=LEFT, anchor=W, fill=X, expand=YES, pady=4)
        self.element_value = StringVar()
        self.element_entry = Entry(self.element_frame, width=50, textvariable=self.element_value)
        self.element_entry.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.default_color = self.element_entry.cget('background')

        self.element_update = ttk.Button(self.element_frame, text="Update", command=self.on_update_element,
                                         state=DISABLED)
        self.element_update.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.element_cancel = ttk.Button(self.element_frame, text="Cancel", command=self.on_clear_element,
                                         state=DISABLED)
        self.element_cancel.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.statusLF = LabelFrame(self, text="Status")
        self.statusLF.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.statusF = Frame(self.statusLF)
        self.statusF.pack(side=TOP, fill=X, expand=YES, padx=6)
        self.status = self.StatusBar(self.statusF, self)

    def on_find(self):
        category = self.cat.get()
        search_list = []
        col_list = []
        search_str = self.man.get()
        if not (validate(search_str)):
            raise Exception("Invalid Manufacture Name")
        search_list.append(search_str)
        col_list.append(Config().parameter['ManufacturerName'])
        search_str = self.mpn.get()
        if not (validate(search_str)):
            raise Exception("Invalid Manufacture Part Number")
        search_list.append(search_str)
        col_list.append(Config().parameter['ManufacturerPartNumber'])
        search_str = self.spn.get()
        if not (validate(search_str)):
            raise Exception("Invalid Supplier Part Number")
        search_list.append(search_str)
        col_list.append(Config().parameter['DigiKeyPartNumber'])
        search_str = self.desc.get().split()
        if not (validate(search_str)):
            raise Exception("Invalid Description")
        search_list += search_str
        col_list.append(Config().parameter['ProductDescription'])
        select = "SELECT * FROM `" + Config().loaded_db.name + "`."
        where = "WHERE"
        like = ""
        i = 0
        for item in search_list:
            if len(item) > 0:
                item = item.replace('%', '\\%')
                item = item.replace('"', '')
                item = item.replace("'", "")
                if i < 3:
                    like += where + " `" + col_list[i] + "` LIKE '" + item + "%'"
                else:
                    like += where + " (`" + col_list[i] + "` LIKE '" + item + "%' OR `" + \
                            col_list[i] + "` LIKE '% " + item + "%')"
                where = " AND"
            i = i + 1 if (i < 3) else i
        self.partsTV.delete(*self.partsTV.get_children())
        count = 0
        if category == "All":
            for table in Config().tables:
                qry = select + "`" + table + "` " + like
                result = Config().loaded_db.query(qry)
                for record in result:
                    v = []
                    spn = record[Config().parameter['DigiKeyPartNumber']]
                    count += 1
                    for id in self.column_id:
                        if id == 'Category':
                            v.append(table)
                        else:
                            v.append(record[Config().parameter[id]])
                    id = self.partsTV.insert('', 'end', iid=spn, text=spn, values=v)
                    for params in record:
                        if record[params] is not None:
                            self.partsTV.insert(id, 'end', text=spn, values=(params, record[params]))
        else:
            qry = select + "`" + category + "` " + like
            result = Config().loaded_db.query(qry)
            for record in result:
                v = []
                count += 1
                spn = record[Config().parameter['DigiKeyPartNumber']]
                for id in self.column_id:
                    if id == 'Category':
                        v.append(category)
                    else:
                        v.append(record[Config().parameter[id]])
                id = self.partsTV.insert('', 'end', iid=spn, text=spn, values=v)
                for params in record:
                    if record[params] is not None:
                        self.partsTV.insert(id, 'end', text=spn, values=(params, record[params]))
        self.status.set(("No" if count == 0 else str(count)) + " items found")

    def on_update_element(self):
        if self.current_selection is None:
            return
        item_name = self.partsTV.item(self.current_selection, "text")
        key = self.element_name.get()
        if len(key) > 0:
            value = self.element_value.get()
            if not validate(value):
                self.status.seterror("Invalid value, must not have quotes")
                return
            element_parent = self.partsTV.parent(self.current_selection)
            table_name = self.partsTV.item(element_parent, "values")[self.column_id.index('Category')]
            part_number = self.partsTV.item(element_parent, "values")[self.column_id.index('DigiKeyPartNumber')]
            set_param = "SET `" + key + "` = '" + value + "' "
            where = "WHERE `" + Config().parameter['DigiKeyPartNumber'] + "` = '" + part_number + "'"
            qry = "UPDATE `" + Config().loaded_db.name + "`.`" + table_name + "` " + set_param + where
            try:
                Config().loaded_db.query(qry)
            except Exception as e:
                self.status.seterror("Database query failed: %s", e)
                return
            self.status.set("Changed " + key + " to " + value + " for part " + part_number + ".")
            self.partsTV.set(self.current_selection, "#2", value)
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
        self.category_option.set("All")
        self.partsTV.delete(*self.partsTV.get_children())
    
    def do_flash(self):
        current_color = self.element_entry.cget("background")
        if current_color == self.default_color:
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
        key = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]
        self.app_window.part_num_string.set(key)
        self.status.set("Part Number '" + key + "' copied to Part Find")

    def on_delete(self):
        selected = self.partsTV.selection()[0]
        key = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]
        table = self.partsTV.item(selected, "values")[self.column_id.index('Category')]
        if messagebox.askokcancel("Delete", "Click OK if you really want to delete '" + key + "' from database?"):
            Config().loaded_db.query("DELETE FROM `" + table + "` WHERE `" + Config().parameter['DigiKeyPartNumber'] +
                                     "` = '" + key + "'")
            self.status.set("Part Number '" + key + "' deleted from database")

    def on_select_new_field(self, event):
        new_selection = self.partsTV.selection()[0]
        current_value = self.element_value.get()
        if self.partsTV.parent(new_selection) != '':
            if self.current_selection is None or self.partsTV.item(self.current_selection, "values")[1] \
                    == current_value:
                value = self.partsTV.item(new_selection, "values")[1]
                key = self.partsTV.item(new_selection, "values")[0]
                self.element_name.set(key)
                self.element_value.set(value)
                self.current_selection = new_selection
                self.partsB.config(state=DISABLED)
                self.delete_partB.config(state=DISABLED)
                self.element_update.config(state=NORMAL)
                self.element_cancel.config(state=NORMAL)
                self.status.set("Part Number '" + self.partsTV.item(self.current_selection, "text") + "' Selected")
            else:
                self.do_flash()
                self.do_flash()
                self.status.seterror("Modified Parameter Value not Saved - Update or Cancel")

        else:
            self.partsB.config(state=NORMAL)
            self.delete_partB.config(state=NORMAL)
            self.element_update.config(state=DISABLED)
            self.element_cancel.config(state=DISABLED)
            self.on_clear_element()
        
    def on_copy_element(self, event):
        try:
            selected = self.partsTV.selection()[0]
            val = self.partsTV.item(selected, "values")[(3 if self.partsTV.parent(selected) == '' else 1)]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(val)
            self.parent.update()
            self.status.set("Part Number '" + val + "' copied to clipboard")
        except Exception as e:
            pass

    def do_find(self, event):
        try:
            self.on_find()
        except Exception as e:
            self.status.seterror(e)


class ManualAddApplication(GenericFrame):
    FAVICON = "../assets/favicon.ico"
    PROPLIST = ['Category', 'Manufacturer', 'Manufacturer Part Number',
                'Supplier 1', 'Supplier Part Number 1', 'Description', 'Cost', 'Footprint Ref',
                'Library Ref']
                
    CATEGORY_INDEX = 0
    SPN_INDEX = 4

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title("Partlocater - Manual Add")

        self.parent.iconbitmap(self.FAVICON)
         
        self.manual_frame = LabelFrame(self, text="Add Component")
        self.manual_frame.pack(side=TOP, fill=BOTH, expand=YES, pady=4, padx=4)
        self.prop_frame = []
        self.propvalue = []
        for item in self.PROPLIST:
            self.prop_frame.append(Frame(self.manual_frame))
            self.prop_frame[-1].pack(side=TOP, fill=X, expand=YES)
            prop_label = Label(self.prop_frame[-1], anchor=E, text=item, width=20)
            prop_label.pack(side=LEFT, anchor=E, fill=X, expand=YES, pady=4)
            self.propvalue.append(StringVar())
            if item != "Category":
                prop_entry = Entry(self.prop_frame[-1], textvariable=self.propvalue[-1], state=NORMAL, width=30)
                prop_entry.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=4)
                self.propvalue[-1].trace("w", self.check_minentry)
            else:
                self.cat_entry = Entry(self.prop_frame[-1], textvariable=self.propvalue[-1], state=DISABLED, width=40)
                self.cat_entry.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=4)
                if (item.startswith("Manufacturer")): 
                    self.propvalue[-1].trace("w", self.check_minentry)
                self.cat_option = StringVar()
                table_list = ['Capacitors'] + Config().tables
                cat_menu = OptionMenu(self.prop_frame[-1], self.cat_option, *table_list, command=self.on_category)
                cat_menu.pack(side=TOP, anchor=N, fill=X, expand=YES)

        self.button_frame = Frame(self.manual_frame)
        self.button_frame.pack(side=TOP, fill=X, expand=NO)
        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.do_clear, state=NORMAL, width=8)
        self.clear_button.pack(side=RIGHT, anchor=W, fill=X, expand=NO)
        self.commit_button = ttk.Button(self.button_frame, text="Add", command=self.do_commit, state=DISABLED, width=8)
        self.commit_button.pack(side=RIGHT, anchor=W, fill=X, expand=NO)
        self.status_frame = LabelFrame(self, text="Status")
        self.status_frame.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.status = self.StatusBar(self.status_frame, self)
        self.status.set("Set Category")

        self.pack(side=LEFT, fill=BOTH, expand=YES)

    def check_minentry(self,*args):
        check = 0
        for i in range(3):
            if (self.propvalue[i].get()):
                check = check+1
        if check == 3:
            self.commit_button.config(state=NORMAL)
        else:
            self.commit_button.config(state=DISABLED)
            
    def do_clear(self):
        for i in range(len(self.PROPLIST)):
            if i != self.CATEGORY_INDEX:
                self.propvalue[i].set("")
        self.propvalue[self.CATEGORY_INDEX].set("")
        self.cat_option.set("Capacitors")
        self.status.set("Set Category")

    def get_part(self):
        part = {}
        for i in range(len(self.PROPLIST)):
            value = self.propvalue[i].get()
            if value:
                if not validate(value):
                    raise self.PROPLIST[i] + " not valid"
                part[self.PROPLIST[i]] = value
        if 'Supplier Part Number 1' not in part:
            raise Exception("Supplier Part Number must be defined")
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
        self.status.set("Part %s added to database" % part['Supplier Part Number 1'])
         
    def on_category(self, value):
        self.cat_entry.config(state=NORMAL)
        self.propvalue[self.CATEGORY_INDEX].set(value)
        self.cat_entry.config(state=DISABLED)
        self.status.set("Category Set - add part information the click add")

class OpenDatabasePopup(GenericFrame):
    FAVICON = "../assets/favicon.ico"

    def __init__(self, parent=None, app_window=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.app_window = app_window
        self.parent.title("Partlocater - Open Database")

        self.parent.attributes("-toolwindow", 1)
        self.parent.iconbitmap(self.FAVICON)
        self.parent.grab_set_global()
        self.database_frame = LabelFrame(self, text="Select Database")
        self.database_frame.pack(side=TOP, fill=BOTH, expand=YES, pady=10, padx=10)
        for db,mdb in Config().db_list:
            self.database_btn = ttk.Button(self.database_frame, text=db.id + " (" + db.host + " " + db.name + ")", command=lambda db=db, mdb=mdb: self.select_database(db, mdb))
            self.database_btn.pack(side=TOP, anchor=W, fill=X, expand=YES, pady=2, padx=5)
        self.cancel = ttk.Button(self.database_frame, text="Cancel", command=self.on_cancel, state=NORMAL)
        self.cancel.pack(side=LEFT, fill=X, expand=YES, pady=2, padx=5)
        
        self.pack(side=LEFT, fill=BOTH, expand=YES)

    def select_database(self, database, meta_database):
        self.app_window.on_connect(database, meta_database)
        self.app_window.database_window.destroy()
    
    def on_cancel(self):
        self.app_window.status.set("Database not connected - use File->Connect To... to connect to database")
        self.app_window.database_window.destroy()
