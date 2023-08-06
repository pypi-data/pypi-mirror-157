import sys
import os.path
from pathlib import Path
from datetime import datetime

from tkinter import PhotoImage
from ttkbootstrap.toast import ToastNotification
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Emoji

import cv2
from PIL import Image, ImageTk

import webbrowser
from random import choice

if __package__:
    from .files_earch_frame import FileSearchFrame
    from .device_info import DeviceInfoFrame
else:
    sys.path.append(os.path.dirname(__file__))
    from files_earch_frame import FileSearchFrame
    from device_info import DeviceInfoFrame

cap = cv2.VideoCapture(0)
INTERVAL = 100 # ms
SAVE_DIR = 'ocam_captures/'
PADDING = 9
DEFAULT_WINSIZE = '500x400'
ENABLE_FULLSCREEN = False
PATH = Path(__file__).parent

def get_timestamp():   

    now = datetime.now() # current date and time

    dt = now.strftime("%Y%m%d%H%M%S")
    return dt

class MainApp(ttk.Frame):

    def __init__(self, master):

        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)
        self.hdr_var = ttk.StringVar()
        
        self.images = [
            PhotoImage(
                name='folder', 
                file=PATH / 'folder2.png'),            
            PhotoImage(
                name='cloud', 
                file=PATH / 'cloud.png'),            
            PhotoImage(
                name='ai', 
                file=PATH / 'ai2.png'),
            PhotoImage(
                name='camera', 
                file=PATH / 'camera2.png'),
            PhotoImage(
                name='brush', 
                file=PATH / 'brush.png'),
            PhotoImage(
                name='close', 
                file=PATH / 'close.png'),
            PhotoImage(
                name='i', 
                file=PATH / 'i.png'),
            PhotoImage(
                name='hibernate', 
                file=PATH / 'hibernate.png')
        ]

        # self.create_header() # if you need a headline
        self.create_liveview_window()
        self.create_buttonbox()
        self.UpdateImage(INTERVAL)
    
    def create_header(self):
        """The application header to display user messages"""
        self.hdr_var.set("进入拍摄模式")

        lbl = ttk.Label(
            master=self, 
            textvariable=self.hdr_var, 
            bootstyle=(LIGHT, INVERSE),
            padding=PADDING
        )
        lbl.pack(fill=X, expand=YES)

    def create_liveview_window(self):
        """Create frame to contain media"""

        # img_path = Path(__file__).parent / 'assets/mp_background.png'
        # self.demo_media = ttk.PhotoImage(file=img_path)
        self.media = ttk.Label(self) # , image=self.demo_media)
        self.media.pack(fill=BOTH, expand=YES)
    
    def create_buttonbox(self):
        """Create buttonbox with media controls"""

        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES)
        ttk.Style().configure('TButton', font="-size 14")

        '''
        btn = ttk.Button(
            master=container,
            text=Emoji.get('BOOKMARK TABS'),
            padding=10,
            command = self.sde
        )
        btn.pack(side=LEFT, fill=X, expand=YES)
        '''
        
        btn = ttk.Button(
            master=container,
            # text = Emoji.get('CAMERA WITH FLASH'), # camera '拍摄',
            image='camera',
            padding=PADDING,
            command= self.capture_image
        )
        btn.pack(side=LEFT, fill=X, expand=YES)  

        btn = ttk.Button(
            master=container,
            # text=Emoji.get('open file folder'),
            image='folder',
            padding=PADDING,
            command= self.open_save_folder
        )
        btn.pack(side=LEFT, fill=X, expand=YES)          

        '''
        btn = ttk.Button(
            master=container,
            text=Emoji.get('cloud'),
            bootstyle=SECONDARY,
            padding=PADDING,
            command = self.upload_to_cloud
        )
        btn.pack(side=LEFT, fill=X, expand=YES)             

        btn = ttk.Button(
            master=container,
            # text='AI', # =Emoji.get('brain'),
            image='ai',
            padding=PADDING,
            command = self.launch_ai
        )
        btn.pack(side=LEFT, fill=X, expand=YES)   
        '''
        
        
        btn = ttk.Button(
            master=container,
            # text=Emoji.get('LOWER LEFT PAINTBRUSH'),
            image='brush',
            padding=PADDING,
            command = self.change_style
        )
        btn.pack(side=LEFT, fill=X, expand=YES)   

        btn = ttk.Button(
            master=container,
            # text=Emoji.get('INFORMATION SOURCE'),
            image='i',
            padding=PADDING,
            command = self.device_info
        )
        btn.pack(side=LEFT, fill=X, expand=YES) 

        btn = ttk.Button(
            master=container,
            # text=Emoji.get('NEGATIVE SQUARED CROSS MARK'),
            image='close',
            padding=PADDING,
            command = self.quit # destroy is not enough
        )
        btn.pack(side=LEFT, fill=X, expand=YES)   

        '''
        btn = ttk.Button(
            master=container,
            # text=Emoji.get('NEGATIVE SQUARED CROSS MARK'),
            image='hibernate',
            padding=PADDING,
            command = self.quit # destroy is not enough
        )
        btn.pack(side=LEFT, fill=X, expand=YES)   
        '''

    def UpdateImage(self, delay, event=None):

        self.pil_image, self.image = self.get_image()
        self.media.configure(image=self.image) # , text="Iteration %s" % self.iteration)

        # reschedule to run again in 1 second
        self.after(delay, self.UpdateImage, INTERVAL) # frame rate

    def get_image(self):

        cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)        

        # Resize the image using resize() method
        # print(self.winfo_width() , self.winfo_height())
        resize_image = img.resize((self.winfo_width() , max(self.winfo_height() - 50, 1) ))
        imgtk = ImageTk.PhotoImage(resize_image)

        return img, imgtk

    ########### BUTTON CLICK EVENT HANDLER #############
    def capture_image(self):

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        fn = SAVE_DIR + get_timestamp() + '.jpg'
        self.pil_image.save( fn )
        # messagebox.showinfo("Message","Hey There! I hope you are doing well.")
        
        toast = ToastNotification(
            title="图片保存成果",
            message="保存路径为" + fn,
            duration=1000,
        )
        toast.show_toast()

    def upload_to_cloud(self):

        toast = ToastNotification(
            title="同步至云端",
            message="开发中, 功能尚未开放",
            duration=2000,
        )
        toast.show_toast()

    def open_save_folder(self):

        # import subprocess
        # subprocess.Popen("./" + SAVE_DIR + "/")
        # webbrowser.open(("./" + SAVE_DIR + "/"))    

        fapp= ttk.Toplevel(app)
        fapp.geometry(DEFAULT_WINSIZE)
        fapp.attributes('-fullscreen', ENABLE_FULLSCREEN)
        fapp.title("拍摄文件一览")
        FileSearchFrame(fapp, SAVE_DIR, fix_path=True, init=True)

    def device_info(self):

        dapp= ttk.Toplevel(app)
        dapp.geometry(DEFAULT_WINSIZE)
        dapp.attributes('-fullscreen', ENABLE_FULLSCREEN)
        dapp.title("设备信息")
        DeviceInfoFrame(dapp)

    def sde(self):
     
        # Toplevel object which will
        # be treated as a new windowcls
        newWindow = ttk.Toplevel(app)
    
        # sets the title of the
        # Toplevel widget
        newWindow.title("Data Entry")
    
        # sets the geometry of toplevel
        newWindow.geometry("400x300")
    
        # A Label widget to show in toplevel
        ttk.Label(newWindow,
            text ="This is a new window").pack()

    def change_style(self):
        style = ttk.Style()
        theme = choice(style.theme_names())
        style.theme_use(theme)   

    def launch_ai(self):        
        os.system('python -m tfjsa.gui')

def key_handler(event):
   app.destroy()
   # sys.exit()

if __name__ == '__main__':

    app = ttk.Window("oCam", "yeti")
    app.geometry(DEFAULT_WINSIZE)
    app.attributes('-fullscreen', ENABLE_FULLSCREEN)
    mp = MainApp(app)

    # use either q or esc to close window
    app.bind('<q>', key_handler)
    app.bind('<Escape>', lambda event: sys.exit())

    app.mainloop()