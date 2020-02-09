import tkinter as tk
from tkinter.font import Font
import matplotlib.pyplot as plt
import mplleaflet as mpl


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Create a container to stack all the frames
        # then raise the one we want visible

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (SearchPage, MainPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        h1 = Font(family="Helvetica", size=28)  # weight="bold"
        startlabel = tk.Label(self, text="Start:", font=h1)
        startlabel.place(x=90, y=98)

        self.start = tk.Entry(self, justify='left')
        self.start.focus()
        self.start.place(x=203, y=100, width=250, height=50)

        endlabel = tk.Label(self, text="End:", font=h1)
        endlabel.place(x=90, y=180)

        large_font = ('Verdana', 14)
        self.end = tk.Entry(self, justify='left', font=large_font)
        self.end.place(x=203, y=180, width=250, height=50)
        self.end.bind('<Return>', )
        # lambda event: guifunc.check_password(self, self.user_txt.get(), self.pass_txt.get()))

        self.search_btn = tk.Button(self, text="Enter", command=lambda: displaymap(self))
        self.search_btn.place(x=200, y=290, width=100, height=50)


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        but = tk.Button(self, text="Test", command=lambda: displaymap(self))
        but.place(x=200, y=190, width=100, height=50)

        button = tk.Button(self, text="Return",
                           command=lambda: [controller.show_frame("MainPage")])
        button.pack()
        button.place(x=200, y=290, width=100, height=50, )


def displaymap(self):
    lat = [1.39833, 1.39641, 1.39832,  1.40639, 1.39957, 1.40069]
    long = [103.90495, 103.90718, 103.90495, 103.90880, 103.90973, 103.91338]

    plt.plot(long, lat, 'b')
    plt.plot(long, lat, 'rs')

    plt.draw()
    #plt.show()
    mpl.show()


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
