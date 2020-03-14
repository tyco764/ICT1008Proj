import csv

# This algorthm is still WIP. This algorihm is only considering direct buses as of now.

#print("Enter start point: ")
#start_point = input()
#print("Enter end point: ")
#end_point = input()

def BusAlgo(csvdata):
    least_stops = 32
    for row in csvdata:
        # print(row)
        if start_point in row and end_point in row:
            least_stops_temp = row.index(end_point) - row.index(start_point)
            if least_stops_temp > 0:
                if least_stops_temp < least_stops:
                    least_stops = least_stops_temp
                    least_stops_print = (str(least_stops) + " stop(s) with Bus Service " + row[0])
                elif least_stops_temp == least_stops:
                    least_stops_print += ", " + row[0]

    if (least_stops != 32):
        return least_stops_print
        #print(least_stops_print)
    else:
        return "There are no direct buses."
        #print("There are no direct buses.")

start_point = '65009'
end_point = '65169'

least_stops = 32
least_stops_print = ""
with open('csv/BusRoutes.csv', mode = 'r') as csv_file:
    csvdata = csv.reader(csv_file, delimiter = ',')
    least_stops_print = BusAlgo(csvdata)

print(least_stops_print)

