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
        self.start = []
        self.middle = []
        self.end = []

        self.hdbdf = pd.DataFrame()
        self.edgesdf = pd.DataFrame()
        self.busedgesdf = pd.DataFrame()
        self.busroutedf = pd.DataFrame()
        self.busnodesdf = pd.DataFrame()

        # debug
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
    # filetype = [("CSV file", "*.csv")]
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

        self.runninglabel = tk.Label(self, text="Path Finder", font=Font(family="Helvetica", size=24, weight="bold"))
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

        options = ["Least Transfer", "Shortest Time", "Least Walking", "Walking Only"]
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
    result = binSearch(self, self.controller.hdbdf, startdest, enddest)

    if result == -1:
        msgbox.showerror("Error", "Cannot Find what you are looking for!")
    else:
        self.runninglabel.config(text='Finding Path...')
        callthread = threading.Thread(target=callalgo, args=[self, option])
        callthread.start()


def callalgo(self, option):
    starttime = time.time()

    print(self.controller.startdest, self.controller.enddest)
    path, walkingdist = astaralgo(self, self.controller.startdest, self.controller.enddest)
    self.controller.start = path

    if (walkingdist < 500 or option == 'Walking Only') and option != 'Least Walking':
        walkingroute = [path, walkingdist]
        displaymap(self, walkingroute, None, None, [path, None])
    else:
        busnodes = self.controller.busnodesdf.values.tolist()
        startwalkingroute, endwalkingroute = [], []
        midbusstop = []

        # getting close bus stops for start dest

        for i in range(len(busnodes)):
            test = getdistance(self.controller.startdest[1], self.controller.startdest[2],
                               busnodes[i][1], busnodes[i][2])
            busnodes[i].append(test)

        busnodes = sorted(busnodes, key=lambda x: x[4])

        for i in range(3):
            midbusstop.append(busnodes[i])

        print("StartNode: ", midbusstop[0], midbusstop[1], midbusstop[2])

        # get walking route
        for i in list(midbusstop):
            if self.controller.startdest[0] == i[0]:
                path = [i[0]]
                walkingdist = 0
            else:
                path, walkingdist = astaralgo(self, self.controller.startdest, i)
            if path == -1:
                midbusstop.remove(i)
            else:
                startwalkingroute.append([path, walkingdist])

        # getting close bus stops for end dest
        busnodes = self.controller.busnodesdf.values.tolist()
        endbusstop = []
        for i in range(len(busnodes)):
            test = getdistance(self.controller.enddest[1], self.controller.enddest[2],
                               busnodes[i][1], busnodes[i][2])
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

        print("Time Take to get walking route: ", time.time() - starttime)

        buspaths = [[None for x in range(3)] for y in range(3)]
        minwalkdist = [[0 for x in range(3)] for y in range(3)]

        for i in range(len(startwalkingroute)):
            for j in range(len(endwalkingroute)):
                startpath = startwalkingroute[i][0]
                endpath = endwalkingroute[j][0]
                minwalkdist[i][j] = startwalkingroute[i][1] + endwalkingroute[j][1]
                res = busalgo(self, startpath[-1], endpath[0])
                res.sort(key=lambda x: x[-1])
                buspaths[i][j] = res[0]

        # buspaths[0][0] = buspaths[0][2]
        print("Time Take to get bus paths: ", time.time() - starttime)

        startidx, endidx = 0, 0
        tempmin, mindist = 1000000, 0
        startlen, endlen = len(buspaths), len(buspaths[i])
        leasttransfers = 1000000
        leasttransferpath = []
        leasttransferwalk = 0

        for i in range(startlen):
            for j in range(endlen):
                walktime = (minwalkdist[i][j] / 1000) / 4 * 60

                if option == 'Least Walking':
                    mindist = minwalkdist[i][j]
                    if mindist is not None:
                        if mindist < tempmin:
                            startidx = i
                            endidx = j
                            tempmin = mindist
                elif option == "Least Transfer":
                    path = buspaths[i][j]
                    if path is not None:
                        if path[-3] < leasttransfers:
                            leasttransferpath = path
                            leasttransferwalk = walktime
                            startidx = i
                            endidx = j
                            leasttransfers = path[-3]
                        elif path[-3] == leasttransfers:
                            if (path[-1] + leasttransferwalk) < (leasttransferpath[-1] + walktime):
                                leasttransferpath = path
                                leasttransferwalk = walktime
                                leasttransfers = path[-3]
                                startidx = i
                                endidx = j
                else:
                    path = buspaths[i][j]
                    if path is not None:
                        mintime = path[-1] + walktime
                        if mintime < tempmin:
                            startidx = i
                            endidx = j
                            tempmin = mintime

        print("Best Path:", startwalkingroute[startidx], buspaths[startidx][endidx], endwalkingroute[endidx])
        print("Time Take to get best path: ", time.time() - starttime)
        print("Displaying map")
        errorcheck = displaymap(self, startwalkingroute[startidx], buspaths[startidx][endidx], endwalkingroute[endidx],
                                [startwalkingroute[startidx][0], endwalkingroute[endidx][0]])
        print("Time Take to draw and display map: ", time.time() - starttime)
        if errorcheck == -1:
            msgbox.showerror("Error", "Drawing Map Failed")

    self.runninglabel.config(text='Path Found!')
    print("Time taken is to find and draw path is:", time.time() - starttime)


def astaralgo(self, startNode, endNode):
    G = nx.Graph()

    starttime = time.time()
    edgesarr = self.controller.edgesdf.to_numpy()

    for i in range(len(edgesarr)):
        G.add_edge(edgesarr[i][0], edgesarr[i][3], weight=edgesarr[i][6])

    hdbarr = self.controller.hdbdf.to_numpy()
    for i in range(len(hdbarr)):
        value = getdistance(hdbarr[i][2], hdbarr[i][1], endNode[1], endNode[2])
        G.add_node(hdbarr[i][0], gVal=0, fVal=0, hVal=value)

    endtime = time.time() - starttime
    print("Graph Added.")
    print("Time Taken to add nodes is", endtime)

    path, walkingdist = rawLogic.AStar(G, startNode[0], endNode[0])
    return path, walkingdist


def busalgo(self, start_point, end_point):
    # busnum = '3 Reverse'
    # test = bus.getdist(self, busnum, start_point, end_point)

    # start_point = 'Opp Blk 103A (65071)'
    # end_point = 'Punggol Temp Int (65009)'
    busfile = self.controller.filenames["folder"] + self.controller.filenames["busroute"]
    busnodesarr = self.controller.busnodesdf.to_numpy()
    # busnodesarr is the array with the opposite bus stops in busnodesarr[3]

    with open(busfile, mode='r') as csv_file:
        csvdata = csv.reader(csv_file, delimiter=',')
        least_stops_print = bus.BusAlgo(self, busnodesarr, csv_file, csvdata, start_point, end_point)
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

    route = list(zip(lat, long))
    print("DrawMap Done")
    return route


# @app.route('/')
def displaymap(self, start, middle, end, pathnames):
    # takes in an array of latitude and longitude and draws them onto openstreetmap
    starttime = time.time()
    map = folium.Map(location=[1.4029, 103.9063], zoom_start=16)

    # Drawing Route for Walking Routes
    route = [None for x in range(2)]
    route[0] = drawmap(self, start[0])
    if end is not None:
        route[1] = drawmap(self, end[0])
    for i in range(len(route)):
        if route[i] is not None:
            for j in range(len(route[i])):
                if 'Way' not in pathnames[i][j]:
                    folium.Marker(location=route[i][j], popup=pathnames[i][j]).add_to(map)
            folium.PolyLine(route[i], color="red").add_to(map)

    # Drawing Route for Bus Routes
    if middle is not None:
        buspath, buspathname = [], []
        dist = 0
        busdf = self.controller.busedgesdf.copy(deep=True)

        pathdict = middle[1]
        for key, values in pathdict.items():

            if len(values) == 1:
                continue

            else:
                temppath = []

                if key == "walk":
                    print(values)
                    for i in values:
                        searchdf = busdf[busdf['fromNode'] == i]
                        busarr = searchdf.to_numpy()
                        print(busarr[0][1], busarr[0][2], busarr[0][3])
                        temppath.append((busarr[0][3], busarr[0][2]))
                        buspath.append(temppath)
                        buspathname.append([values[0], values[-1]])
                    continue

                searchdf = busdf[busdf['bus number'] == key]
                busarr = searchdf.to_numpy()
                idx = 0
                starttemp = busarr[idx][1]

                if len(busarr) == 0:
                    continue
                while busarr[idx][0] == key:
                    if starttemp != values[0]:
                        idx += 1
                        if idx == len(busarr):
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
                                return -1
                        endtemp = busarr[idx][4]
                    else:
                        temppath.append((busarr[idx][6], busarr[idx][5]))
                        break
                buspath.append(temppath)
                buspathname.append([values[0], values[-1]])


        for i in range(len(buspath)):
            for j in range(len(buspath[i])):
                if j == 0:
                    folium.Marker(location=buspath[i][j], popup=buspathname[i][0]).add_to(map)
                elif j == len(buspath[i]):
                    folium.Marker(location=buspath[i][j], popup=buspathname[i][-1]).add_to(map)
                else:
                    continue
            folium.PolyLine(buspath[i], color="blue").add_to(map)

    endtime = time.time() - starttime
    print("Time Taken to Draw Map is", endtime)

    map.save("static/map.html")
    writehtml(self, start, middle, end)
    if writehtml == -1:
        msgbox.showerror("Error", "Error writing route instructions")

    webbrowser.open("http://127.0.0.1:5000")
    self.controller.show_frame("SearchPage")
    return 0


def writehtml(self, start, middle, end):
    # start is the list of walking to first bus stop
    # middle is list with dictionary in 2nd position ,-3 transfers, -2 distance, -1 time
    # end is the list of walking from end bus stop to dest

    startTr = ""
    middleTr = ""
    endTr = ""
    step = 0
    message = """
    <table border=1>
         <tr>
           <th>Step No.</th>
           <th>Instructions</th>
         </tr>
         <indent>
    """

    if start[-1] > 0:
        i = 0
        trueStartLen = getSizeOfNestedList(start)
        nestedStartLen = trueStartLen - 1  # Skip the last element which is distance
        while i < (nestedStartLen - 1):
            startTr += "<tr><td>%d</td><td>From %s, walk to %s.</td></tr>" % ((i + 1), start[0][i], start[0][i + 1])
            i += 1
            step += 1

    if middle is not None:
        if middle[-2] > 0:
            if isinstance(middle[1], dict):
                extractedDict = middle[1]
                dict_keys = list(extractedDict.keys())
                for j in range(len(dict_keys)):
                    if dict_keys[j] == 'walk':
                        walkLen = len(extractedDict['walk'])
                        walk = extractedDict['walk']
                        for k in range(walkLen - 1):
                            step += 1
                            middleTr += "<tr><td>%d</td><td>From %s, walk to %s.</td></tr>" % (
                            (step), walk[k], walk[k + 1])
                    else:
                        buses = extractedDict[dict_keys[j]]
                        correctedDictKeys = [sub.replace(" Reverse", "") for sub in dict_keys]
                        if 'Transfer' in correctedDictKeys[j]:
                            step += 1
                            middleTr += "<tr><td>%d</td><td>Do a %s, from %s to %s.</td></tr>" % (
                            (step), correctedDictKeys[j], buses[0], buses[-1])
                        elif 'LRT' in correctedDictKeys[j]:
                            step += 1
                            middleTr += "<tr><td>%d</td><td>Board %s, from %s to %s.</td></tr>" % (
                                (step), correctedDictKeys[j], buses[0], buses[-1])
                        else:
                            step += 1
                            middleTr += "<tr><td>%d</td><td>Board Bus %s, from %s to %s.</td></tr>" % (
                                (step), correctedDictKeys[j], buses[0], buses[-1])
    if end is not None:
        if end[-1] > 0:
            k = 0
            trueEndLen = getSizeOfNestedList(end)
            nestedEndLen = trueEndLen - 1
            while k < (nestedEndLen - 1):
                endTr += "<tr><td>%d</td><td>From %s, walk to %s.</td></tr>" % ((step + k + 1), end[0][k], end[0][k + 1])
                k += 1
        else:
            return -1
    endTr += "</indent></table>"

    transfer = 0
    if start[-1] > 0:
        transfer += 1
    if end[-1] > 0:
        transfer += 1

    endpara = "<p></p>" + \
              "<table> " + "<tr> <td>Transfers</td> <td></td> <td>%s</td> </tr>" % (transfer + middle[-3]) + \
              "<tr> <td>Distance</td> <td></td> <td>%.02f m</td> </tr>" % (start[-1] + middle[-2] + end[-1]) + \
              "<tr> <td>Time</td> <td></td> <td>%.02f minutes</td> </tr>" % (((start[-1] + end[-1]) * 4 / 60 ) + end[-1]) + \
              " </table"

    Html_file = open("static/route.html", "w")
    Html_file.write(message)
    Html_file.write(startTr)
    Html_file.write(middleTr)
    Html_file.write(endTr)
    Html_file.write(endpara)
    Html_file.close()


def getSizeOfNestedList(listOfElem):
    count = 0
    # Iterate over the list
    for elem in listOfElem:
        # Check if type of element is list
        if type(elem) == list:
            # Again call this function to get the size of this element
            count += getSizeOfNestedList(elem)
        else:
            count += 1
    return count


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
    if self.controller.filenames["folder"] is not None:
        try:
            self.controller.hdbdf = pd.read_csv(self.controller.filenames["folder"] + self.controller.filenames["hdb"])
            self.controller.edgesdf = pd.read_csv(
                self.controller.filenames["folder"] + self.controller.filenames["edges"])
            self.controller.busedgesdf = pd.read_csv(
                self.controller.filenames["folder"] + self.controller.filenames["busedges"])
            self.controller.busroutedf = pd.read_csv(
                self.controller.filenames["folder"] + self.controller.filenames["busroute"])
            self.controller.busnodesdf = pd.read_csv(
                self.controller.filenames["folder"] + self.controller.filenames["busnodes"])

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
