# since python 3.x, Tkinter is renamed to tkinter

import tkinter 
import cv2
from PIL import Image, ImageTk
from tkinter import messagebox

cap = cv2.VideoCapture(0)
INTERVAL = 100 # ms

class App(tkinter.Tk):
    
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.label = tkinter.Label() #(text="CAMERA LIVEVIEW", compound="top")
        self.label.pack(side="top", padx=8, pady=8)
        self.iteration=0

        self.btn = tkinter.Button(text="CAPTURE", compound="top", command= self.capture_image)
        self.btn.pack(side="top", padx=8, pady=8)
        
        self.UpdateImage(INTERVAL)        

    def capture_image(self):
        self.pil_image.save(str(self.iteration) + '.jpg')
        # messagebox.showinfo("Message","Hey There! I hope you are doing well.")

    def UpdateImage(self, delay, event=None):
        # this is merely so the display changes even though the image doesn't
        self.iteration += 1

        self.pil_image, self.image = self.get_image()
        self.label.configure(image=self.image) # , text="Iteration %s" % self.iteration)

        # reschedule to run again in 1 second
        self.after(delay, self.UpdateImage, INTERVAL) # frame rate

    def get_image(self):

        cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image = img)

        return img, imgtk

        # this is where you get your image and convert it to 
        # a Tk PhotoImage. For demonstration purposes I'll
        # just return a static image
        data = '''
            R0lGODlhIAAgALMAAAAAAAAAgHCAkC6LV76+vvXeswD/ANzc3DLNMubm+v/6zS9PT6Ai8P8A////
            /////yH5BAEAAAkALAAAAAAgACAAAAS00MlJq7046803AF3ofAYYfh8GIEvpoUZcmtOKAO5rLMva
            0rYVKqX5IEq3XDAZo1GGiOhw5rtJc09cVGo7orYwYtYo3d4+DBxJWuSCAQ30+vNTGcxnOIARj3eT
            YhJDQ3woDGl7foNiKBV7aYeEkHEignKFkk4ciYaImJqbkZ+PjZUjaJOElKanqJyRrJyZgSKkokOs
            NYa2q7mcirC5I5FofsK6hcHHgsSgx4a9yzXK0rrV19gRADs=
        '''
        image = tkinter.PhotoImage(data=data)
        return image

if __name__ == "__main__":
    app=App()
    app.attributes('-fullscreen', True)
    app.mainloop()