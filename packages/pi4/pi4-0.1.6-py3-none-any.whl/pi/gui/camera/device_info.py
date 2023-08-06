from pathlib import Path
from tkinter import PhotoImage
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
import os


PATH = Path(__file__).parent

class DeviceInfoFrame(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)
        self.master = master
        
        self.images = [
            PhotoImage(
                name='reset', 
                file=PATH / 'reset.png'),            
            PhotoImage(
                name='submit', 
                file=PATH / 'submit.png'),            
            PhotoImage(
                name='buy', 
                file=PATH / 'buy.png'),
            PhotoImage(
                name='device', 
                file=PATH / 'fundus-camera.png')
        ]

        for i in range(1):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)

        # column 1
        col1 = ttk.Frame(self, padding=10)
        col1.grid(row=0, column=0, sticky=NSEW)

        # device info
        dev_info = ttk.Labelframe(col1, text='设备信息', padding=10)
        dev_info.pack(side=TOP, fill=BOTH, expand=YES)

        # header
        dev_info_header = ttk.Frame(dev_info, padding=5)
        dev_info_header.pack(fill=X)

        btn = ttk.Button(
            master=dev_info_header,
            image='reset',
            bootstyle=LINK,
            command=self.reset_callback
        )
        btn.pack(side=LEFT)

        lbl = ttk.Label(dev_info_header, text='Model 2022, 2xAA Batteries')
        lbl.pack(side=LEFT, fill=X, padx=15)

        btn = ttk.Button(
            master=dev_info_header,
            image='submit',
            bootstyle=LINK,
            command=self.tech_callback
        )
        btn.pack(side=LEFT)

        # image
        ttk.Label(dev_info, image='device').pack(fill=X)

        # progressbar
        pb = ttk.Progressbar(dev_info, value=66, bootstyle=(SUCCESS))
        pb.pack(fill=X, pady=5, padx=5)
        ttk.Label(pb, text='80%', bootstyle=(SUCCESS, INVERSE)).pack()

        # progress message
        self.setvar('progress', '重在充电')
        lbl = ttk.Label(
            master=dev_info,
            textvariable='progress',
            font='Helvetica 8',
            anchor=CENTER
        )
        # lbl.pack(fill=X)

        # col2 = ttk.Frame(self, padding=10)
        # col2.grid(row=0, column=1, sticky=NSEW)

        # licence info
        lic_info = ttk.Labelframe(col1, text='许可信息', padding=20)
        lic_info.pack(side=TOP, fill=BOTH, expand=YES, pady=(10, 0))
        lic_info.rowconfigure(0, weight=1)
        lic_info.columnconfigure(0, weight=2)

        lic_title = ttk.Label(
            master=lic_info,
            text='Trial Version, 28 days left',
            anchor=CENTER
        )
        lic_title.pack(fill=X, pady=(0, 20))

        lbl = ttk.Label(
            master=lic_info,
            text='serial number:',
            anchor=CENTER,
            font='Helvetica 8'
        )
        lbl.pack(fill=X)
        self.setvar('license', 'dtMM2-XYZGHIJKLMN3')

        lic_num = ttk.Label(
            master=lic_info,
            textvariable='license',
            bootstyle=PRIMARY,
            anchor=CENTER
        )
        lic_num.pack(fill=X, pady=(0, 20))

        buy_now = ttk.Button(
            master=lic_info,
            image='buy',
            padding=7,
            command=self.contact_callback
        )
        buy_now.pack(side=LEFT, padx=10, fill=X, expand=YES)

        btn = ttk.Button(
            master=lic_info,
            text = '返回',
            padding=10,
            command=self.master.destroy
        )
        btn.pack(side=LEFT, padx=10, fill=X, expand=YES)

    def reset_callback(self):

        if self.master.attributes('-fullscreen'):
            toast = ToastNotification(
                title='reset',
                message='即将重启...', 
                duration=1000,
            )
            toast.show_toast()
            os.system("shutdown /t 1")
        else:
            res = Messagebox.okcancel(
                title='设备重启', 
                message="确定重启？"
            )

            if res == 'OK':
                os.system("shutdown /t 1")

    def tech_callback(self):
        if self.master.attributes('-fullscreen'):
            toast = ToastNotification(
                title='技术咨询',
                message='服务热线 10086', 
                duration=1000,
            )
            toast.show_toast()
        else:
            Messagebox.ok(
                title='技术咨询', 
                message="服务热线 10086"
            )

    def contact_callback(self):
        self.tech_callback()

if __name__ == '__main__':

    app = ttk.Window("检眼镜", "yeti")
    DeviceInfoFrame(app)
    app.mainloop()
