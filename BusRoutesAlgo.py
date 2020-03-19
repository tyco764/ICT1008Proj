import csv
import collections


# This algorthm is still WIP. This algorihm is only considering direct buses as of now.

# print("Enter start point: ")
# start_point = input()
# print("Enter end point: ")
# end_point = input()

def BusAlgo(csv_file, csvdata, start_point, end_point):
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
        buses.append(i[0])
        temp = []
        for j in i:
            if (j != ''):
                temp.append(j)
        new.append(temp)

    for row in new:
        # print(row)
        if start_point in row and end_point in row:  # direct bus found ****
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

    if (least_stops != 32):
        return least_stops_print
    else:
        csv_file.seek(0)

        for i in start:
            for j in range(i):
                next(csvdata)  # skip not matched buses
            start_stops.append(next(csvdata))  # reached bus service
            csv_file.seek(0)

        csv_file.seek(0)

        for i in end:
            for i in range(i):
                next(csvdata)
            end_stops.append(next(csvdata))
            csv_file.seek(0)

        print(start)
        answer = []
        mystart = collections.deque([])
        for i in start:
            row = new[i]
            mystart.append([row[0]] + row[row.index(start_point):row.index(start_point) + 2])
        print(mystart)

        while (mystart and len(mystart[0]) < 36):
            mydelay = 0
            transferCount = 0
            stopCounter = 0
            current = mystart.popleft()
            if (current[-1] == end_point):
                if (current[0] != ''):
                    answer.append(current)
                    currentBus = current[0]
                    mystr = currentBus
                    mystr += "-> "
                    for i in current[1:]:
                        if (mydelay == 1):
                            mydelay = 0
                            continue
                        elif (len(i) > 4):
                            stopCounter += 1
                            mystr += " "
                            mystr += i
                        else:
                            if currentBus == i:
                                mydelay = 1
                                continue
                            else:
                                transferCount += 1
                                currentBus = i
                                mystr += " "
                                mystr += i
                                mystr += "-> "
                    print("Transfers:" + str(transferCount))
                    print("Stops:" + str(stopCounter))
                    transferCount = 0
                    stopCounter = 0

                    print(mystr)
            for possibleRoute in new:
                if (current[-1] in possibleRoute):
                    if possibleRoute.index(current[-1]) + 1 < len(possibleRoute):
                        mystart.append(current + [possibleRoute[0]] + possibleRoute[possibleRoute.index(
                            current[-1]):possibleRoute.index(current[-1]) + 2])

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
