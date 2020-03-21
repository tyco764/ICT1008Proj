import main
import csv
import collections
import copy
import numpy as np


# This algorthm is still WIP. This algorihm is only considering direct buses as of now.

# print("Enter start point: ")
# start_point = input()
# print("Enter end point: ")
# end_point = input()


def getdist(self, bus, startstop, endstop):
    np.set_printoptions(linewidth=1000)
    busdf = self.controller.busedgesdf.copy(deep=True)
    searchdf = busdf.loc[busdf['bus number'] == bus]

    busarr = searchdf.to_numpy()
    idx = 0
    #busarr = busarr[np.argsort(busarr[:, 0])]
    #idx = main.binSearchAlgo(self, busarr, bus, 0)

    #while busarr[idx][0] == bus and idx > -1:
        #idx -= 1
    #idx += 1

    # 1 and 4
    distance = 0
    starttemp = busarr[idx][1]


    while busarr[idx][0] == bus:
        if starttemp != startstop:
            idx += 1
            if idx == len(busarr):
                return 300  # hardcoded return 300 if not found(constant for lrt transfers or between lrts)
            starttemp = busarr[idx][1]
        else:
            break

    endtemp = busarr[idx][4]

    while busarr[idx][0] == bus:
        if endtemp != endstop:
            distance += busarr[idx][7]
            idx += 1
            if idx == len(busarr):
                return 300  # hardcoded return 300 if not found(constant for lrt transfers or between lrts)
            endtemp = busarr[idx][4]
        else:
            break


    if distance == 0:
        return 300 #hardcoded return 300 if not found(constant for lrt transfers or between lrts)

    distance += busarr[idx][7]
    return distance



def BusAlgo(self, csv_file, csvdata, start_point, end_point):
    new = []
    start = []
    end = []
    start_stops = []
    end_stops = []
    line = 0
    transfer = 0
    least_stops = 32
    least_stops_print = ''
    buses = []
    
    for i in csvdata:
            if(i):

                buses.append(i[0])
            temp = []
            for j in i:
                if(j != ''):
                    temp.append(j)
            new.append(temp)


    for row in new:
        # print(row)
        if start_point in row and end_point in row:     #direct bus found ****
            least_stops_temp = row.index(end_point) - row.index(start_point)
            if least_stops_temp > 0:
                if least_stops_temp < least_stops:
                    least_stops = least_stops_temp
                    least_stops_print = (str(least_stops) + " stop(s) with Bus Service " + row[0])
                elif least_stops_temp == least_stops:
                    least_stops_print += ", " + row[0]
        if start_point in row:
            start.append(line)
        if end_point in row:
            end.append(line)
        line += 1

    # if (least_stops != 32):
    #     return least_stops_print
    # else:
    if(1 == 1):
        csv_file.seek(0)
                      
        for i in start:  
            for j in range(i):
                next(csvdata) #skip not matched buses
            start_stops.append(next(csvdata)) #reached bus service
            csv_file.seek(0)
        
        csv_file.seek(0)
        
        for i in end:
            for i in range(i):
                next(csvdata)
            end_stops.append(next(csvdata))
            csv_file.seek(0)

       
        answer = []
        mystart = collections.deque([]) 
        for i in start:
            newBus = {}
            row = new[i]
            newBus[row[0]] = row[row.index(start_point):row.index(start_point)+1]
            mystart.append(newBus)
      
        temparray = []
        while(mystart and len(mystart[0]) < 6):

            current = mystart.popleft()
            backup = copy.deepcopy(current)
            backup2 = copy.deepcopy(current)
            backup3 = copy.deepcopy(current)

            #check for answer
            lastBus = list(current.keys())[-1]
            currentBus = 0;
            if(len(current[lastBus]) == 1):
                starting = current[lastBus][-1]
                for possibleRoute in new:
                    if possibleRoute[0] == lastBus:
                        currentBus = possibleRoute
                        break

                if end_point in currentBus and currentBus.index(end_point) >= currentBus.index(starting):
                    current[lastBus] += (currentBus[currentBus.index(starting)+1:currentBus.index(end_point)+1])
                    
                    keyCount = len(current.keys()) - 1 
                    #print( "Transfers: " + str(keyCount))
                    mycount = 0
                    for count in current.keys():
                        mycount += len(current[count])
                    #print("Bus Stops: " + str(mycount - keyCount - 1))
                    for i in current.keys():
                        for j,stops in enumerate(current[i][:-1]): 
                            pass
                            #print(getdist(self, '136','Punggol Temp Int (65009)', 'Punggol Sec/Blk 601B (65281)'))


                    answer.append([mycount - keyCount - 1,current, len(current.keys()) - 1])
                    #print(current)


            #appending part
            for possibleRoute in new:
                if possibleRoute[0] == lastBus:
                    currentBus = possibleRoute
                    break;
            #print(backup)
            #print(currentBus)
            if currentBus.index(backup[lastBus][-1]) + 1 < len(currentBus):
               
                start = currentBus.index(backup[lastBus][-1])
                end = currentBus.index(backup[lastBus][-1])
                backup[lastBus].append(currentBus[start+1])
             
               
                mystart.append(backup)


            for possibleRoute in new:

                if len([i for i in backup2.keys() if i in possibleRoute]) == 0  and backup2[lastBus][-1] in possibleRoute and len(backup2[lastBus]) > 1 and backup2[lastBus][-1] != end_point:
                    
                    temp = backup2[lastBus][-1]
                    backup2[possibleRoute[0]] = [temp]
                    
                    mystart.append(backup2)
                    #print(backup2)
                    backup2 = copy.deepcopy(backup3)
                                    
    return answer

                        # print(new)
        # print(start_stops)
        # for i, startBus in enumerate(start_stops):
        #     for startStop in startBus[startBus.index(start_point):]:
        #         for j, endBus in enumerate(end_stops):
        #             for endStop in endBus[1:endBus.index(end_point)+1]:  
        #                 if(startStop != '' and endStop != '' and endStop == startStop):
        #                     least_stops_print += (str(start_point) + " -> Bus " + str(start_stops[i][0]) + " (" + str(startBus[startBus.index(start_point):].index(startStop)) + " stops) -> " + str(endStop) + " -> Bus " + str(end_stops[j][0]) + " (" + str(endBus.index(end_point) - endBus.index(endStop)) + " stops) -> " + str(end_point) + '\n') 
        #                     transfer = 1

        # if transfer == 0:
        #     return "There are no bus routes with 1 transfer." 
        # else:
        #     least_stops_print = "Bus routes with " + str(transfer) + " transfer(s):" + '\n' + least_stops_print
        #     return least_stops_print

# start_point = '65221'
# end_point = '65449'

# with open('csv/BusRoutes.csv', mode = 'r') as csv_file:
# csvdata = csv.reader(csv_file, delimiter = ',')
# least_stops_print = BusAlgo(csvdata)

# print(least_stops_print)
