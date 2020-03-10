import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import networkx as nx
from geopy.distance import geodesic
import folium, threading, webbrowser
from flask import Flask, render_template
import djs, rawLogic, time

app = Flask(__name__, static_url_path="")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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
            "road": tk.StringVar(),
            "edges": tk.StringVar(),
            "busedges": tk.StringVar(),
            "roadedges": tk.StringVar(),
        }

        self.startdest = []
        self.enddest = []

        self.hdbdf = pd.DataFrame()
        self.roaddf = pd.DataFrame()
        self.edgesdf = pd.DataFrame()
        self.busedgesdf = pd.DataFrame()
        self.roadedgesdf = pd.DataFrame()

        #debug
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.width', 500)

        self.route = []
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
        hdblabel = tk.Label(self, text="HDB CSV", font=h1)
        hdblabel.place(x=90, y=45)

        # self.hdb = tk.Entry(self, justify='left', state='disabled')
        entry_hdb = tk.StringVar()
        hdb_file = tk.Entry(self, text=entry_hdb, state='disabled')
        hdb_file.place(x=250, y=50)
        hdb_filebtn = tk.Button(self, text='HDB File',
                                command=lambda: enter_file(self, entry_hdb, "hdb"))
        hdb_filebtn.place(x=380, y=45)

        h1 = Font(family="Helvetica", size=18)  # weight="bold"
        roadlabel = tk.Label(self, text="Road CSV", font=h1)
        roadlabel.place(x=90, y=95)

        # self.hdb = tk.Entry(self, justify='left', state='disabled')
        entry_road = tk.StringVar()
        road_file = tk.Entry(self, text=entry_road, state='disabled')
        road_file.place(x=250, y=100)
        road_filebtn = tk.Button(self, text='Road File',
                                 command=lambda: enter_file(self, entry_road, "road"))
        road_filebtn.place(x=380, y=105)

        edgeslabel = tk.Label(self, text="Edges CSV", font=h1)
        edgeslabel.place(x=90, y=145)

        entry_edges = tk.StringVar()
        edges_file = tk.Entry(self, text=entry_edges, state='disabled')
        edges_file.place(x=250, y=150)
        edges_filebtn = tk.Button(self, text='Edges File',
                                 command=lambda: enter_file(self, entry_edges, "edges"))
        edges_filebtn.place(x=380, y=155)

        busedgeslabel = tk.Label(self, text="Bus Edges CSV", font=h1)
        busedgeslabel.place(x=50, y=195)

        bus_edges = tk.StringVar()
        busedges_file = tk.Entry(self, text=bus_edges, state='disabled')
        busedges_file.place(x=250, y=200)
        busedges_filebtn = tk.Button(self, text='Bus Edges',
                                 command=lambda: enter_file(self, bus_edges, "busedges"))
        busedges_filebtn.place(x=380, y=205)

        submit_btn = tk.Button(self, text='Submit', command=lambda: csvreader(self))
        submit_btn.pack()
        submit_btn.place(x=200, y=290, width=100, height=50, )


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
        startdest.set("612B")
        self.start = tk.Entry(self, justify='left', text=startdest)
        self.start.focus()
        self.start.place(x=203, y=100, width=250, height=50)

        endlabel = tk.Label(self, text="End:", font=h1)
        endlabel.place(x=90, y=180)

        # large_font = ('Verdana', 14)
        enddest = tk.StringVar()
        enddest.set("293")
        self.end = tk.Entry(self, justify='left', text=enddest)
        self.end.place(x=203, y=180, width=250, height=50)
        self.end.bind('<Return>')

        self.search_btn = tk.Button(self, text="Search", command=lambda: binSearch(self, self.controller.hdbdf,
                                                                                   startdest, enddest))
        self.search_btn.place(x=200, y=290, width=100, height=50)


class AlgoPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        but = tk.Button(self, text="Best Route", command=lambda: astaralgo(self))
        but.place(x=200, y=190, width=100, height=50)

        but2 = tk.Button(self, text="Best Route Debug)", command=lambda: bestalgo(self))
        but2.place(x=310, y=190, width=100, height=50)

        button = tk.Button(self, text="Search Again",
                           command=lambda: [controller.show_frame("SearchPage")])
        button.pack()
        button.place(x=200, y=290, width=100, height=50, )

        returnbtn = tk.Button(self, text="Return",
                           command=lambda: [controller.show_frame("StartPage")])
        returnbtn.pack()
        returnbtn.place(x=310, y=290, width=100, height=50, )


def astaralgo(self):
    G = nx.Graph()

    starttime = time.time()
    edgesarr = self.controller.edgesdf.to_numpy()

    for i in range(len(edgesarr)):
        for name in self.controller.hdbdf['name']:
            #if edgesarr[i][0] == name or edgesarr[i][3] == name:
            G.add_edge(edgesarr[i][0], edgesarr[i][3], weight= edgesarr[i][6])
    print(edgesarr[0][0], edgesarr[0][3], edgesarr[0][6])

    hdbarr = self.controller.hdbdf.to_numpy()
    for i in range(len(hdbarr)):
        value = getdistance(self, hdbarr[i][2], hdbarr[i][1],self.controller.enddest[1], self.controller.enddest[2])
        G.add_node(hdbarr[i][0], gVal=0, fVal=0, hVal=value)

    endtime = time.time() - starttime
    print("Graph Added.")
    print(G.nodes(data=True))
    print("Time Taken is", endtime)

    starttime = time.time()

    startNode = self.controller.startdest[0]
    #print(startNode)
    endNode = self.controller.enddest[0]

    self.controller.route = rawLogic.AStar(G, startNode, endNode)
    print(self.controller.route)
    if self.controller.route == -1:
        msgbox.showerror("Error", "No Paths Found")

    else:
        #hdbarr = self.controller.hdbdf.to_numpy()
        searchdf = self.controller.hdbdf.copy(deep=True)
        searchdf["name"] = searchdf["name"].apply(str)
        hdbarr = searchdf.to_numpy()
        hdbarr = hdbarr[np.argsort(hdbarr[:,0])]

        self.controller.routelong = []
        self.controller.routelat = []
        for i in range(len(self.controller.route)):
            idx = binSearchAlgo(self, hdbarr, str(self.controller.route[i]), 0)
            if idx is not None:
                self.controller.routelong.append(hdbarr[idx][1])
                self.controller.routelat.append(hdbarr[idx][2])

        #print(self.controller.routelong)
        displaymap(self)

        endtime = time.time() - starttime
        print("Time Taken is", endtime)


def bestalgo(self):
    self.controller.routelat = [1.40523, 1.4037392, 1.4031741, 1.4026126, 1.4030339,1.4051606, 1.40526]
    self.controller.routelong = [103.90235, 103.9041668,103.9049597, 103.9056626, 103.9068768,103.907831, 103.90858]

    dist = getdistance(self, self.controller.routelat[0], self.controller.routelong[0],
                       self.controller.routelat[1], self.controller.routelong[1])
    print("Distance between Hougang Mall and SIT@NYP is: ", dist)

    displaymap(self)


# @app.route('/')
def displaymap(self):
    # takes in an array of latitude and longitude and draws them onto openstreetmap
    long = self.controller.routelong.copy()
    lat = self.controller.routelat.copy()

    route = list(zip(lat, long))

    map = folium.Map(location=[1.4029, 103.9063], zoom_start=16)
    for i in range(len(route)):
        folium.Marker(route[i]).add_to(map)
        # popup=names[]
    folium.PolyLine(route).add_to(map)

    map.save("static/map.html")
    #webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new("map.html")
    webbrowser.open("http://127.0.0.1:5000")
    self.controller.show_frame("StartPage")


def binSearch(self, df, query, query2):
    searchdf = df.copy(deep=True)
    searchdf["name"] = searchdf["name"].apply(str)
    searcharr = searchdf.to_numpy()

    searcharr = searcharr[np.argsort(searcharr[:, 0])]
    startvalue = binSearchAlgo(self, searcharr, query.get(), 0)
    endvalue = binSearchAlgo(self, searcharr, query2.get(), 0)

    if startvalue is None or endvalue is None:
        msgbox.showerror("Error", "Cannot Find what you are looking for!")
        self.controller.show_frame("SearchPage")
    else:
        self.controller.startdest = [query.get(), searcharr[startvalue][2], searcharr[startvalue][1]]
        self.controller.enddest = [query2.get(), searcharr[endvalue][2], searcharr[endvalue][1]]
        print(self.controller.startdest, "\n", self.controller.enddest)
        self.controller.show_frame("AlgoPage")


def binSearchAlgo(self, array, query, col):
    lo = 0
    high = len(array) - 1
    middle = 0

    while lo <= high:
        middle = (lo + high) // 2
        if array[middle][col] < query:
            lo = middle + 1
        elif array[middle][col] > query:
            high = middle - 1
        else:
            return middle
    return None


def csvreader(self):
    if self.controller.filenames["hdb"].get() and self.controller.filenames["road"].get() and self.controller.filenames["edges"].get():


        self.controller.hdbdf = pd.read_csv(self.controller.filenames["hdb"].get())
        self.controller.roaddf = pd.read_csv(self.controller.filenames["road"].get())
        self.controller.edgesdf = pd.read_csv(self.controller.filenames["edges"].get())
        if self.controller.filenames["busedges"].get() and self.controller.filenames["roadedges"].get():
            self.controller.busedgesdf = pd.read_csv(self.controller.filenames["busedges"].get())
            self.controller.roadedgesdf = pd.read_csv(self.controller.filenames["roadedges"].get())

        print(self.controller.hdbdf.head(5), "\n")
        self.controller.show_frame("SearchPage")

        #else:
            #msgbox.showerror("Error", "Please try again!")
    else:
        msgbox.showerror("Error", "Please try again!")


def getdistance(self, startlat, startlong, endlat, endlong):
    startarr = (startlat, startlong)
    endarr = (endlat, endlong)

    return float(geodesic(startarr, endarr).m)


def tk_main():
    root = SampleApp()
    width = 500
    height = 350
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    ws = (ws / 2) - (width) - 350
    hs = (hs / 2) - (height / 2) - 250
    root.resizable(False, False)  # don't allow user to resize
    root.title('1008 Data Structures')
    root.geometry('%dx%d+%d+%d' % (width, height, ws, hs))  # set app size
    root.attributes('-topmost', False)  # allow other window to be above main app
    root.mainloop()


def flask_main():
    app.run()

@app.route("/")
def indexpage():
    return render_template("index.html")


if __name__ == "__main__":
    flt = threading.Thread(target=flask_main)
    flt.daemon = True
    flt.start()
    tk_main()


