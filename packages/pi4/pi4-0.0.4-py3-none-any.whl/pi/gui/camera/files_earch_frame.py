import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
from ttkbootstrap.icons import Emoji

USE_PROGRESSBAR = False

class FileSearchFrame(ttk.Frame):

    queue = Queue()
    searching = False

    def __init__(self, master, _path, init = True, fix_path = False):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        self.master = master

        '''
        Parameters
        ----------
        _path : default target folder
        init : whether perform search on startup
        fix_path : whether allow user to change target folder
        '''
        
        # print(_path)

        # application variables
        if _path is None or _path == '':
            _path = pathlib.Path().absolute().as_posix()

        self.path_var = ttk.StringVar(value=_path)
        self.term_var = ttk.StringVar(value='.jpg')
        self.type_var = ttk.StringVar(value='endswidth')

        # header and labelframe option container
        # option_text = "Complete the form to begin your search"
        # self.option_lf = ttk.Labelframe(self, text=option_text, padding=5) 
        # self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row(fix_path)
        self.create_term_row()
        self.create_type_row()
        self.create_results_view()
        
        if USE_PROGRESSBAR:

            self.progressbar = ttk.Progressbar(
                master=self, 
                mode=INDETERMINATE, 
                bootstyle=(STRIPED, SUCCESS)
            )
            self.progressbar.pack(fill=X, expand=YES)

        self.create_context_menu() # preview | delete | upload, etc.

        if init:
            self.on_search() # perform search on startup

    def create_path_row(self, fix_path = False):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="目录", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row, 
            text="设置目录", 
            command=self.on_browse, 
            width=8,
            state = DISABLED if fix_path else NORMAL
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="关键词", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row, 
            text="检索图片", 
            command=self.on_search, 
            bootstyle=OUTLINE, 
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_type_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="文件类型", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row, 
            text="包含", 
            variable=self.type_var, 
            value="contains"
        )
        contains_opt.pack(side=LEFT)
        
        startswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="前缀", 
            variable=self.type_var, 
            value="startswith"
        )
        startswith_opt.pack(side=LEFT, padx=15)
        
        endswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="后缀", 
            variable=self.type_var, 
            value="endswith"
        )
        endswith_opt.pack(side=LEFT)
        endswith_opt.invoke()

    def clear_results_view(self):
        # for item in self.resultview.get_children():
        #    self.resultview.delete(item)
        self.resultview.delete(*self.resultview.get_children())

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self, 
            bootstyle=INFO, 
            columns=[0, 1, 2, 3, 4],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='文件名', anchor=W)
        self.resultview.heading(1, text='时间戳', anchor=W)
        self.resultview.heading(2, text='类型', anchor=E)
        self.resultview.heading(3, text='大小', anchor=E)
        self.resultview.heading(4, text='路径', anchor=W)
        self.resultview.column(
            column=0, 
            anchor=W, 
            width=utility.scale_size(self, 125), 
            stretch=False
        )
        self.resultview.column(
            column=1, 
            anchor=W, 
            width=utility.scale_size(self, 140), 
            stretch=False
        )
        self.resultview.column(
            column=2, 
            anchor=E, 
            width=utility.scale_size(self, 50), 
            stretch=False
        )
        self.resultview.column(
            column=3, 
            anchor=E, 
            width=utility.scale_size(self, 50), 
            stretch=False
        )
        self.resultview.column(
            column=4, 
            anchor=W, 
            width=utility.scale_size(self, 300)
        )

    def create_context_menu(self):

        PADDING = 9

        container = ttk.Frame(self)
        container.pack(fill=X, expand=YES)
        ttk.Style().configure('TButton', font="-size 14")
        
        btn = ttk.Button(
            master=container,
            text='预览',
            padding=PADDING,
            # command= self.capture_image
        )
        btn.pack(side=LEFT, fill=X, expand=YES)  

        btn = ttk.Button(
            master=container,
            text='删除',
            padding=PADDING,
            # command= self.open_save_folder
        )
        btn.pack(side=LEFT, fill=X, expand=YES)     

        btn = ttk.Button(
            master=container,
            text='上传',
            padding=PADDING,
            state=DISABLED,
            # command= self.open_save_folder
        )
        btn.pack(side=LEFT, fill=X, expand=YES)    

        btn = ttk.Button(
            master=container,
            text='返回',
            padding=PADDING,
            command= self.master.destroy
        )
        btn.pack(side=LEFT, fill=X, expand=YES)         

    def on_browse(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        if path:
            self.path_var.set(path)

    def on_search(self):
        """Search for a term based on the search type"""
        search_term = self.term_var.get()
        search_path = self.path_var.get()
        search_type = self.type_var.get()
        
        if search_term == '':
            return

        self.clear_results_view()
        
        # start search in another thread to prevent UI from locking
        Thread(
            target=FileSearchFrame.file_search, 
            args=(search_term, search_path, search_type), 
            daemon=True
        ).start()

        if USE_PROGRESSBAR:
            self.progressbar.start(10)
        
        iid = self.resultview.insert(
            parent='', 
            index=END, 
        )
        self.resultview.item(iid, open=True)
        self.after(100, lambda: self.check_queue(iid))

    def check_queue(self, iid):
        """Check file queue and print results if not empty"""
        if all([
            FileSearchFrame.searching, 
            not FileSearchFrame.queue.empty()
        ]):
            filename = FileSearchFrame.queue.get()
            self.insert_row(filename, iid)
            self.update_idletasks()
            self.after(100, lambda: self.check_queue(iid))
        elif all([
            not FileSearchFrame.searching,
            not FileSearchFrame.queue.empty()
        ]):
            while not FileSearchFrame.queue.empty():
                filename = FileSearchFrame.queue.get()
                self.insert_row(filename, iid)
            self.update_idletasks()
            if USE_PROGRESSBAR:
                self.progressbar.stop()
        elif all([
            FileSearchFrame.searching,
            FileSearchFrame.queue.empty()
        ]):
            self.after(100, lambda: self.check_queue(iid))
        else:
            if USE_PROGRESSBAR:
                self.progressbar.stop()

    def insert_row(self, file, iid):
        """Insert new row in tree search results"""
        try:
            _stats = file.stat()
            _name = file.stem
            _timestamp = datetime.datetime.fromtimestamp(_stats.st_mtime)
            _modified = _timestamp.strftime(r'%m/%d/%Y %I:%M:%S%p')
            _type = file.suffix.lower()
            _size = FileSearchFrame.convert_size(_stats.st_size)
            _path = file.as_posix()
            iid = self.resultview.insert(
                parent='', 
                index=END, 
                values=(_name, _modified, _type, _size, _path)
            )
            self.resultview.selection_set(iid)
            self.resultview.see(iid)
        except OSError:
            return

    @staticmethod
    def file_search(term, search_path, search_type):
        """Recursively search directory for matching files"""
        FileSearchFrame.set_searching(1)
        if search_type == 'contains':
            FileSearchFrame.find_contains(term, search_path)
        elif search_type == 'startswith':
            FileSearchFrame.find_startswith(term, search_path)
        elif search_type == 'endswith':
            FileSearchFrame.find_endswith(term, search_path)

    @staticmethod
    def find_contains(term, search_path):
        """Find all files that contain the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if term in file:
                        record = pathlib.Path(path) / file
                        FileSearchFrame.queue.put(record)
        FileSearchFrame.set_searching(False)

    @staticmethod
    def find_startswith(term, search_path):
        """Find all files that start with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.startswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchFrame.queue.put(record)
        FileSearchFrame.set_searching(False)

    @staticmethod
    def find_endswith(term, search_path):
        """Find all files that end with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.endswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchFrame.queue.put(record)
        FileSearchFrame.set_searching(False)

    @staticmethod
    def set_searching(state=False):
        """Set searching status"""
        FileSearchFrame.searching = state

    @staticmethod
    def convert_size(size):
        """Convert bytes to mb or kb depending on scale"""
        kb = size // 1000
        mb = round(kb / 1000, 1)
        if kb > 1000:
            return f'{mb:,.1f} MB'
        else:
            return f'{kb:,d} KB'        


if __name__ == '__main__':
  
    app = ttk.Window("文件一览") # , "cyborg")
    FileSearchFrame(app, None)
    app.mainloop()