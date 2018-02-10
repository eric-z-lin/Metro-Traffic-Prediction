# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 14:23:35 2017
Subway individual commute time prediction 
@author: Eric
"""
import os
import pickle
from datetime import datetime as dt
from datetime import timedelta as td
from sklearn.linear_model import LinearRegression

'''
Baseline -- Historical Average Time
'''
#os.chdir('C:/Users/Eric.GoldenRatio/Documents/ASSIP Code/Metro Data Project/FinalCode')
os.chdir('/home/tjhsst/Documents/Eric/ASSIP/FinalCode')

'''
entireSetup:
0    1st dimension is 91 starting stations
    2nd dimension is 287 starting times, separated in 5 minute intervals
    3rd dimension is 92 ending stations
    4th dimension is 5 -- probability of going to that station, avg. travel time, std Deviation, median, destListCount
'''
pickle_in_eSetup = open('012SetupNOMAR24toAPR24.pickle', 'rb')
#pickle_in_eSetup = open('012DiscreteSetupMAR24toAPR24.pickle', 'rb')
entireSetup = pickle.load(pickle_in_eSetup)
pickle_in_eSetup.close()

    
def convertToInterval(rawTime, interval):
    minutes = convertToMinutes(rawTime)
    stime = minutes // interval  #integer division
    if(stime > 286):
        stime = 286
    return stime
    
def convertToMinutes(rawTime):
    arr = rawTime.split(':')
    arr[2] = arr[2][:2] #cut off the AM or PM
    for i in range(3):
        arr[i] = int(arr[i])
    if 'AM' in rawTime:
        if arr[0] == 12:
            arr[0] = 0
    if 'PM' in rawTime:
        if arr[0] != 12:
            arr[0] += 12
    minutes = arr[0] * 60 + arr[1]  #seconds are negligible
    return minutes

'''
Station List
'''
pickle_stations_in = open('StationList.pickle', 'rb')
stationList = pickle.load(pickle_stations_in)
pickle_stations_in.close()

#%%
'''
Input Data Formatting
'''
def findCurrentPassengers(currTime, day, interval, rawData):
    currPassengers = []
    timeFMT = '%I:%M:%S%p'
    lowerBound = dt.strptime(currTime, timeFMT)
#    timeIncrement = td(minutes = interval)
    upperBound = lowerBound
    i = 0
    for line in rawData:
        if i % 1000000 == 0:
            print(i)
        arr = line.split(',')
        arr[0] = arr[0].replace('"', '')
        arr[2] = arr[2].replace('"', '')
        arr[4] = arr[4].replace('"', '')
        if arr[0] == day:
            arr[2] = arr[2].replace('\n', '')
            arr[4] = arr[4].replace('\n', '')
            travel_minutes = convertToMinutes(arr[4]) - convertToMinutes(arr[2])
            arr[2] = dt.strptime(arr[2], timeFMT)
            arr[4] = dt.strptime(arr[4], timeFMT)
            if arr[2] < upperBound and arr[4] > upperBound and travel_minutes < 240 and arr[1] != arr[3]:
                currPassengers.append(line)
        i += 1
    return currPassengers
#%%
monthData = open('APR.csv', "r")
currentPassengersList = findCurrentPassengers('07:20:00AM', '25-APR-2017', 5, monthData)     #always has to be 5 minutes before the 2nd arg of finalPrediction                                       


#%%
'''
Days
'''
dayTypeLst = [[0]*31, [0]*28, [0]*31, [0]*30, [0]*31, [0]*30]
for month in range(len(dayTypeLst)):
    for day in range(len(dayTypeLst[month])):
        tempDateTime = dt(2017, month + 1, day + 1)
        if tempDateTime.weekday() >= 5:      #if weekend
            dayTypeLst[month][day] = 1
dayTypeLst[0][0] = 3    #New Year's
dayTypeLst[0][1] = 3    #New Year's
dayTypeLst[0][15] = 3   #MLK
dayTypeLst[0][19] = 3   #Inauguration
dayTypeLst[0][20] = 3   #Women's March
dayTypeLst[1][19] = 3   #George Washington's Birthday
dayTypeLst[4][28] = 3   #Memorial Day

#For a type of day (holiday, weekday, weekend), Generate a list of all trips starting from all stations, 2nd dim is list
def findTrips(lowerBound, upperBound, day_types, holidays, timeConstraint):    #lowerBound and upperBound are strings ex. '1-JAN-2017' and day_type is a list of ints from 0-6
    dateFMT = '%d-%b-%Y'     
    timeFMT = '%I:%M:%S%p'
    januaryMetro = open('JAN.csv', 'r')      #januaryMetro is a list of strings
    februaryMetro = open('FEB.csv', 'r')
    marchMetro = open('MAR.csv', 'r')
    aprilMetro = open('APR.csv', 'r')
    mayMetro = open('MAY.csv', 'r')
#    juneMetro = open('june.csv', 'r')
    pickle_stations = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_stations)
    trips = []      #1D, 1st dim is station, 2nd dim is trip, 3rd list is trip parsed into lists
#    for i in range(91):
#        trips.append([])
#    print(len(trips))
    #Formatting Lower and Upper Bounds...
    lowerBound_date = dt.strptime(lowerBound, dateFMT)
    upperBound_date = dt.strptime(upperBound, dateFMT)
    january_date = dt.strptime('31-JAN-2017', dateFMT)
    february_date = dt.strptime('28-FEB-2017', dateFMT)
    march_date = dt.strptime('31-MAR-2017', dateFMT)
    april_date = dt.strptime('30-APR-2017', dateFMT)
    may_date = dt.strptime('31-MAY-2017', dateFMT)
    january_date2 = dt.strptime('1-JAN-2017', dateFMT)
    february_date2 = dt.strptime('1-FEB-2017', dateFMT)
    march_date2 = dt.strptime('1-MAR-2017', dateFMT)
    april_date2 = dt.strptime('1-APR-2017', dateFMT)
    may_date2 = dt.strptime('1-MAY-2017', dateFMT)
    if lowerBound_date <= january_date and upperBound_date >= january_date2:
        print('January')
        i = 0
        next(januaryMetro)
        for line in januaryMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                if (timeConstraint in line):
                    newLine = line
                    arr = newLine.split(',') #loop through every line in file and split with ,
                    currDate = dt.strptime(arr[0].replace('"', ''), dateFMT)
                    dayOfWeek = currDate.weekday()
                    date = int(arr[0].replace('"', '').split('-')[0])
                    if holidays == True or dayTypeLst[0][date - 1] != 3:
                        if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
                            for j in range(len(arr)):
                                arr[j] = arr[j].replace('"', '')
#                            stationNum = stationList.index(arr[1])
#                            arr[0] = arr[0].replace('JAN', '01')
#                            arr[2] = dt.strptime(arr[2], timeFMT)
#                            arr[4] = arr[4].replace('\n', '')
#                            arr[4] = dt.strptime(arr[4], timeFMT)                    
#                            arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                            trips.append(line)
            i += 1
    if lowerBound_date <= february_date and upperBound_date >= february_date2:
        print('February')
        i = 0
        next(februaryMetro)
        for line in februaryMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                if (timeConstraint in line):
                    newLine = line
                    arr = newLine.split(',') #loop through every line in file and split with ,
                    currDate = dt.strptime(arr[0].replace('"', ''), dateFMT)
                    dayOfWeek = currDate.weekday()
                    date = int(arr[0].replace('"', '').split('-')[0])
                    if holidays == True or dayTypeLst[1][date - 1] != 3:
                        if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
                            for j in range(len(arr)):
                                arr[j] = arr[j].replace('"', '')
#                            stationNum = stationList.index(arr[1])
#                            arr[0] = arr[0].replace('FEB', '02')
#                            arr[2] = dt.strptime(arr[2], timeFMT)
#                            arr[4] = arr[4].replace('\n', '')
#                            arr[4] = dt.strptime(arr[4], timeFMT)                    
#                            arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                            trips.append(line)
            i += 1
    if lowerBound_date <= march_date and upperBound_date >= march_date2:
        print('March')
        i = 0
        for line in marchMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                if (timeConstraint in line):
                    newLine = line
                    arr = newLine.split(',') #loop through every line in file and split with ,
                    currDate = dt.strptime(arr[0], dateFMT)
                    dayOfWeek = currDate.weekday()
                    date = int(arr[0].replace('"', '').split('-')[0])
                    if holidays == True or dayTypeLst[2][date - 1] != 3:
                        if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
        #                    for j in range(len(arr)):
        #                        arr[j] = arr[j][1:-1]
#                            stationNum = stationList.index(arr[1])
#                            arr[0] = arr[0].replace('MAR', '03')
#                            arr[2] = dt.strptime(arr[2], timeFMT)
#                            arr[4] = arr[4].replace('\n', '')
#                            arr[4] = dt.strptime(arr[4], timeFMT)                    
#                            arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                            trips.append(line)
            i += 1
#    counter = 0
    if lowerBound_date <= april_date and upperBound_date >= april_date2:
        print("hi im april")
        i = 0
        for line in aprilMetro:
            
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                if (timeConstraint in line):
                    newLine = line
                    arr = newLine.split(',') #loop through every line in file and split with ,
                    currDate = dt.strptime(arr[0], dateFMT)
                    dayOfWeek = currDate.weekday()
                    date = int(arr[0].replace('"', '').split('-')[0])
                    if holidays == True or dayTypeLst[3][date - 1] != 3:
                        if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
        #                    print("no pls")    
        #                    for j in range(len(arr)):
        #                        arr[j] = arr[j][1:-1]
#                            stationNum = stationList.index(arr[1])
#                            arr[0] = arr[0].replace('APR', '04')
#                            arr[2] = dt.strptime(arr[2], timeFMT)
#                            arr[4] = arr[4].replace('\n', '')
#                            arr[4] = dt.strptime(arr[4], timeFMT)                    
#                            arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                            trips.append(line)
            i += 1
#    print('counter:' + str(counter))
    if lowerBound_date <= may_date and upperBound_date >= may_date2:
        print('May')
        i = 0
        for line in mayMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                if (timeConstraint in line):
                    newLine = line
                    arr = newLine.split(',') #loop through every line in file and split with ,
                    currDate = dt.strptime(arr[0], dateFMT)
                    dayOfWeek = currDate.weekday()
                    date = int(arr[0].replace('"', '').split('-')[0])
                    if holidays == True or dayTypeLst[4][date - 1] != 3:
                        if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
        #                    for j in range(len(arr)):
        #                        arr[j] = arr[j][1:-1]
#                            stationNum = stationList.index(arr[1])
#                            arr[0] = arr[0].replace('MAY', '05')
#                            arr[2] = dt.strptime(arr[2], timeFMT)
#                            arr[4] = arr[4].replace('\n', '')
#                            arr[4] = dt.strptime(arr[4], timeFMT)                    
#                            arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                            trips.append(line)
            i += 1
#    i = 0
#    for line in juneMetro:
#        if i % 300000 == 0:
#            print(i)
#        if len(line.strip()) != 0:
#            if (timeConstraint in line):
#                newLine = line
#                arr = newLine.split(',')
#                if arr[1] == station:
#                    for j in range(len(arr)):
#                        arr[j] = arr[j].replace('"', '')
#                    arr[0] = arr[0].replace('JUN', '06')
#                    arr[2] = dt.strptime(arr[2], timeFMT)
#                    arr[4] = arr[4].replace('\n', '')
#                    arr[4] = dt.strptime(arr[4], timeFMT)
#                    dayOfWeek = dt.strptime(arr[0], dateFMT).weekday()
#                    arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
#                    trips.append(line)
#        i += 1
        
    januaryMetro.close()
    februaryMetro.close()
    marchMetro.close()
    aprilMetro.close()
    mayMetro.close()
#    juneMetro.close()
    return trips

#%%
rawTripsList = findTrips('24-MAR-2017', '24-APR-2017', [1], False, 'AM')
print('done with parsing trips')
pickle_out_stations = open('1AMRawMAR24toAPR24.pickle', 'wb')
pickle.dump(rawTripsList, pickle_out_stations)
pickle_out_stations.close()


#%%
'''
Machine Learning
'''
#==============================================================================
# supervised learning:
#     1. Start Station
#     2. End Station
#     3. Start Time
#     4. Day of the week
#     5. Historical Commute Time
#     6. Historic Traffic
#     7. Add-on: Bayesian Traffic Estimation + Ghosts
#==============================================================================

#Generating Training Set
def generateTrainingSetNaive(rawParsedData): #rawParsedData is list of strings
    trainingLst = []  #to be returned
    tripFeatures = [] #to insert into trainingLst
    count = 0
    for line in rawParsedData:
        tripFeatures = []
        if(count % 100000 == 0):
            print(count)
        arr = line.split(',')
        startStation = stationList.index(arr[1])
        endStation = stationList.index(arr[3])
        startTime = convertToInterval(arr[2], 5)
        lineDate = int(arr[0][0:2])
        monthNum = 0
        if 'FEB' in line:
            monthNum = 1
        if 'MAR' in line:
            monthNum = 2
        if 'APR' in line:
            monthNum = 3
        if 'MAY' in line:
            monthNum = 4
        if 'JUN' in line:
            monthNum = 5
        dayOfWeek = dayTypeLst[monthNum][lineDate - 1]
        if(dayOfWeek != 3):
            tempDateTime = dt(2017, month + 1, lineDate + 1)
            dayOfWeek = tempDateTime.weekday()
        histTravelTime = historicalBaseline(line)
        tripFeatures.append(startStation)
        tripFeatures.append(endStation)
        tripFeatures.append(startTime)
        tripFeatures.append(dayOfWeek)
        tripFeatures.append(histTravelTime)
        trainingLst.append(tripFeatures)
        count += 1
    return trainingLst

#Generate Target Set
def generateTargetSet(rawParsedData):  #rawParsedData is list of strings
    targetLst = []   #to be returned
    count = 0
    for line in rawParsedData:
        if(count % 100000 == 0):
            print(count)
        arr = line.split(',')
        trueTravelTime = convertToMinutes(arr[4]) - convertToMinutes(arr[2])
        targetLst.append(trueTravelTime)
        count += 1
    return targetLst
    
#%%
'''
Pickle in raw parsed data
'''
pickle_in_parsed = open('1AMRawMAR24toAPR24.pickle', 'rb')
rawTripsList = pickle.load(pickle_in_parsed)
pickle_in_parsed.close()

#%%
'''
Historical Baseline
'''
def historicalBaseline(rawLine):    #from line for one passenger trip, output historical average travel time
    arr = rawLine.split(',')
    arr[2] = arr[2].replace('"', '')
    arr[2] = arr[2].replace('\n', '')
    startStationNum = stationList.index(arr[1])
    startTimeNum = convertToInterval(arr[2], 5)
    endStationNum = stationList.index(arr[3])
    if(startStationNum > 90):
        print("startStationNum: " + rawLine)
    if(startTimeNum > 286):
        print("startTimeNum: " + str(startTimeNum) + " " + rawLine)
    if(endStationNum > 90):
        print("endStationNum: " + rawLine)
    if(len(entireSetup[startStationNum]) < startTimeNum + 1):
        return 0
    return entireSetup[startStationNum][startTimeNum][endStationNum][1]
#%%
'''
Historical Testing
'''
numTest = 23816
totalError = 0
totalTripTime = 0
for i in range(numTest):
    #print(currentPassengersList[i])
    currPassengerArr = currentPassengersList[i].split(',')
    trueTravel = convertToMinutes(currPassengerArr[4])-convertToMinutes(currPassengerArr[2])
    histTravel = historicalBaseline(currentPassengersList[i])
    #print("True Travel Time: " + str(trueTravel))
    #print("Historical Predicted Travel Time: " + str(histTravel))
    totalError += abs(trueTravel - histTravel)
    totalTripTime += trueTravel

#print(totalError)
print("Average trip time: " + str(totalTripTime / numTest) + " minutes.")
print("Average error: " + str(totalError / (numTest)) + " minutes.")

#%%
'''
Dumping Target Set
'''
targetLst = generateTargetSet(rawTripsList)
print("Done with generating target list.")
pickle_out_MLList = open('1AMTargetMAR24toAPR24.pickle', 'wb')
pickle.dump(targetLst, pickle_out_MLList)
pickle_out_MLList.close()

#%%
'''
Dumping Training Set
'''
trainingLstNaive = generateTrainingSetNaive(rawTripsList)
print("Done with generating training list.")

pickle_out_MLList = open('1AMTrainingNaiveMAR24toAPR24.pickle', 'wb')
pickle.dump(trainingLstNaive, pickle_out_MLList)
pickle_out_MLList.close()

#%%
'''
Training and Target List
'''
pickle_in_MLList = open('1AMTargetMAR24toAPR24.pickle', 'rb')
targetLst = pickle.load(pickle_in_MLList)
pickle_in_MLList.close()

pickle_in_MLList = open('1AMTrainingNaiveMAR24toAPR24.pickle', 'rb')
trainingLstNaive = pickle.load(pickle_in_MLList)
pickle_in_MLList.close()
#%%
'''
Small dataset
'''
smalltrainingLstNaive = []
smalltargetLst = []
for i in range(len(trainingLstNaive)):
    if i % 5000 == 0:
        smalltrainingLstNaive.append(trainingLstNaive[i])
        smalltargetLst.append(targetLst[i])
mediumtrainingLstNaive = []
mediumtargetLst = []
for i in range(len(trainingLstNaive)):
    if i % 290 == 0:
        mediumtrainingLstNaive.append(trainingLstNaive[i])
        mediumtargetLst.append(targetLst[i])
        
largetrainingLstNaive = []
largetargetLst = []
for i in range(len(trainingLstNaive)):
    if i % 100 == 0:
        largetrainingLstNaive.append(trainingLstNaive[i])
        largetargetLst.append(targetLst[i])
        
hugetrainingLstNaive = []
hugetargetLst = []
for i in range(len(trainingLstNaive)):
    if i % 20 == 0:
        hugetrainingLstNaive.append(trainingLstNaive[i])
        hugetargetLst.append(targetLst[i])
#%%
'''
Linear Regression
'''
lr = LinearRegression()
y_pred_lr = lr.fit(trainingLstNaive, targetLst)

print('Testing with training data:')
print('Linear Regression: ', end = '')
print(lr.score(trainingLstNaive[:100], targetLst[:100]))


#%%














