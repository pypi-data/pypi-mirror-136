from tkinter import *
from playsound import playsound
class Scene:
    def up(e):
	display.move(spr,0,-20)
    def down(e):
	display.move(spr,0,20)
    def left(e):
	display.move(spr,-20,0)
    def right(e):
	display.move(spr,20,0)
    def __init__(self,title,hw):
	self.title = title
	global root
	root = Tk()
	root.title(self.title)
	root.bind('<Up>',Scene.up)
	root.bind('<Down>',Scene.down)
	root.bind('<Left>',Scene.left)
	root.bind('<Right>',Scene.right)
    def tweak(self,title,hw):
	self.title = title
	root.title(self.title)
	root.geometry(hw.replace(':','x'))
    def sound(path):
	playsound(path)
    def run(self):
	root.mainloop()
    def quit(self):
	root.destroy()
class Area:
    def __init__(self,hw,bg):
	self.height = hw.split(':')[0]
	self.width = hw.split(':')[1]
	self.bg = bg
	global display
	display = Canvas(height=self.height,width=self.width,bg=self.bg)
	display.pack()
    def tweak(self,hw):
	self.height = hw.split(':')[0]
	self.width =  hw.split(':')[1]
class Sprite:
    def skin(self,img,name):
        self.img = PhotoImage(file=img)
        self.sprname = name
    def add(self,hw):
	global spr
	spr = display.create_image(hw.split(':')[0],hw.split(':')[1],image=self.img)
    def teleport(self,xy):
	x = xy.split(':')[0]
	y = xy.split(':')[1]
	display.move(spr,abs(display.coords(spr),x),abs(display.coords(spr),y))
