import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt
import mplleaflet as mpl
import pandas as pd
from geopy.distance import geodesic
import numpy as np


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Create a container to stack all the frames
        # then raise the one we want visible

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.filenames = {
            "hdb": tk.StringVar(),
            "road": tk.StringVar()
        }

        self.hdbdf = pd.DataFrame()
        self.roaddf = pd.DataFrame()

        self.routelat = []
        self.routelong = []

        self.frames = {}
        for F in (StartPage, SearchPage, AlgoPage,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        h1 = Font(family="Helvetica", size=18)  # weight="bold"
        hdblabel = tk.Label(self, text="HDB Excel", font=h1)
        hdblabel.place(x=90, y=90)

        # self.hdb = tk.Entry(self, justify='left', state='disabled')
        entry_hdb = tk.StringVar()
        hdb_file = tk.Entry(self, text=entry_hdb, state='disabled')
        hdb_file.place(x=250, y=100)
        hdb_filebtn = tk.Button(self, text='HDB File',
                                command=lambda: enter_file(self, entry_hdb, "hdb"))
        hdb_filebtn.place(x=380, y=95)

        h1 = Font(family="Helvetica", size=18)  # weight="bold"
        roadlabel = tk.Label(self, text="Road CSV", font=h1)
        roadlabel.place(x=90, y=150)

        # self.hdb = tk.Entry(self, justify='left', state='disabled')
        entry_road = tk.StringVar()
        road_file = tk.Entry(self, text=entry_road, state='disabled')
        road_file.place(x=250, y=150)
        road_filebtn = tk.Button(self, text='HDB File',
                                 command=lambda: enter_file(self, entry_road, "road"))
        road_filebtn.place(x=380, y=155)

        submit_btn = tk.Button(self, text='Submit', command=lambda: csvreader(self))
        submit_btn.place(x=150, y=245)


def enter_file(self, entry, file_name):
    # set default filetype and restrict user to select CSV files only
    filetype = [("CSV file", "*.csv")]
    filename = filedialog.askopenfilename(initialdir="./csv", title="Select file", defaultextension=".csv",
                                          filetypes=filetype)
    if filename != "":
        entry.set(filename)
        self.controller.filenames[file_name].set(filename)  # store filename as into dictionary
    else:
        msgbox.showerror("Error", "Please try again!")


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        h1 = Font(family="Helvetica", size=28)  # weight="bold"
        startlabel = tk.Label(self, text="Start:", font=h1)
        startlabel.place(x=90, y=98)

        startdest = tk.StringVar()
        self.start = tk.Entry(self, justify='left', text=startdest)
        self.start.focus()
        self.start.place(x=203, y=100, width=250, height=50)

        endlabel = tk.Label(self, text="End:", font=h1)
        endlabel.place(x=90, y=180)

        # large_font = ('Verdana', 14)
        enddest = tk.StringVar()
        self.end = tk.Entry(self, justify='left', text=enddest)
        self.end.place(x=203, y=180, width=250, height=50)
        self.end.bind('<Return>', )

        self.search_btn = tk.Button(self, text="Search", command=lambda: binSearch(self, self.controller.hdbdf,
                                                                                   startdest, enddest))
        self.search_btn.place(x=200, y=290, width=100, height=50)


class AlgoPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        but = tk.Button(self, text="Best Route", command=lambda: bestalgo(self))
        but.place(x=200, y=190, width=100, height=50)

        button = tk.Button(self, text="Return",
                           command=lambda: [controller.show_frame("SearchPage")])
        button.pack()
        button.place(x=200, y=290, width=100, height=50, )


def bestalgo(self):
    lat = [1.37244, 1.37741]
    long = [103.89379, 103.84876]

    dist = getdistance(self, lat[0], long[0], lat[1], long[1])
    print("Distance between Hougang Mall and SIT@NYP is: ", dist)

    displaymap(self, lat, long)


def displaymap(self, lat, long):
    plt.plot(long, lat, 'b')
    plt.plot(long, lat, 'rs')

    plt.draw()
    # plt.show()
    mpl.show()


def binSearch(self, df, query, query2):
    searchdf = df.copy(deep=True)
    searchdf["name"] = searchdf["name"].apply(str)
    searcharr = searchdf.to_numpy()

    np.chararray.sort(searcharr, axis=0)
    startvalue = binSearchAlgo(self, searcharr, query.get(), 0)
    endvalue = binSearchAlgo(self, searcharr, query2.get(), 0)

    if startvalue is None or endvalue is None:
        msgbox.showerror("Error", "Cannot Find what you are looking for!")
        self.controller.show_frame("SearchPage")
    else:
        startdest = searcharr[startvalue]
        enddest = searcharr[endvalue]
        print(startdest, enddest)
        self.controller.show_frame("AlgoPage")


def binSearchAlgo(self, array, query, col):
    lo = 0
    high = len(array) - 1

    while lo <= high:
        middle = (lo + high) // 2
        if array[middle][col] < query:
            lo = middle + 1
        elif array[middle][col] > query:
            high = middle -1
        else:
            return middle
    return None


def csvreader(self):
    if self.controller.filenames["hdb"].get() is not None:
        self.controller.hdbdf = pd.read_csv(self.controller.filenames["hdb"].get())
        print(self.controller.hdbdf.head(5), "\n")
    if self.controller.filenames["road"].get() is not None:
        self.controller.roaddf = pd.read_csv(self.controller.filenames["road"].get())
        print(self.controller.roaddf.head(5), "\n")

    self.controller.show_frame("SearchPage")


def getdistance(self, startlat, startlong, endlat, endlong):
    startarr = (startlat, startlong)
    endarr = (endlat, endlong)

    return geodesic(startarr, endarr).km


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
