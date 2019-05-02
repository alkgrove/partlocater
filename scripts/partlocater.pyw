#! /usr/bin/python

# partlocater.py 
# This is the main executible for the Digi-Key query to SQL database tool
# by Alex Alkire & Bob Alkire (Copyright 2019)
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted 
# provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions   
# and the following disclaimer.  
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions  
# and the following disclaimer in the documentation and/or other materials provided with the 
# distribution.  
# 3. Neither the name of the copyright holder nor the names of its contributors may be 
# used to endorse or promote products derived from this software without specific prior written 
# permission.  
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR 
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER 
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF 
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from tkinter import *
from datetime import timedelta, datetime
import os
import subprocess
import requests
import logging
import json
import types
import re, string
import digikey
from configReader import *
from digikey import *
import partdb
from searchdb import *
from about import *
import traceback
from tkinter import font, filedialog, messagebox
from genericframe import *
from tkinter.ttk import Treeview, Scrollbar
###############################
###   Tkinter App Window    ###
###############################


class Application(GenericFrame):
    LED_ON = "../assets/ledon.gif"
    LED_OFF = "../assets/ledoff.gif"

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()
        self.loaded_parameters = dict()
        self.loaded_table = None
        self.commit_btn.config(state=DISABLED)
        self.locate_btn.config(state=DISABLED)
        self.clear_btn.config(state=DISABLED)
        self.current_selection = None
        self.hiliteList = {'Library Ref':1, 'Footprint Ref':1, 'Base Part Number':1}
    ###############################
    ###       Exceptions        ###
    ###############################
    class EmptyField(Exception):
        def __init__(self, expression):
            self.expression = expression
            self.message = "Empty Field Error"

        def __str__(self):
            return self.message

    ###############################
    ###        Events           ###
    ###############################
    def handleError(self, title, e=""):
        self.status.seterror(title+" "+str(e))
        Config().log_write("ERROR: " + str(e))
        Config().log_write(traceback.format_exc())

    def close_search_window(self):
        self.databaseMenu.entryconfig(self.search_index, state=NORMAL)
        self.searchwindow.destroy()

    def reset_hilite(self):
        for i in self.hiliteList:
            self.hiliteList[i] = 1

    def close_about_window(self):
        self.aboutMenu.entryconfig(self.about_index, state=NORMAL)
        self.aboutwindow.destroy()

    def close_systeminfo_window(self):
        self.aboutMenu.entryconfig(self.system_index, state=NORMAL)
        self.systeminfowindow.destroy()

    def close_help_window(self):
        self.aboutMenu.entryconfig(self.help_index, state=NORMAL)
        self.helpwindow.destroy()

    def on_about(self):
        self.aboutwindow = Toplevel(self.master)
        about = AboutApplication(parent=self.aboutwindow)
        self.aboutwindow.protocol("WM_DELETE_WINDOW", self.close_about_window)
        self.aboutMenu.entryconfig(self.about_index, state=DISABLED)
        return

    def on_help(self):
        self.helpwindow = Toplevel(self.master)
        help = HelpApplication(parent=self.helpwindow)
        self.helpwindow.protocol("WM_DELETE_WINDOW", self.close_help_window)
        self.aboutMenu.entryconfig(self.help_index, state=DISABLED)
        return

    def on_export(self):
        exportfilename = filedialog.asksaveasfilename(initialdir = ".",title = "Save database '" + Config().loaded_db.name + "' to file.sql",filetypes = (("sql file","*.sql"),("all files","*.*")))
        if not exportfilename == "":
            if not exportfilename.lower().endswith('.sql'):
                exportfilename += '.sql'
            try:
                subprocess.call('"' + Config().pref['mysql_path'] + '\mysqldump" --user=' + Config().loaded_db.user + ' --password=' + Config().loaded_db.password +
                                ' --opt --databases ' + Config().loaded_db.name +' > "' + exportfilename + '"', shell=True)
            except OSError as e:
                self.status.seterror("mysqldump failed: %s", e)
            self.status.set("Exported " + exportfilename + " from database '" + Config().loaded_db.name + "'")
    def on_import(self):
        if (Config().loaded_db.database_exists()):
            tables, rows = Config().loaded_db.get_count()
            if (rows > 0):
                if askokcancel("Delete Existing Database", "Do you want to remove the existing database and replace it with the imported one?") == 0:
                    self.status.set("Cancel import")
                    return
            
        importfilename = filedialog.askopenfilename(initialdir = ".",title = "Load .sql file into database '" + Config().loaded_db.name + "'",filetypes = (("sql files","*.sql"),("all files","*.*")))
        if not importfilename == "":
            try:
                subprocess.call('"' + Config().pref['mysql_path'] + '\mysql" --user=' + Config().loaded_db.user + ' --password=' + Config().loaded_db.password +
                                    ' ' + Config().loaded_db.name +' < "' + importfilename + '"', shell=True)
            except OSError as e:
                self.status.seterror("mysql failed: %s", e)
            self.status.set("File " + os.path.basename(importfilename) + " imported into database " + Config().loaded_db.name )

    def on_sync_token(self):
        tokenlist = []
        maxts = 0
        for db, mdb in Config().db_list:
            try: 
                token = mdb.get_latest_token()
                ts = token['timestamp'].timestamp()
                if (ts > maxts):
                    maxmdb = mdb
                    maxtoken = token
                    maxts = ts
                tokenlist.append((mdb, token))
            except:
                pass
        print("Token %s Timestamp %s"%(maxtoken['access_token'], maxtoken['timestamp']))
        update = False
        # we update all databases except for the newest one
        for mdb,token in tokenlist:
            if (maxtoken['access_token'] != token['access_token']):
                print ("Updating Tokens ", maxtoken['access_token'], token['access_token'])
                try:
                    mdb.set_token(maxtoken);
                    self.status.set("Updating token to host: %s database: %s" % (mdb.host, mdb.name))
                    update = True
                except Exception as e:
                    self.status.seterror("Update Token Failed: %s", e)
        if not update:
            self.status.set("No change, all tokens up to date")
                   
        
    def on_systeminfo(self):
        self.systeminfowindow = Toplevel(self.master)
        about = SystemInfoApplication(parent=self.systeminfowindow, cfg=Config())
        self.systeminfowindow.protocol("WM_DELETE_WINDOW", self.close_systeminfo_window)
        self.aboutMenu.entryconfig(self.system_index, state=DISABLED)
        return

    def on_open_search(self):
        if Config().loaded_db is None:
            self.handleError("Failed to open Search Window.", Exception("No database currently loaded!"))
            return
        Config().tables = Config().loaded_db.get_tables()
        self.searchwindow = Toplevel(self.master)
        self.searchwindow.resizable(False, False)
        app = SearchApplication(parent=self.searchwindow, dbwindow=self)
        self.searchwindow.protocol("WM_DELETE_WINDOW", self.close_search_window)
        self.databaseMenu.entryconfig(self.search_index, state=DISABLED)
        return
 
    def on_disconnect(self):
        if Config().loaded_db is not None:
            Config().loaded_db.close()
            self.status.set("Database %s Disconnected", Config().loaded_db.name)
            Config().loaded_db = None
            self.locate_btn.config(state=DISABLED)
            self.databaseMenu.entryconfig(self.search_index, state=DISABLED)
            self.databaseMenu.entryconfig(self.disconnect_index, state=DISABLED)
            if self.export_index is not None:
                self.databaseMenu.entryconfig(self.export_index, state=DISABLED)
                self.databaseMenu.entryconfig(self.import_index, state=DISABLED)
        if Config().loaded_metadb is not None:
            Config().loaded_metadb.close()
            Config().loaded_metadb = None
           
    def on_connect(self, database, meta_database):
        self.on_disconnect()
        Config().load_database(database, meta_database)
        if ((self.export_index is not None) and (Config().loaded_db.host == 'localhost')):
            self.databaseMenu.entryconfig(self.import_index, state=NORMAL)
        try:
            Config().loaded_db.connect()
            self.status.set("Host %s Database %s Connected", Config().loaded_db.host, Config().loaded_db.name)
        except Exception as e:
            self.status.seterror("Failed to connect to Host %s Database %s. %s", Config().loaded_db.host, Config().loaded_db.name, e)
            return
        self.databaseMenu.entryconfig(self.search_index, state=NORMAL)
        if ((self.export_index is not None) and (Config().loaded_db.host == 'localhost')):
            self.databaseMenu.entryconfig(self.export_index, state=NORMAL)
        Config().log_write("Check Token")
        # get the latest token in the database
        try:
            token_info = Config().loaded_metadb.get_latest_token()
            Config().access_token_string = token_info['access_token']
#            Config().loaded_metadb.connect()
#            token_info = Config().load_current_token_info()
            Config().log_write("Current Token is " + token_info['access_token'])
        except Exception as e:
            self.status.seterror("Can't find token from %s. Use browser to get initial token", Config().loaded_metadb.host)
            Config().log_write("Error while trying to get token from database %s. Error: %s", Config().loaded_metadb.host, str(e))
            return
        
        if is_token_old(token_info):
            try:          
                Config().log_write("Token Expired, Updating from Digi-Key with %s" % token_info['refresh_token'])
                new_token = digikey_get_new_token(token_info['refresh_token'])
                new_token['timestamp'] = datetime.now()
                Config().access_token_string = new_token['access_token']
            except Exception as e:
                self.status.seterror("Digikey Query: %s", e)
                return
            Config().loaded_metadb.set_token(new_token)
#            Config().refresh_token(new_token) # replace with set token
            self.status.set("Host %s Database %s Connected, Token Updated", Config().loaded_db.host, Config().loaded_db.name)
        self.databaseMenu.entryconfig(self.disconnect_index, state=NORMAL)
        self.locate_btn.config(state=NORMAL)
        self.clear_btn.config(state=NORMAL)
        Config().log_write("Connected to "+database.name)

    def on_clear_element(self):
        self.current_selection = None
        self.element_name.set("")
        self.element_value.set("")

    def on_clear_btn(self):
        self.on_clear_element()
        self.part_num_string.set("")
        for i in self.part_info_tree.get_children():
            self.part_info_tree.delete(i)
        self.update_part_info({})
        self.commit_btn.config(state=DISABLED)
        self.element_update.config(state=DISABLED)
        self.part_label.set("Part Info")
        self.status.set("")
 
    def on_commit_btn(self):
        try:
            if self.commit_btn["text"] == "Overwrite":
                Config().update_part(self.loaded_table, self.loaded_parameters)
                self.status.set("Part %s updated in %s", self.loaded_parameters['Supplier Part Number 1'], self.loaded_table) 
            else:
                newTable = ""
                if (Config().insert_part(self.loaded_table, self.loaded_parameters)):
                    newTable = " New Library generated, update Altium"
                self.status.set("Part %s added to %s%s", self.loaded_parameters['Supplier Part Number 1'], self.loaded_table, newTable) 
                self.commit_btn["text"] = "Overwrite"
        except Exception as e:
            self.handleError("Error while committing entry into Database", e)

    def on_locate_btn(self):
        try:
            part_num = self.get_part_num_field()
            self.status.set("Query Digi-Key")
            part_json = digikey_get_part(part_num)
        except Exception as e:
            self.handleError("",e)
            return
        try:
            self.loaded_parameters, self.loaded_table = translate_part_json(part_json)
        except Exception as e:
            self.handleError("Translation Error", e)
            return
        except self.EmptyField as e:
            return
        part_stat = ""
        try:
            self.commit_btn.config(state=NORMAL)
            self.element_update.config(state=DISABLED)
            if Config().entry_exists(part_num, self.loaded_table):
                self.commit_btn["text"] = "Overwrite"
                part_stat = ", part is already in database"
            else:
                self.commit_btn["text"] = "Commit"
                part_stat = ", not in database, commit to add"
        except Exception as e:
            self.handleError("Error while searching for entry in Database", e)
        self.on_clear_element()
        self.reset_hilite()
        self.status.set("Found part %s%s", part_num, part_stat)
        self.part_label.set("Part Info: %s" % part_num)
        self.update_part_info(self.loaded_parameters)
         
    def on_update_element(self):
        if self.current_selection is None:
            return
        item_name = self.part_info_tree.item(self.current_selection, "text")
        self.current_selection = None
        new_item_value = self.element_value.get()
        if not validate(new_item_value):
            self.status.seterror("Invalid value, must not have quotes")
            return
        self.loaded_parameters[item_name] = new_item_value
        self.on_clear_element()
        self.status.set("%s updated", item_name)
        if (item_name in self.hiliteList):
            self.hiliteList[item_name] = 0
        self.update_part_info(self.loaded_parameters)

    def do_flash(self):
        current_color = self.element_entry.cget("background")
        if (current_color == self.default_color):
            self.element_entry.config(background="red")
        else:
            self.element_entry.config(background=self.default_color)
            return
        root.after(250, self.do_flash)

    def on_select_new_field(self, event):
        new_selection = self.part_info_tree.selection()[0]
        current_value = self.element_value.get()
        # first we check if it has been updated or first selection or
        # we check if the last selected item value and the value in the text entry has changed
        if self.current_selection is None or self.part_info_tree.item(self.current_selection, "values")[1] == current_value:
            # no old stuff to update, so update the modify fields and set the new current_selection
            value = self.part_info_tree.item(new_selection, "values")[1]
            key = self.part_info_tree.item(new_selection, "text")
            self.element_name.set(key)
            self.element_value.set(value)
            self.current_selection = new_selection
            self.element_update.config(state=NORMAL)
            self.status.set("Name '%s' Fetched - modify then update", key)
        else:
            self.do_flash()
            self.status.seterror("Modified Parameter Value not Saved - Update or Cancel")


    ###############################
    ###    GUI Functionality    ###
    ###############################
    def get_part_num_field(self):
        part_id = self.part_num_string.get().strip()
        if not (validate(part_id)): 
            raise Exception("Invalid part number, must not have quotes")
        if part_id == "":
            raise self.EmptyField('Part Number')
        return part_id

    def update_part_info(self, dict):
        self.part_info_tree.delete(*self.part_info_tree.get_children())
        if len(dict) > 0:
            for k, v in dict.items():
                if k in self.hiliteList and self.hiliteList[k]:
                    self.part_info_tree.insert('', 'end', iid=k, text=k, values=(k, v), tags=('hilite','boldfont'))
                else:
                    self.part_info_tree.insert('', 'end', iid=k, text=k, values=(k, v))

           
    def on_copy_element(self, event):
        try:
            selected = self.part_info_tree.selection()[0]
            pn = self.part_info_tree.item(selected,"values")[1]
            self.clipboard_clear()
            self.clipboard_append(pn)
            self.update()
            self.status.set("Part Number '" + pn + "' copied to clipboard")
        except Exception as e:
            pass
    ###############################
    ###           GUI           ###
    ###############################



    def create_widgets(self):
        global config
        # Frame Containers
        self.window_frame = Frame(self, width=1200)

        self.top_frame = Frame(self.window_frame, width=800)
        self.top_frame.pack(side="top", fill=X, expand=YES, pady=12)
        self.left_frame = Frame(self.top_frame, width=600)
        self.left_frame.pack(side="left", fill=BOTH, expand=YES)
        self.right_frame = Frame(self.top_frame, width=200)
        self.right_frame.pack(side="left", padx=10)
        self.window_frame.pack(pady=(0, 12))
        
        self.element_labelframe = LabelFrame(self.window_frame, text="Modify Name/Value")
        self.element_labelframe.pack(side=TOP, fill=X, expand=YES, pady=4, padx=6)
        self.element_frame = Frame(self.element_labelframe);
        self.element_frame.pack(side=TOP)

        self.menubar = Menu(self)
        self.databaseMenu = Menu(self.menubar, tearoff=0)
        self.databaseListMenu = Menu(self.databaseMenu, tearoff=0)
        self.databaseMenu.add_cascade(label="Connect to", menu=self.databaseListMenu)
        for db,mdb in Config().db_list:
            self.databaseListMenu.add_command(label=db.id + " (" + db.host + " " + db.name + ")", command=lambda db=db, mdb=mdb: self.on_connect(db,mdb))
        self.databaseMenu.add_command(label="Disconnect", state=DISABLED, command=lambda : self.on_disconnect())
        self.disconnect_index = 1
        self.databaseMenu.add_separator()
        self.databaseMenu.add_command(label="Search Database", state=DISABLED, command=lambda : self.on_open_search())
        self.search_index = 3
        self.databaseMenu.add_command(label="Sync Tokens", state=DISABLED, command=lambda : self.on_sync_token())
        self.sync_token_index = 4
        if (len(Config().db_list) > 1):
            self.databaseMenu.entryconfig(self.sync_token_index, state=NORMAL)
        self.export_index = None
        self.import_index = None
        if 'mysql_path' in Config().pref:
            self.databaseMenu.add_command(label="Export", state=DISABLED, command=lambda : self.on_export())
            self.export_index = 5
            self.databaseMenu.add_command(label="Import", state=DISABLED, command=lambda : self.on_import())
            self.import_index = 6
        self.databaseMenu.add_command(label="Quit", command=root.quit);
        self.menubar.add_cascade(label="File", menu=self.databaseMenu)
        self.aboutMenu = Menu(self.menubar, tearoff=0)
        self.aboutMenu.add_command(label="About", command = lambda:self.on_about())
        self.about_index = 0
        self.aboutMenu.add_command(label="System", command = lambda:self.on_systeminfo())
        self.system_index = 1
        self.aboutMenu.add_command(label="Help", command = lambda:self.on_help())
        self.help_index = 2
        self.menubar.add_cascade(label="Help", menu=self.aboutMenu)
        root.config(menu=self.menubar)

        # Part Number Entry Field
        self.part_num_label = Label(self.right_frame, text="Part Number")
        self.part_num_label.pack(side=TOP, anchor=W, fill=X, expand=YES)
        self.part_num_string=StringVar()
        self.part_num_text = Entry(self.right_frame, textvariable=self.part_num_string)
        self.part_num_text.pack(side=TOP, anchor=W, fill=X, expand=YES)

        # Locate Button
        self.locate_btn = Button(self.right_frame, text="Locate", command=self.on_locate_btn)
        self.locate_btn.pack(side=TOP, anchor=W, fill=X, expand=YES)
        
        # Cancel Button
        self.clear_btn = Button(self.right_frame, text="Clear", command=self.on_clear_btn)
        self.clear_btn.pack(side=TOP, anchor=W, fill=X, expand=YES)
        
        # Commit Button
        self.commit_btn = Button(self.right_frame, text="-", command=self.on_commit_btn)
        self.commit_btn.pack(side=TOP, anchor=W, fill=X, expand=YES)
 
        # Status Bar
        self.status_labelframe = LabelFrame(self, text="Status")
        self.status_labelframe.pack(side=BOTTOM, fill=X, expand=YES, pady=4, padx=6)
        self.status_frame = Frame(self.status_labelframe);
        self.status_frame.pack(side=TOP, fill=X, expand=YES, padx=6)
        self.status = self.StatusBar(self.status_frame, self)
        self.status.set("Select Database")

        # Part Info Text Box

        self.part_label = StringVar()
        self.part_info_label = Label(self.left_frame, textvariable=self.part_label)
        self.part_info_label.pack(side=TOP, fill=X, expand=YES)
        self.part_label.set("Part Info")
        self.part_info_tree = Treeview(self.left_frame)
        self.part_info_tree.pack(side=LEFT, anchor=W, fill=X, expand=YES)
        self.part_info_tree.bind('<<TreeviewSelect>>', self.on_select_new_field)
        self.part_info_tree.bind('<Control-c>', self.on_copy_element)
        self.part_info_tree['show'] = 'headings'
        self.part_info_tree['columns'] = ('parameter', 'value')
        self.part_info_tree.heading('parameter', text='Parameter Name')
        self.part_info_tree.heading('value', text='Parameter Value')
        self.part_info_tree.column('parameter', width=260)
        self.part_info_tree.column('value', width=350)
        self.scrollbar = Scrollbar(self.left_frame, orient='vertical', command=self.part_info_tree.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y, expand=YES, anchor=E)
        self.part_info_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.config(command=self.part_info_tree.yview)
        treefontname = ttk.Style().lookup("Treeview","font")
        sysbold = font.nametofont(treefontname).copy()
        sysbold.config(weight='bold')
        self.part_info_tree.tag_configure('boldfont', font=sysbold)        
        self.part_info_tree.tag_configure('hilite', background='azure')
        self.element_name = StringVar()
        self.element_label = Label(self.element_frame, textvariable=self.element_name, width=30, anchor=W, justify=LEFT)
        self.element_label.pack(side=LEFT, anchor=W, fill=X, expand=YES, pady=4)
        self.element_value = StringVar()
        self.element_entry = Entry(self.element_frame, width=50, textvariable=self.element_value)
        self.element_entry.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.default_color = self.element_entry.cget('background')

        self.element_update = Button(self.element_frame, text="Update", command=self.on_update_element, state=DISABLED)
        self.element_update.pack(side=LEFT, fill=X, expand=YES, pady=4)
        self.element_cancel = Button(self.element_frame, text="Cancel", command=self.on_clear_element)
        self.element_cancel.pack(side=LEFT, fill=X, expand=YES, pady=4)
        

Config().parse_file()
FAVICON = "../assets/favicon.ico"

root = Tk()
root.title("Partlocater")
root.iconbitmap(FAVICON)
root.resizable(False, False)
app = Application(master=root)
app.mainloop()
try:
    root.destroy()
except Exception:
    quit()