
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
        self.selectedField = None

        self.parent.title("Partlocater - Advanced Database Search")
        self.parent.iconbitmap(self.FAVICON)
        self.menubar = Frame(self, background='white')
        
        self.menubar.pack(side=TOP, fill=X, expand=YES);
        self.win_frame = Frame(self)
        self.win_frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.editbutton = Menubutton(self.menubar, text='Edit', background='grey98')
        self.editbutton.pack(side=LEFT, fill=X)
        self.editmenu = Menu(self.editbutton, tearoff=0)
        self.editbutton.config(menu=self.editmenu)
        self.copySourcesMenu = Menu(self.editbutton, tearoff=0)
        self.editmenu.add_cascade(label='Copy', menu=self.copySourcesMenu)
        self.copySourcesMenu.add_command(label='Part Number', state=DISABLED, command=self.on_copy_partnumber)
        self.partnumber_index = 0
        self.copySourcesMenu.add_command(label='Selected Parameter', state=DISABLED, command=self.on_copy_parameters)
        self.selectedParameter_index = 1
        self.copySourcesMenu.add_command(label='Selected Part All Parameters', state=DISABLED, command=self.on_copy_all_parameters)
        self.allParameters_index = 2
        self.editmenu.add_command(label='Delete Part', state=DISABLED, command=self.on_delete)
        self.delete_part_index = 1
        
        self.searchLF = LabelFrame(self.win_frame, text="Search")
        self.searchLF.pack(side=LEFT, fill=X, expand=YES, pady=4, padx=6)
        self.searchLeftF = Frame(self.searchLF)
        self.searchLeftF.pack(side=LEFT, anchor=W)
        self.searchRightF = Frame(self.searchLF)
        self.searchRightF.pack(side=LEFT, anchor=N)
        self.searchLabelWidth = 20
        self.catF = Frame(self.searchLeftF)
        self.catF.pack(side=TOP, anchor=W)
        self.catL = Label(self.catF, text='Category', width=self.searchLabelWidth, anchor=W, justify=LEFT)
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
        self.manL = Label(self.manF, text='ManufacturerName', width=self.searchLabelWidth, anchor=W, justify=LEFT)
        self.manL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.man = StringVar()
        self.manE = Entry(self.manF, width=50, textvariable=self.man)
        self.manE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.mpnF = Frame(self.searchLeftF)
        self.mpnF.pack(side=TOP, anchor=W)
        self.mpnL = Label(self.mpnF, text='ManufacturerPartNumber', width=self.searchLabelWidth, anchor=W, justify=LEFT)
        self.mpnL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.mpn = StringVar()
        self.mpnE = Entry(self.mpnF, width=50, textvariable=self.mpn)
        self.mpnE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.spnF = Frame(self.searchLeftF)
        self.spnF.pack(side=TOP, anchor=W)
        self.spnL = Label(self.spnF, text='DigiKeyPartNumber', width=self.searchLabelWidth, anchor=W, justify=LEFT)
        self.spnL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.spn = StringVar()
        self.spnE = Entry(self.spnF, width=50, textvariable=self.spn)
        self.spnE.pack(side=LEFT, fill=X, expand=YES, pady=4)

        self.descF = Frame(self.searchLeftF)
        self.descF.pack(side=TOP, anchor=W)
        self.descL = Label(self.descF, text='ProductDescription', width=self.searchLabelWidth, anchor=W, justify=LEFT)
        self.descL.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.desc = StringVar()
        self.descE = Entry(self.descF, width=50, textvariable=self.desc)
        self.descE.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.descE.focus_force()

        self.findF = Frame(self.searchLeftF)
        self.findF.pack(side=TOP, anchor=E)
        self.findB = ttk.Button(self.findF, text="Find", width=12, command=lambda event=None: self.do_find(event))
        self.findB.pack(side=LEFT, pady=4)
        self.clearB = ttk.Button(self.findF, text="Clear", width=6, command=self.on_clear_search)
        self.clearB.pack(side=LEFT, pady=4)

        self.partsLF = LabelFrame(self, text="Found Components")
        self.partsLF.pack(side=TOP, fill=X, expand=YES, pady=4, padx=4)
        self.partsF = Frame(self.partsLF)
        self.partsF.pack(side=TOP, pady=4, padx=4)
        # change treeview for search here
        self.partsTV = Treeview(self.partsF, selectmode=BROWSE, show='tree headings', columns=self.column_id)

        self.partsTV.bind('<Double-Button-1>', self.on_edit_item)
        self.partsTV.bind('<<TreeviewSelect>>', self.fieldChanged)
        self.partsTV.bind('<Escape>', self.clearSelection)
        self.partsTV.bind('<MouseWheel>', self.mousewheel)
        self.partsTV.bind('<Button-4>', self.mousewheel)
        self.partsTV.bind('<Button-5>', self.mousewheel)
        vcmd = (self.register(self.validateEntry), '%P')
        self.editfield = ttk.Entry(self.partsTV, validate='key', validatecommand=vcmd)
        self.editfield.bind('<Return>', self.updateField)
        self.editfield.bind('<Escape>', self.clearSelection)

        
        self.partsTV.bind('<Control-c>', self.on_copy_element)
        self.partsTV.column("#0", minwidth=0, width=18, stretch=NO)
        for t in self.column_id:
            self.partsTV.heading(t, text=Config().parameter[t])
        self.partsTV.column('Category', width=60)
        self.scrollbar = Scrollbar(self.partsF, orient='vertical', command=self.partsTV.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y, expand=YES, anchor=E)
        self.partsTV.configure(yscroll=self.scrollbar.set)
        self.scrollbar.config(command=self.yview)
        
        self.partsTV.pack(side=TOP, anchor=W, fill=X, expand=YES)
        self.partsTV.delete(*self.partsTV.get_children())
    
        self.statusLF = LabelFrame(self, text="Status")
        self.statusLF.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.statusF = Frame(self.statusLF)
        self.statusF.pack(side=TOP, fill=X, expand=YES, padx=6)
        self.status = self.StatusBar(self.statusF, self)

    def validateEntry(self, P):
        if (len(P) <= 120):
            return True
        else:
            self.bell()
            return False
    # scroll bar event
    def yview(self,*args):
        if self.selectedField is not None:
            self.editfield.place_forget()
            self.selectedField = None
        self.partsTV.yview(*args)

    # mousewheel and button4/5 event
    def mousewheel(self, event):
        if self.selectedField is not None:
            self.editfield.place_forget()
            self.selectedField = None
            
    # escape event in treeview or editfield
    def clearSelection(self, event):
        self.editfield.place_forget()
        self.selectedField = None
        self.partsTV.selection_remove(self.partsTV.selection())
        self.status.set("")
              
    # double button event
    def on_edit_item(self, event):
        if self.partsTV.parent(self.partsTV.selection()) == '': # testing should not edit a parent
            self.selectedField = None
            return
        if(self.partsTV.identify_region(event.x, event.y) == 'cell'):
            self.selectedField = self.partsTV.identify_row(event.y)
            x,y,width,height = self.partsTV.bbox(self.selectedField, '#2')
            v = self.partsTV.set(self.selectedField, 1)
            self.editfield.pack()
            self.editfield.delete(0, len(self.editfield.get()))
            self.editfield.insert(0,v)
            self.editfield.selection_range(0, 'end')
            self.editfield.focus_force()
            self.editfield.place(x=x, y=y, width=width, height=height)    

    # find button event
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

    # return event
    def updateField(self, event):
        value=self.editfield.get()
        self.editfield.place_forget()
        name = self.partsTV.item(self.selectedField, "text")
        if not validate(value):
            self.status.seterror("Invalid value, must not have quotes")
            return
        self.partsTV.set(self.selectedField, "#2", value)
        key = self.partsTV.set(self.selectedField, "#1")
        self.editfield.place_forget()
        element_parent = self.partsTV.parent(self.selectedField)
        table_name = self.partsTV.item(element_parent, "values")[self.column_id.index('Category')]
        part_number = self.partsTV.item(element_parent, "values")[self.column_id.index('DigiKeyPartNumber')]
        set_param = "SET `" + key + "` = '" + value + "' "
        where = "WHERE `" + Config().parameter['DigiKeyPartNumber'] + "` = '" + part_number + "'"
        qry = "UPDATE `" + Config().loaded_db.name + "`.`" + table_name + "` " + set_param + where
        print(qry)
        try:
            Config().loaded_db.query(qry)
        except Exception as e:
            self.status.seterror("Database query failed: %s", e)
            return
        self.status.set("Changed " + key + " to " + value + " for part " + part_number + ".")
        self.partsTV.see(self.selectedField)

    # clear button in search frame   
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
    # category option menu
    def on_category(self, value):
        self.catE.config(state=NORMAL)
        self.cat.set(value)
        self.catE.config(state=DISABLED)

    #def on_copy(self):
        #selected = self.partsTV.selection()[0]
        #key = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]
        #self.app_window.part_num_string.set(key)
        #self.status.set("Part Number '" + key + "' copied to Part Find")
    # Edit -> Delete menu
    def on_delete(self):
        selected = self.partsTV.selection()[0]
        key = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]
        table = self.partsTV.item(selected, "values")[self.column_id.index('Category')]
        if messagebox.askokcancel("Delete", "Click OK if you really want to delete '" + key + "' from database?"):
            Config().loaded_db.query("DELETE FROM `" + table + "` WHERE `" + Config().parameter['DigiKeyPartNumber'] +
                                     "` = '" + key + "'")
            self.status.set("Part Number '" + key + "' deleted from database")
            try:
                self.on_find()
            except Exception as e:
                self.status.seterror(e)

    # treeview select event
    def fieldChanged(self, event):
        selected = self.partsTV.selection()
        if len(selected) > 0:
            self.copySourcesMenu.entryconfig(self.partnumber_index, state=NORMAL)
            self.copySourcesMenu.entryconfig(self.allParameters_index, state=NORMAL)
        else:
            self.copySourcesMenu.entryconfig(self.partnumber_index, state=DISABLED)
            self.copySourcesMenu.entryconfig(self.allParameters_index, state=DISABLED)
            self.copySourcesMenu.entryconfig(self.selectedParameter_index, state=DISABLED)
            self.editmenu.entryconfig(self.delete_part_index, state=DISABLED)
            return
        if self.partsTV.parent(selected) == '':
            self.copySourcesMenu.entryconfig(self.selectedParameter_index, state=DISABLED)
            self.editmenu.entryconfig(self.delete_part_index, state=NORMAL)
        else:
            self.copySourcesMenu.entryconfig(self.selectedParameter_index, state=NORMAL)
            self.editmenu.entryconfig(self.delete_part_index, state=DISABLED)
        if selected != self.selectedField:
            self.editfield.place_forget()
            self.selectedField = None


    def on_copy_parameters(self):
        selected = self.partsTV.selection()
        if len(selected) == 0 or self.partsTV.parent(selected) == '':
            return
        try:
            property = self.partsTV.item(selected, "values")
            self.parent.clipboard_clear()
            self.parent.clipboard_append(property[0] + '\t' + property[1])
            self.parent.update()
            self.status.set(property[0] + ' ' + property[1] + " copied to clipboard")
        except Exception as e:
            pass
    
    def on_copy_partnumber(self):
        selected = self.partsTV.selection()
        if len(selected) == 0 or self.partsTV.parent(selected) == '':
            return
        try:
            if self.partsTV.parent(selected) != '':
                selected = self.partsTV.parent(selected)
            partnumber = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(partnumber)
            self.parent.update()
            self.status.set(" '" + partnumber + "' copied to clipboard")
        except Exception as e:
            pass
    
    def on_copy_all_parameters(self):
        selected = self.partsTV.selection()
        if len(selected) == 0:
            return
        try:
            if self.partsTV.parent(selected) != '':
                selected = self.partsTV.parent(selected)
            partnumber = self.partsTV.item(selected, "values")[self.column_id.index('DigiKeyPartNumber')]            
            elements = self.partsTV.get_children(selected)
            self.parent.clipboard_clear()
            self.parent.clipboard_clear()
            for i in elements:
                element = self.partsTV.item(i, "values")
                self.parent.clipboard_append(element[0] + "\t" + element[1] + "\n")
            self.parent.update()
            self.status.set("All properties of " + partnumber +  " copied to clipboard")
        except Exception as e:
            pass

          # deprecate   
    def on_copy_element(self, event):
        try:
            selected = self.partsTV.selection()[0]
            if self.partsTV.parent(selected) == '':
                partnumber = self.partsTV.item
                elements = self.partsTV.get_children(selected)
                self.parent.clipboard_clear()
                for i in elements:
                    element = self.partsTV.item(i, "values")
                    self.parent.clipboard_append(element[0] + "\t" + element[1] + "\n")
                self.parent.update()
                self.status.set("All properties of " + self.partsTV.item(selected,"values")[3] +  " copied to clipboard")
            else:
                key = self.partsTV.item(selected, "values")[0]
                val = self.partsTV.item(selected, "values")[1]
                self.parent.clipboard_clear()
                self.parent.clipboard_append(val)
                self.parent.update()
                self.status.set(key + " '" + val + "' copied to clipboard")
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
