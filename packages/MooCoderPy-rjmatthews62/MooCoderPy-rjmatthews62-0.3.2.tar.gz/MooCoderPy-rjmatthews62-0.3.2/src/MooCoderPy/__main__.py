#!/usr/bin/python3

from tkinter import *
from tkinter import filedialog
from tkinter import ttk 
from tkinter import font
from tkinter import scrolledtext
from tkinter import simpledialog
import os,sys
from turtle import width
from MooCoderPy.SettingsDialog import getConfig
# Stupid packaging messes with paths...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print("SCRIPT_DIR=",SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

from ScrollText import *
from TerminalWindow import *
import SettingsDialog
import configparser
 
def doOpen():
    tf = filedialog.askopenfilename(
        initialdir="C:/td/srtmoo/", 
        title="Open Text file", 
        filetypes=(("Text Files", "*.moo"),)
        )
    if tf:
        with open(tf,"r") as f:
            data=f.read();
            memo1.delete("1.0",END)
            memo1.insert("1.0",data)

def doClose():
    tw.disconnect()
    tw.saveSettings()
    root.quit()    

def doConnect():
    inifile=SettingsDialog.getConfig()
    server=inifile["settings"]["Server"]
    connectstr=inifile["settings"]["Connect"]
    (server,port)=server.split(":")
    tw.connectString=connectstr
    tw.doConnect(server,int(port))

def doDisconnect():
    tw.disconnect()

def doSettings():
    SettingsDialog.SettingsDialog(root,title="Server Configuration")

def handlecapture(text:str, name:str):
    memo1.delete("1.0","end")
    memo1.insert("1.0",text)
    nb.select(ff)
    nb.tab(ff,text=name)

def doupdate(event=None):
    global ff
    re=tw.currentPage()
    if (re and re.tabtype==1):
        tw.docompile(re)
    else:
        t=nb.nametowidget(nb.select())
        if (t==ff):
            if tw.doupdate(memo1.get("1.0","end")):
                nb.select(tw)

def doTabChanged(event):
    tabname=nb.tab("current","text")
    if (tabname=="Terminal"):
        tw.sendEntry.focus()

def donewtab(event=None):
    """Load a verb into a new tab"""
    verb=simpledialog.askstring("Verb","Enter Object:Verb")
    if (verb):
        tw.loadVerb(verb)

def viewStack(event=None):
    """Make stack visible."""
    global stackloaded
    mainpack(not stackloaded)

def buildMenu():
    menubar=Menu(root)
    filemenu=Menu(menubar,tearoff=0)
    filemenu.add_command(label="Open", command=doOpen,underline=0)
    filemenu.add_command(label="Connect", command=doConnect,underline=0)
    filemenu.add_command(label="Disconnect", command=doDisconnect, underline=0)
    filemenu.add_command(label="Exit", command=doClose,underline=1)
    settingmenu=Menu(menubar,tearoff=0)
    settingmenu.add_command(label="Server Config",command=doSettings, underline=0)
    editmenu=Menu(menubar,tearoff=0)
    editmenu.add_command(label="Send Update F5", command=doupdate, underline=0)
    root.bind("<F5>",doupdate)
    projectmenu=Menu(menubar,tearoff=0)
    projectmenu.add_command(label="New Tab Ctrl+N",command=donewtab,underline=0)
    projectmenu.add_command(label="Get Verbs Ctrl+Shift+V",command=tw.getVerbs,underline=0)
    projectmenu.add_command(label="Clear Project",command=tw.clearProject,underline=0)
    
    root.bind("<Control-Shift-Key-V>",tw.getVerbs)
    root.bind("<Control-Shift-Key-v>",tw.getVerbs)
    
    # Apparently the key binding is case sensitive...
    root.bind("<Control-Key-N>",donewtab)
    root.bind("<Control-Key-n>",donewtab)
    menubar.add_cascade(label="File",menu=filemenu, underline=0)
    menubar.add_cascade(label="Settings", menu=settingmenu, underline=0)
    menubar.add_cascade(label="Edit", menu=editmenu, underline=0)
    menubar.add_cascade(label="Project",menu=projectmenu, underline=0)
    viewmenu=Menu(menubar,tearoff=0)
    viewmenu.add_command(label="Stack", command=viewStack,underline=0)
    menubar.add_cascade(label="View",menu=viewmenu,underline=0)
    root.config(menu=menubar)

def mainpack(usestack:bool):
    """Pack the main window so it's possible to hide and reload stack"""
    global stackloaded
    nb.pack_forget()
    stack.pack_forget()
    nb.pack(side=LEFT, fill=Y)
    if usestack:
        stack.pack(side=LEFT,fill=Y)
    nb.pack(fill=BOTH,expand=True)
    stackloaded=usestack

def loadSettings():
    ifile=SettingsDialog.getConfig()
    tw.dumpobject=ifile['settings'].get('LastDump',"")

def doVerbDblClick(event=None):
    nd=verblist.item(verblist.selection())
    tw.loadVerb(nd["text"]+":"+nd["values"][1])

def doStackClick(event:Event):
    tw.gotoError(stack)

if not("__VERSION+__" in globals()):
    import importlib.metadata
    __VERSION__ = importlib.metadata.version('MooCoderPy-rjmatthews62')

print("MooCoderPy",__VERSION__)
root = Tk()
try:
    root.iconbitmap(SCRIPT_DIR+"/moocoder.ico")
except:
    print("Couldn't find icon file. Trying png")
    try:
        ico=PhotoImage(file=SCRIPT_DIR+"/moocoder.png")
        root.iconphoto(False,ico)
    except:
        print("Didn't need that dumb icon anyway.")

myfont=font.Font(name="Arial",size=10)
root.option_add( "*font", myfont)
root.title("MooCoderPy "+__VERSION__)
root.protocol("WM_DELETE_WINDOW",doClose)
stack=Text(root,width=50)
stack.bind("<Double-Button-1>",doStackClick)
nb=ttk.Notebook(root)
mainpack(False)

ff=Frame(nb)
tw=TerminalWindow(nb,background="black",foreground="white",font=("Courier",12,"bold"),insertbackground="white")
tw.normalfont=myfont
tw.setstackvisible=mainpack
tw.stack=stack
nb.add(tw,text="Terminal")
nb.add(ff,text="Edit")
memo1 = scrolledtext.ScrolledText(ff,insertbackground="white");
memo1.config({"background":"black","foreground":"white","font":("Courier",12,"bold")})
memo1.pack(fill=BOTH,expand=True)

verbframe=Frame(nb)
nb.add(verbframe,text="Verbs")
verblist=ttk.Treeview(verbframe,columns=("c1","c2","c3","c4"))
verblist.heading("#0",text="Obj")
verblist.heading("c1",text="Name")
verblist.heading("c2",text="Verb")
verblist.heading("c3",text="Args")
verblist.heading("c4",text="Detail")
verblist.column("#0",stretch=False,width=50)
for i in range(3):
    verblist.column(i,stretch=False,width=80)
verblist.pack(fill=BOTH, expand=True)
verblist.bind("<Double-Button-1>",doVerbDblClick)
verblist.style=ttk.Style(verblist)
verblist.style.configure("Treeview",font=myfont)
verblist.style.configure("Treeview.Heading",font=myfont)
print(verblist.style)
nb.enable_traversal()
tw.capturefunc=handlecapture
tw.lvVerbs=verblist
nb.bind("<<NotebookTabChanged>>",func=doTabChanged)
nb.select(tw)
tw.pages=nb
buildMenu()
loadSettings()
try:
    root.state("zoomed") # Works in windows (and MacOs?)
except:
    root.attributes("-zoomed",True) # Works for linux

root.mainloop()
print("Done")

