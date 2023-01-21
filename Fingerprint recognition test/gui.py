#Import the Tkinter library
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

from App import run_app_gui

path = "" # path of the selected image
result = ["",""] # match result of the selected image

#Create an instance of Tkinter frame
win = Tk()

#Define the geometry
win.geometry("750x350")
win.title("Image Gallery")

# image file selection function
def select_file():
   path= filedialog.askopenfilename(title="Select an Image", filetypes=(('image    files','*.jpg'),('all files','*.*')))
   img= Image.open(path)
   img=ImageTk.PhotoImage(img)
   label= Label(win, image= img)
   label.image= img
   label.pack()
   
   # run fingerprint matching function
   result = run_app_gui(path)
   
   # display matched image details
   Label(win, text="BEST MATCH: "+ result[0], font=('Caveat 13')).pack(pady=20)
   Label(win, text="SCORE: "+ str(result[1]), font=('Caveat 13')).pack(pady=20)
   
#Create a label and a Button to Open the dialog
Label(win, text="Click the Button below to select an Image", font=('Caveat 15 bold')).pack(pady=20)
button= ttk.Button(win, text="Select to Open", command= select_file)
button.pack(ipadx=5, pady=15)
win.mainloop()


