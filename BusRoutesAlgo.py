import csv

# This algorthm is still WIP. This algorihm is only considering direct buses as of now.

#print("Enter start point: ")
#start_point = input()
#print("Enter end point: ")
#end_point = input()

def BusAlgo(csvdata):
    
    start = []
    end = []
    start_stops = []
    end_stops = []
    line = 0
    transfer = 0
    least_stops = 32
    least_stops_print = ''
    
    for row in csvdata:
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

    if (least_stops != 32):
        return least_stops_print
    else:
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
      
        for i, startBus in enumerate(start_stops):
            for startStop in startBus[startBus.index(start_point):]:
                for j, endBus in enumerate(end_stops):
                    for endStop in endBus[1:endBus.index(end_point)+1]:  
                        if(startStop != '' and endStop != '' and endStop == startStop):
                            least_stops_print += (str(start_point) + " -> Bus " + str(start_stops[i][0]) + " (" + str(startBus[startBus.index(start_point):].index(startStop)) + " stops) -> " + str(endStop) + " -> Bus " + str(end_stops[j][0]) + " (" + str(endBus.index(end_point) - endBus.index(endStop)) + " stops) -> " + str(end_point) + '\n') 
                            transfer = 1
        
        if transfer == 0:
            return "There are no bus routes with 1 transfer." 
        else:
            least_stops_print = "Bus routes with " + str(transfer) + " transfer(s):" + '\n' + least_stops_print
            return least_stops_print

start_point = '65221'
end_point = '65449'

with open('csv/BusRoutes.csv', mode = 'r') as csv_file:
    csvdata = csv.reader(csv_file, delimiter = ',')
    least_stops_print = BusAlgo(csvdata)

print(least_stops_print)
