#Import the Tkinter library
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

from App import enroll_fp, verify_fp

import PyPDF2
from tkinter.filedialog import askopenfile
from functions import display_logo, display_textbox, display_icon, display_images, extract_images,  resize_image, copy_text, save_all, save_image


path = "" # path of the selected image
result = ["",""] # match result of the selected image

selected_enroll_img_name = "" 
selected_enroll_img_id = "-1" 

selected_verify_img_name = "" 
selected_verify_img_id = "-1" 

#Create an instance of Tkinter frame
root = Tk()

#Define the geometry
root.geometry('+%d+%d'%(350,10))
root.title("Biometric encryption")

# #header area - logo & browse button
# header = Frame(root, width=800, height=175, bg="white")
# header.grid(columnspan=3, rowspan=2, row=0)

# #main content area - text and image extraction
# main_content = Frame(root, width=800, height=250, bg="#20bebe")
# main_content.grid(columnspan=3, rowspan=2, row=4)

# #BEGIN INITIAL APP COMPONENTS
# display_logo('logo.png', 0, 0)

# #instructions
# instructions = Label(root, text="Select a PDF file", font=("Raleway", 10), bg="white")
# instructions.grid(column=0, row=0, sticky=SE, padx=75, pady=5)

# image file selection function
def select_enrolling_file():
   path= filedialog.askopenfilename(title="Select an Image", filetypes=(('image    files','*.jpg'),('all files','*.*')))
   img= Image.open(path)
   img=ImageTk.PhotoImage(img)
   label= Label(root, image= img)
   label.image= img
   label.pack()
   
   selected_enroll_img_name = path.split("/")[-1].split(".")[0]
   selected_enroll_img_id = selected_enroll_img_name.split("p")[-1]
   
   enroll_fp(selected_enroll_img_id)
   
   # # run fingerprint matching function
   # result = run_app_gui(path)
   
   # display matched image details
   Label(root, text="Selected image : "+ selected_enroll_img_name, font=('Caveat 13')).pack(pady=20)
   # Label(root, text="BEST MATCH: "+ result[0], font=('Caveat 13')).pack(pady=20)
   # Label(root, text="SCORE: "+ str(result[1]), font=('Caveat 13')).pack(pady=20)
   
   Label(root, text="Click the Button below to select an Fingerprint to verify", font=('Caveat 15 bold')).pack(pady=20)
   button2= ttk.Button(root, text="Select to Fingerprint", command= select_verifying_file)
   button2.pack(ipadx=5, pady=15)
   
def select_verifying_file():
   path= filedialog.askopenfilename(title="Select an Image", filetypes=(('image    files','*.jpg'),('all files','*.*')))
   img= Image.open(path)
   img=ImageTk.PhotoImage(img)
   label= Label(root, image= img)
   label.image= img
   label.pack()
   
   selected_verify_img_name = path.split("/")[-1].split(".")[0]
   selected_verify_img_id = selected_verify_img_name.split("p")[-1]
   
   # # run fingerprint matching function
   # result = run_app_gui(path)
   
   # display matched image details
   Label(root, text="Selected image : "+ selected_verify_img_name, font=('Caveat 13')).pack(pady=20)
   # Label(root, text="BEST MATCH: "+ result[0], font=('Caveat 13')).pack(pady=20)
   # Label(root, text="SCORE: "+ str(result[1]), font=('Caveat 13')).pack(pady=20)
   verified_data(selected_verify_img_id)
#    button3= ttk.Button(root, text="Verify", command= verified_data(selected_verify_img_id))
#    button3.pack(ipadx=5, pady=15)
   
def verified_data(id):
   result = verify_fp(id)
   
   if(result):
      Label(root, text="Verification successful !!", font=('Caveat 13')).pack(pady=20)
   else:
      Label(root, text="Verification failed !!", font=('Caveat 13')).pack(pady=20)

   
#Create a label and a Button to Open the dialog
Label(root, text="Click the Button below to select an Fingerprint to enroll", font=('Caveat 15 bold')).pack(pady=20)
button1= ttk.Button(root, text="Select a Fingerprint", command= select_enrolling_file)
button1.pack(ipadx=5, pady=15)


root.mainloop()


