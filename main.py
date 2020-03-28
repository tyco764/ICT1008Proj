import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import networkx as nx
import BusRoutesAlgo as bus
from geopy.distance import geodesic
import folium, threading, webbrowser
from flask import Flask, render_template
import djs, rawLogic, time, csv

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
            "folder": None,
            "hdb": '/hdb.csv',
            "road": '/roads.csv',
            "edges": '/edges.csv',
            "busroute": '/BusRoutes.csv',
            "busedges": '/busedges.csv',
            "busnodes": '/busnodes.csv'
        }

        self.startdest = []
        self.enddest = []

        self.hdbdf = pd.DataFrame()
        self.edgesdf = pd.DataFrame()
        self.busedgesdf = pd.DataFrame()
        self.busroutedf = pd.DataFrame()
        self.busnodesdf = pd.DataFrame()

        #debug
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.width', 500)

        self.route = []
        self.routelat = []
        self.routelong = []

        self.frames = {}
        for F in (StartPage, SearchPage,):
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

        h1 = Font(family="Helvetica", size=20)  # weight="bold"

        startlabel = tk.Label(self, text="CSV Folder", font=h1)
        startlabel.place(x=40, y=105)

        folder = tk.StringVar()
        folder_entry = tk.Entry(self, justify='left', text=folder, state='disabled')
        folder_entry.focus()
        folder_entry.place(x=200, y=100, width=160, height=50)

        folder_filebtn = tk.Button(self, text='Browse',
                                  command=lambda: enter_file(self, folder))
        folder_filebtn.pack()
        folder_filebtn.place(x=380, y=100, width=100, height=50)

        submit_btn = tk.Button(self, text='Submit', command=lambda: csvreader(self))
        submit_btn.pack()
        submit_btn.place(x=200, y=290, width=100, height=50)


def enter_file(self, entry):
    # set default filetype and restrict user to select CSV files only
    #filetype = [("CSV file", "*.csv")]
    folder = filedialog.askdirectory()

    if folder != "":
        entry.set(folder)
        self.controller.filenames["folder"] = folder  # store filename as into dictionary
    else:
        msgbox.showerror("Error", "Please try again!")


class SearchPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.runninglabel = tk.Label(self, text="Path Finder", font = Font(family="Helvetica", size=24, weight="bold"))
        self.runninglabel.place(x=40, y=30)

        h1 = Font(family="Helvetica", size=20)  # weight="bold"
        startlabel = tk.Label(self, text="Start:", font=h1)
        startlabel.place(x=85, y=90)

        startdest = tk.StringVar()
        startdest.set("Cove LRT")
        self.start = tk.Entry(self, justify='left', text=startdest)
        self.start.focus()
        self.start.place(x=200, y=90, width=250, height=50)

        endlabel = tk.Label(self, text="End:", font=h1)
        endlabel.place(x=85, y=150)

        # large_font = ('Verdana', 14)
        enddest = tk.StringVar()
        enddest.set("623B")
        self.end = tk.Entry(self, justify='left', text=enddest)
        self.end.place(x=200, y=150, width=250, height=50)
        self.end.bind('<Return>')

        options = ["Least Transfer", "Shortest Time", "Least Walking"]
        option = tk.StringVar()
        option.set(options[1])
        optionmenu = tk.OptionMenu(self, option, *options)
        optionmenu.place(x=120, y=230, width=120, height=43)

        self.search_btn = tk.Button(self, text="Find Path",
                                    command=lambda: threadalgo(self, option.get(), startdest, enddest))
        self.search_btn.place(x=260, y=230, width=100, height=40)

        returnbtn = tk.Button(self, text="Return",
                              command=lambda: [controller.show_frame("StartPage"),
                                               self.runninglabel.config(text='Path Finder')])
        returnbtn.pack()
        returnbtn.place(x=200, y=290, width=100, height=50)


def threadalgo(self, option, startdest, enddest):
    result = binSearch(self, self.controller.hdbdf,startdest, enddest)

    if result == -1:
        msgbox.showerror("Error", "Cannot Find what you are looking for!")
    else:
        self.runninglabel.config(text='Finding Path...')
        callthread = threading.Thread(target=callalgo, args=[self, option])
        callthread.start()

def callalgo(self, option):
    starttime = time.time()
    busnodes = self.controller.busnodesdf.values.tolist()
    startwalkingroute, endwalkingroute = [], []
    midbusstop = []

    #getting close bus stops for start dest

    for i in range(len(busnodes)):
        test = getdistance(self.controller.startdest[1], self.controller.startdest[2],
                           busnodes[i][2], busnodes[i][1])
        busnodes[i].append(test)

    busnodes = sorted(busnodes, key=lambda x: x[4])

    for i in range(3):
        midbusstop.append(busnodes[i])
        print(busnodes[i])

    print("StartNode: ", midbusstop[0], midbusstop[1], midbusstop[2])

    # get walking route
    for i in list(midbusstop):
        print("startdest , midbusstop ", self.controller.startdest, i)
        if self.controller.startdest[0] == i[0]:
            path = [i[0]]
            walkingdist = 0
        else:
            path, walkingdist = astaralgo(self, self.controller.startdest, i)
        if path == -1:
            midbusstop.remove(i)
        else:
            startwalkingroute.append([path, walkingdist])

    #getting close bus stops for end dest
    busnodes = self.controller.busnodesdf.values.tolist()
    endbusstop = []
    for i in range(len(busnodes)):
        test = getdistance(self.controller.enddest[1], self.controller.enddest[2],
                           busnodes[i][2], busnodes[i][1])
        busnodes[i].append(test)

    busnodes = sorted(busnodes, key=lambda x: x[4])
    for i in range(3):
        endbusstop.append(busnodes[i])

    print("EndNode: ", endbusstop[0], endbusstop[1], endbusstop[2])

    # get walking route
    for i in list(endbusstop):
        path, walkingdist = astaralgo(self, self.controller.enddest, i)
        if path == -1:
            endbusstop.remove(i)
        else:
            path.reverse()
            endwalkingroute.append([path, walkingdist])

    for i in range(len(startwalkingroute)):
        print("start walking route", startwalkingroute[i])

    for i in range(len(endwalkingroute)):
        print("end walking route", endwalkingroute[i])

    buspaths = [[None for x in range(3)] for y in range(3)]

    #"Least Transfer", "Shortest Time", "Least Walking"
    if option == 'Least Transfer':
        optionvalue = -3
    elif option == 'Shortest Time':
        optionvalue = -1
    elif option == 'Least Walking':
        optionvalue = -1

    minwalkdist = [[None for x in range(3)] for y in range(3)]
    for i in range(len(startwalkingroute)):
        for j in range(len(endwalkingroute)):
            startpath = startwalkingroute[i][0]
            endpath = endwalkingroute[j][0]
            minwalkdist[i][j] = startwalkingroute[i][1] + endwalkingroute[j][1]
            print(minwalkdist[i][j])
            print(startpath[-1], endpath[0], minwalkdist[i][j])
            res = busalgo(self, startpath[-1], endpath[0])
            res.sort(key=lambda x: x[optionvalue])
            buspaths[i][j] = res[0]
    #buspaths[0][0] = buspaths[0][2]

    print(len(buspaths))
    #print(buspaths[0])
    startidx , endidx = 0, 0
    tempmin, mindist = 1000000, 0
    startlen, endlen = len(buspaths), len(buspaths[i])

    for i in range(startlen):
        for j in range(endlen):
            if option == 'Least Walking':
                mindist = minwalkdist[i][j]
                if mindist is not None:
                    if mindist < tempmin:
                        startidx = i
                        endidx = j
                        tempmin = mindist
            else:
                path = buspaths[i][j]
                if path is not None:
                    mintime = path[optionvalue] + (minwalkdist[i][j] / 1000) / 4 * 60
                    if mintime < tempmin:
                        startidx = i
                        endidx = j
                        tempmin = mintime

            if buspaths[i][j] is not None:
                print(startwalkingroute[i], buspaths[i][j], endwalkingroute[j])
    print(startidx, endidx)
    #buspaths[0].sort(key = lambda x: x[-1])
    #startidx, endidx = 1,1
    print(startwalkingroute[startidx], buspaths[startidx][endidx], endwalkingroute[endidx])

    print("displaying map")
    errorcheck = displaymap(self, startwalkingroute[startidx], buspaths[startidx][endidx], endwalkingroute[endidx])

    '''
    for i in range(len(startwalkingroute)):
        for j in range(len(endwalkingroute)):
            errorcheck = displaymap(self, startwalkingroute[i], buspaths[i][j],
                                    endwalkingroute[j])
            time.sleep(5)
    '''
    if errorcheck == -1:
        msgbox.showerror("Error", "Drawing Map Failed")

    #drawmap(self, startwalkingroute[i][0] + endwalkingroute[j][0])
    self.runninglabel.config(text='Path Found!')
    print("Time taken is:", time.time() - starttime)


def astaralgo(self, startNode, endNode):
    G = nx.Graph()

    starttime = time.time()
    edgesarr = self.controller.edgesdf.to_numpy()

    for i in range(len(edgesarr)):
        for name in self.controller.hdbdf['name']:
            #if edgesarr[i][0] == name or edgesarr[i][3] == name:
            G.add_edge(edgesarr[i][0], edgesarr[i][3], weight= edgesarr[i][6])
    #print(edgesarr[0][0], edgesarr[0][3], edgesarr[0][6])

    hdbarr = self.controller.hdbdf.to_numpy()
    #for i in range(5):
        #print(hdbarr[i])
    for i in range(len(hdbarr)):
        value = getdistance(hdbarr[i][2], hdbarr[i][1], endNode[2], endNode[1])
        G.add_node(hdbarr[i][0], gVal=0, fVal=0, hVal=value)
    endtime = time.time() - starttime
    print("Graph Added.")
    #print(G.nodes(data=True))
    print("Time Taken to add nodes is", endtime)

    starttime = time.time()
    #print(startNode)
    #endNode = self.controller.enddest[0]
    path,walkingdist = rawLogic.AStar(G, startNode[0], endNode[0])
    return path, walkingdist


def busalgo(self, start_point, end_point):
    #busnum = '3 Reverse'
    #test = bus.getdist(self, busnum, start_point, end_point)

    #start_point = 'Opp Blk 103A (65071)'
    #end_point = 'Punggol Temp Int (65009)'
    busfile = self.controller.filenames["folder"] + self.controller.filenames["busroute"]
    busnodesarr = self.controller.busnodesdf.to_numpy()
    #busnodesarr is the array with the opposite bus stops in busnodesarr[3]



    with open(busfile, mode='r') as csv_file:
        csvdata = csv.reader(csv_file, delimiter=',')
        #print(bus.getdist(self, '136', 'Punggol Temp Int (65009)', 'Punggol Sec/Blk 601B (65281'))
        least_stops_print = bus.BusAlgo(self, busnodesarr, csv_file, csvdata, start_point, end_point)
        #print(least_stops_print)
        #for i in range(len(least_stops_print)):
            #print(least_stops_print[i])
        print("End of Paths")
        return least_stops_print



def drawmap(self, path):
    searchdf = self.controller.hdbdf.copy(deep=True)
    searchdf["name"] = searchdf["name"].apply(str)
    hdbarr = searchdf.to_numpy()
    hdbarr = hdbarr[np.argsort(hdbarr[:, 0])]

    long = []
    lat = []
    for i in range(len(path)):
        idx = binSearchAlgo(self, hdbarr, str(path[i]), 0)
        if idx is not None:
            long.append(hdbarr[idx][1])
            lat.append(hdbarr[idx][2])

        # print(self.controller.routelong)
    route = list(zip(lat, long))
    #print(route)
    print("DrawMap Done")
    return route

# @app.route('/')
def displaymap(self, start, middle, end):
    # takes in an array of latitude and longitude and draws them onto openstreetmap
    starttime = time.time()
    #self.controller.route = start

    # printing out the path -- Walking (WIP)
    # hdbarr = self.controller.hdbdf.to_numpy()

    route = [0 for x in range(2)]
    route[0] = drawmap(self, start[0])
    route[1] = drawmap(self, end[0])

    # route[1] = drawmap(self, middle)
    buspath = []
    dist = 0
    busdf = self.controller.busedgesdf.copy(deep=True)

    pathdict = middle[1]
    for key, values in pathdict.items():

        if len(values) == 1:
            print(key, values)
            continue

        else:
            temppath = []

            if key == "walk":
                print(values)
                for i in values:
                    print(i)
                    searchdf = busdf[busdf['fromNode'] == i]
                    busarr = searchdf.to_numpy()
                    print(busarr[0][1], busarr[0][2], busarr[0][3])
                    temppath.append((busarr[0][3], busarr[0][2]))
                    buspath.append(temppath)
                continue

            searchdf = busdf[busdf['bus number'] == key]
            busarr = searchdf.to_numpy()
            idx = 0
            try:
                starttemp = busarr[idx][1]
            except IndexError:
                print(key)
                print(middle)
            if len(busarr) == 0:
                continue
            while busarr[idx][0] == key:
                if starttemp != values[0]:
                    idx += 1
                    if idx == len(busarr):
                        print("starttemp =", values[0])
                        return -1
                    starttemp = busarr[idx][1]

                else:
                    temppath.append((busarr[idx][3], busarr[idx][2]))
                    break

            endtemp = busarr[idx][4]
            while busarr[idx][0] == key:
                if endtemp != values[-1]:
                    temppath.append((busarr[idx][6], busarr[idx][5]))
                    idx += 1
                    if idx == len(busarr):
                        if (key == 'LRT' or key == 'LRT Reverse'):
                            idx = 0
                        else:
                            print("start, end = ", key, starttemp, values[-1])
                            return -1
                    endtemp = busarr[idx][4]
                else:
                    temppath.append((busarr[idx][6], busarr[idx][5]))
                    break
            buspath.append(temppath)
    print(buspath)
    #route[1] = buspath

    map = folium.Map(location=[1.4029, 103.9063], zoom_start=16)



    for i in range(len(route)):
        for j in range(len(route[i])):
            #if i%2 == 0 and j == len(route[i])-1:
                #continue
            folium.Marker(route[i][j]).add_to(map)
        # popup=names[]

        folium.PolyLine(route[i], color="red").add_to(map)


    for eachbus in buspath:
        for i in range(len(eachbus)):
            if i == 0 or i == len(eachbus):
                folium.Marker(eachbus[i]).add_to(map)
            else:
                continue
        folium.PolyLine(eachbus, color="blue").add_to(map)


    endtime = time.time() - starttime
    print("Time Taken is", endtime)

    map.save("static/map.html")
    #call function to write route.html
    #returnval = writehtml(start, middle, end)
    # if returnval == -1:
    #

    #webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new("map.html")
    webbrowser.open("http://127.0.0.1:5000")
    self.controller.show_frame("SearchPage")
    return 0

def writehtml(self, start, middle, end):
    #start is the list of walking to first bus stop
    #middle is list with dictionary in 2nd position ,-3 transfers, -2 distance, -1 time
    #end is the list of walking from end bus stop to dest
    pass

def binSearch(self, df, query, query2):
    searchdf = df.copy(deep=True)
    searchdf["name"] = searchdf["name"].apply(str)
    searcharr = searchdf.to_numpy()

    searcharr = searcharr[np.argsort(searcharr[:, 0])]
    startvalue = binSearchAlgo(self, searcharr, query.get(), 0)
    endvalue = binSearchAlgo(self, searcharr, query2.get(), 0)

    if startvalue is None or endvalue is None:
        return -1
    else:
        self.controller.startdest = [query.get(), searcharr[startvalue][2], searcharr[startvalue][1]]
        self.controller.enddest = [query2.get(), searcharr[endvalue][2], searcharr[endvalue][1]]
        print(self.controller.startdest, "\n", self.controller.enddest)
        return 1


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

    #self.controller.filenames["folder"] = tk.filedialog.askdirectory()
    print(self.controller.filenames["folder"]+self.controller.filenames["hdb"])

    if self.controller.filenames["folder"] is not None:
        try:
            #print(self.controller.filenames["folder"])
            self.controller.hdbdf = pd.read_csv(self.controller.filenames["folder"]+self.controller.filenames["hdb"])
            self.controller.edgesdf = pd.read_csv(self.controller.filenames["folder"]+self.controller.filenames["edges"])
            self.controller.busedgesdf = pd.read_csv(self.controller.filenames["folder"]+self.controller.filenames["busedges"])
            self.controller.busroutedf = pd.read_csv(self.controller.filenames["folder"]+self.controller.filenames["busroute"])
            self.controller.busnodesdf = pd.read_csv(self.controller.filenames["folder"] + self.controller.filenames["busnodes"])

            print(self.controller.hdbdf.head(5), "\n")
            self.controller.show_frame("SearchPage")
        except FileNotFoundError:
            msgbox.showerror("Error", "Please try again!")
    else:
        msgbox.showerror("Error", "Please try again!")


def getdistance(startlat, startlong, endlat, endlong):
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
