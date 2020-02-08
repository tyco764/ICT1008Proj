import tkinter as tk
import tkinter.font as tkFont
#from PIL import ImageTk, Image
#import guifunc
#import Seperate_class
#import sampleproject

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Create a container to stack all the frames
        # then raise the one we want visible
        self.filenames = {
            "file1": tk.StringVar(),
            "file2": tk.StringVar(),
            "file3": tk.StringVar()
        }
        self.saved = [0, ]

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Login, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Login")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class Login(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        h1 = tkFont.Font(family="Helvetica", size=28) #weight="bold"
        startlabel = tk.Label(self, text="Start:", font=h1)
        startlabel.place(x=100, y=98)

        self.start = tk.Entry(self, justify='left')
        self.start.focus()
        self.start.place(x=243, y=100, width=250, height=50)

        endlabel = tk.Label(self, text="End:", font=h1)
        endlabel.place(x=110, y=180)

        large_font = ('Verdana', 14)
        self.end = tk.Entry(self, justify='left', font=large_font)
        self.end.place(x=243, y=180, width=250, height=50)
        self.end.bind('<Return>', )
        #lambda event: guifunc.check_password(self, self.user_txt.get(), self.pass_txt.get()))

        self.change_btn = tk.Button(self, text="Search", command=lambda: self.search())
        self.change_btn.place(x=200, y=290, width=100, height=50)


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        sample_button = tk.Button(self, border=0, command=lambda: guifunc.button_click(self))
        sample_button.place(x=25, y=100)

        button = tk.Button(self, text="Logout",
                           command=lambda: [controller.show_frame("Login"),
                                            self.controller.frames["Login"].user_txt.focus()])
        button.pack()
        button.place(x=225, y=300)

        self.modify = tk.Button(self, text='Modify Users', command=lambda: guifunc.modify(self))


if __name__ == "__main__":
    app = SampleApp()
    width = 500
    height = 350
    ws = app.winfo_screenwidth()
    hs = app.winfo_screenheight()
    ws = (ws / 2) - (width) - 350
    hs = (hs / 2) - (height / 2) - 250
    app.resizable(False, False)  # don't allow user to resize
    app.title('1008 Data Structures')
    app.geometry('%dx%d+%d+%d' % (width, height, ws, hs))  # set app size
    app.attributes('-topmost', False)  # allow other window to be above main app
    app.mainloop()

