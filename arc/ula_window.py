import os
import tkinter as tk
from tkinter import *
import multiprocessing
import subprocess

# Custom Libraries
try:
    from arc import gnu_str
    from arc import install
    from arc import get_all_files
except Exception:
    import gnu_str
    import install
    import get_all_files


class Main(object):
    """GUI for the ULA of the  Antecedent Rainfall Calculator"""

    def __init__(self, downloader=False):
        self.downloader = downloader
        self.ula_ccepted = False
        # Find Root Folder
        module_path = os.path.dirname(os.path.realpath(__file__))
        root_folder = os.path.split(module_path)[0]

        # Create Master Frame
        self.master=tk.Tk()
        self.master.geometry("725x475+431+132")
        self.master.minsize(120, 1)
        self.master.maxsize(1370, 749)
        self.master.resizable(1, 1)
        self.master.title("User Licence Agrement - Antecedent Rainfall Calculator")

        # Set Window Icon
        try:
            graph_icon_file = '{}\\GUI Images\\Graph.ico'.format(root_folder)
            self.master.wm_iconbitmap(graph_icon_file)
        except Exception:
            graph_icon_file = os.path.join(sys.prefix, 'images\\Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)


        self.label_1=tk.Label(self.master,
                        text="Please review and accept the user licence agrement to proceed",
                        font='Helvetica 13 bold')
        self.label_1.grid(row=0, column=0, padx=0, pady=0)
        #label2=Label(self.master, text="accept the licence agrement.                                                                                                   ",font='Helvetica 8 bold')
        #label2.grid(row=1, column=0)


        self.agreement_text = Text(self.master, height=20, width=79) # creating a textbox for getting address
        self.scrollbar = Scrollbar(self.master)  # making a scrolbar with entry test text field
        self.agreement_text.config(yscrollcommand=self.scrollbar.set)  # setting scrolbar to y-axis
        self.scrollbar.config(command=self.agreement_text.yview)  # setting the scrolbar to entry test textbox
        self.agreement_text.insert(END, gnu_str.GNU_GPL_v3) # Inserting the License 
        self.agreement_text.config(state=DISABLED)
        self.agreement_text.grid(column=0, row=2, sticky='W', padx=30) # set entry to Specific column of bottom frame grid
        self.scrollbar.grid(column=1, row=2, sticky=N + S + W) # set self.scrollbar to Specific column of bottom frame grid




        self.f1 = tk.Frame(self.master)

        self.f1.grid(row=3, column=0, sticky="nsew")

        self.var1 = IntVar()

        self.checkbox=Checkbutton(self.f1,
                        text="I have read and accept the terms of the license agreement",
                        variable=self.var1,
                        command=self.checkboxChecked)

        self.checkbox.grid(row=0,column=0,padx=25,pady=10)


        self.f2 = tk.Frame(self.master)
        self.f2.grid(row=4, column=0, sticky="nsew")

        self.button_accept=Button(self.f2,
                                text="Submit",
                                state=DISABLED,
                                command=self.click_accept_button)
        self.button_cancel=Button(self.f2,text="Cancel",command=self.click_cancel_button)
        self.button_accept.grid(row=0,column=0,padx=110)
        self.button_cancel.grid(row=0,column=2,padx=0)

        # Configure rows and columns
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # a trick to activate the window (on windows 7)
        self.master.deiconify()

    def checkboxChecked(self):
        if self.var1.get()==1:
            self.button_accept.config(state=NORMAL)
        else:
            self.button_accept.config(state=DISABLED)

    def click_accept_button(self):
        self.ula_ccepted = False
        self.master.destroy() # Close ULA window
        if self.downloader:
            get_all_files.downloader()
            install.create_shortcut_frozen() # Create Desktop Shortcut
            module_folder = os.path.dirname(os.path.realpath(__file__))
            root_folder = os.path.split(module_folder)[0]
            main_exe_path = '"{}\\arc_ex.exe"'.format(root_folder)
            subprocess.Popen(main_exe_path, shell=True)
            sys.exit()
        return True

    def click_cancel_button(self):
        self.ula_ccepted = True
        self.master.destroy() # Close ULA window
        return False

    def run(self):
        self.master.mainloop()

if __name__ == '__main__':
    APP = Main()
    APP.run()
