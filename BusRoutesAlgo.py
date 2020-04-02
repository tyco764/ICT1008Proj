import main
import csv
import collections
import copy
import numpy as np

def getdist(self, bus, startstop, endstop):
    np.set_printoptions(linewidth=1000)
    busdf = self.controller.busedgesdf.copy(deep=True)
    searchdf = busdf[busdf['bus number'] == bus]
    busarr = searchdf.to_numpy()

    if len(busarr) == 0:
        return -1        #means there is an error with getdist

    idx = 0
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



def BusAlgo(self, busarr, csv_file, csvdata, start_point, end_point):
    thisBus = []
    oppBus = []
    with open('csv/busnodes.csv', mode = 'r') as csv_file2:
        
        reader = csv.DictReader(csv_file2)
        for row in reader:
            thisBus.append(row['fromNode'])
            oppBus.append(row['OppBusStop'])



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
                myOppBus = []
                for i in currentBus[currentBus.index(starting):]:
                    if(i in thisBus):
                        if(oppBus[thisBus.index(i)] != '0'):
                            myOppBus.append(oppBus[thisBus.index(i)])
                
                if ((end_point in currentBus and currentBus.index(end_point) >= currentBus.index(starting)) or end_point in myOppBus):



                    if(end_point in myOppBus): #walking code adding to dict
                        tempLastBus = thisBus[oppBus.index(end_point)]
                        current[lastBus] += (currentBus[currentBus.index(starting)+1:currentBus.index(tempLastBus)+1])
                        current["walk"] = [current[lastBus][-1], end_point];
                        
                       
                    else:
                        
                        current[lastBus] += (currentBus[currentBus.index(starting)+1:currentBus.index(end_point)+1])

                    
                    keyCount = len(current.keys()) - 1 

                    mycount = 0
                    for count in current.keys():
                        mycount += len(current[count])

                    totalDistance = 0
                    time = 0
                    for i in current.keys():
                        for j,stops in enumerate(current[i][:-1]): 
                            if(i != 'walk'):
                                speed = float(new[buses.index(i)][1])
                                dist = getdist(self, lastBus, current[i][j], current[i][j+1])
                                totalDistance += dist
                                time += (dist/1000)/speed*60
                            else:
                                start = main.binSearchAlgo(self, busarr, current[i][j], 0)
                                end = main.binSearchAlgo(self, busarr, end_point, 0)
                                dist = main.getdistance(busarr[start][1], busarr[start][2], busarr[end][1], busarr[end][2])
                                totalDistance += dist
                                time += (dist / 1000) / 4 * 60

                    transfers = len(current.keys()) - 1
                    if 'walk' in current.keys():
                        transfers -= 1
                    answer.append([mycount - keyCount - 1,current, transfers, totalDistance, time])


            #appending part
            for possibleRoute in new:
                if possibleRoute[0] == lastBus:
                    currentBus = possibleRoute
                    break;

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

                    backup2 = copy.deepcopy(backup3)
                                    
    return answer
