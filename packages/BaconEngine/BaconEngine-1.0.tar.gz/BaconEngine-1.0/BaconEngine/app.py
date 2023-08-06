from tkinter import *
class Window:
    def __init__(self,title,hw):
	global root
	root = Tk()
	root.title(title)
	root.geometry(hw.split(':')[0]+'x'+hw.split(':')[1])
	root.mainloop()
   def tweak(self,title,hw):
        root.title(title)
        root.geometry(hw.split(':')[0]+'x'+hw.split(':')[1])
        root.mainloop()
   def add(name):
	exec(name+'.pack()')
class Widget:
    def TextInput():
	text = Entry()
    def Display(_bg='white'):
	disp = Canvas(bg=_bg)
    def Button(_text,onclick):
	btn = Button(label=_text,command=onclick)
    def Text(_text):
	lbl = Label(text=_text)
