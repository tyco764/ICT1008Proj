import csv

# This algorthm is still WIP. This algorihm is only considering direct buses as of now.

#print("Enter start point: ")
#start_point = input()
#print("Enter end point: ")
#end_point = input()

start_point = '65009'
#start_point = '65171'

#print(start_point)

end_point = '65169'
#end_point = '65129'

least_stops = 32

with open('BusRoutes.csv', mode = 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter = ',')
    
    for row in csv_reader:
        #print(row)
        if start_point in row and end_point in row:
            #print(row[0] + " have.")
            #print(row.index(end_point))
            #print(row.index(start_point))
            #print(str(len(row)))
            least_stops_temp = row.index(end_point) - row.index(start_point)
            #print(least_stops_temp)
            if least_stops_temp > 0:
                #least_stops_temp = row.index(end_point) - row.index(start_point)
                #print(least_stops_temp)
                if least_stops_temp < least_stops:
                    least_stops = least_stops_temp
                    least_stops_print = (str(least_stops) + " stop(s) with Bus Service " + row[0])
                elif least_stops_temp == least_stops:
                    least_stops_print += ", " + row[0]
    
    if least_stops == 100:
        print("There are no direct buses.")
    else:
        print(least_stops_print)