from tkinter import *
from PIL import ImageTk,Image
import tkinter.messagebox
import tkinter.font
import cv2
global img_counter

def camera():
    video = cv2.VideoCapture(0)
    cv2.namedWindow('test')
    img_counter=0
    while True:
        ret, frame = video.read()
        if not ret:
           # print("failed to grab frame")
            break
        cv2.imshow("test", frame)
        k = cv2.waitKey(1)
        if k % 256 == 27:
           # print("escape hit")
            break
        elif k % 256 == 32: # save image
            img = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite(img, frame)
           # print("{} written!".format(img))
            img_counter += 1
            img1 = cv2.imread(img,1)
            cv2.imshow("image", img1)
    video.release()
    cv2.destroyAllWindows()

win=Tk()
win.title("Gui camera")
c=Canvas(win,bg="blue",height=250,width=300)
file=PhotoImage(file="water.png")
backlabel=Label(win,image=file)
backlabel.place(x=0,y=0,relwidth=1,relheight=1)
b1=Button(win,text="OPEN CAMERA",bg="Tomato",bd=12,command=camera)
label=Label(win,text="press SPACE for capturing picture",fg="red",bd=12,font="TimesNewRoman 12")
label1=Label(win,text="press ESC for EXIT!",fg="red",bd=12,font="TimesNewRoman 12")
label1.pack()
label.pack()
b1.pack()
c.pack()
win.mainloop()