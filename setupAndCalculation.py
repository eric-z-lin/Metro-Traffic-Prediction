# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 09:56:44 2017

@author: Eric Lin

For every station: generates the matrix of the probability for a user to go to another station and the time it takes to get there, with SD
"""
import os
from operator import itemgetter
from datetime import datetime as dt
from datetime import timedelta as td
import pickle
import statistics as stat
import scipy.stats as st
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import numpy as np
import warnings
from sklearn.metrics import mean_squared_error

#os.chdir('C:/Users/Eric.GoldenRatio/Documents/ASSIP Code/Metro Data Project/FinalCode')
os.chdir('/home/tjhsst/Documents/Eric/ASSIP/FinalCode')

dateFMT = '%d-%b-%Y'
timeFMT = '%I:%M:%S%p'

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
def findTrips(lowerBound, upperBound, day_types, holidays):    #lowerBound and upperBound are strings ex. '1-JAN-2017' and day_type is a list of ints from 0-6
    januaryMetro = open('JAN.csv', 'r')      #januaryMetro is a list of strings
    februaryMetro = open('FEB.csv', 'r')
    marchMetro = open('MAR.csv', 'r')
    aprilMetro = open('APR.csv', 'r')
    mayMetro = open('MAY.csv', 'r')
#    juneMetro = open('june.csv', 'r')
    pickle_stations = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_stations)
    trips = []      #3D, 1st dim is station, 2nd dim is trip, 3rd list is trip parsed into lists
    for i in range(91):
        trips.append([])
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
                newLine = line
                arr = newLine.split(',') #loop through every line in file and split with ,
                currDate = dt.strptime(arr[0].replace('"', ''), dateFMT)
                dayOfWeek = currDate.weekday()
                date = int(arr[0].replace('"', '').split('-')[0])
                if holidays == True or dayTypeLst[0][date - 1] != 3:                    Q
                    if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
                        for j in range(len(arr)):
                            arr[j] = arr[j].replace('"', '')
                        stationNum = stationList.index(arr[1])
                        arr[0] = arr[0].replace('JAN', '01')
                        arr[2] = dt.strptime(arr[2], timeFMT)
                        arr[4] = arr[4].replace('\n', '')
                        arr[4] = dt.strptime(arr[4], timeFMT)                    
                        arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                        trips[stationNum].append(arr)
            i += 1
    if lowerBound_date <= february_date and upperBound_date >= february_date2:
        print('February')
        i = 0
        next(februaryMetro)
        for line in februaryMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                newLine = line
                arr = newLine.split(',') #loop through every line in file and split with ,
                currDate = dt.strptime(arr[0].replace('"', ''), dateFMT)
                dayOfWeek = currDate.weekday()
                date = int(arr[0].replace('"', '').split('-')[0])
                if holidays == True or dayTypeLst[1][date - 1] != 3:
                    if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
                        for j in range(len(arr)):
                            arr[j] = arr[j].replace('"', '')
                        stationNum = stationList.index(arr[1])
                        arr[0] = arr[0].replace('FEB', '02')
                        arr[2] = dt.strptime(arr[2], timeFMT)
                        arr[4] = arr[4].replace('\n', '')
                        arr[4] = dt.strptime(arr[4], timeFMT)                    
                        arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                        trips[stationNum].append(arr)
            i += 1
    if lowerBound_date <= march_date and upperBound_date >= march_date2:
        print('March')
        i = 0
        for line in marchMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                newLine = line
                arr = newLine.split(',') #loop through every line in file and split with ,
                currDate = dt.strptime(arr[0], dateFMT)
                dayOfWeek = currDate.weekday()
                date = int(arr[0].replace('"', '').split('-')[0])
                if holidays == True or dayTypeLst[2][date - 1] != 3:
                    if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
    #                    for j in range(len(arr)):
    #                        arr[j] = arr[j][1:-1]
                        stationNum = stationList.index(arr[1])
                        arr[0] = arr[0].replace('MAR', '03')
                        arr[2] = dt.strptime(arr[2], timeFMT)
                        arr[4] = arr[4].replace('\n', '')
                        arr[4] = dt.strptime(arr[4], timeFMT)                    
                        arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                        trips[stationNum].append(arr)
            i += 1
#    counter = 0
    if lowerBound_date <= april_date and upperBound_date >= april_date2:
        print("hi im april")
        i = 0
        for line in aprilMetro:
            
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
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
                        stationNum = stationList.index(arr[1])
                        arr[0] = arr[0].replace('APR', '04')
                        arr[2] = dt.strptime(arr[2], timeFMT)
                        arr[4] = arr[4].replace('\n', '')
                        arr[4] = dt.strptime(arr[4], timeFMT)                    
                        arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                        trips[stationNum].append(arr)
            i += 1
#    print('counter:' + str(counter))
    if lowerBound_date <= may_date and upperBound_date >= may_date2:
        print('May')
        i = 0
        for line in mayMetro:
            if i % 1000000 == 0:
                print(i)
            if len(line.strip()) != 0:
                newLine = line
                arr = newLine.split(',') #loop through every line in file and split with ,
                currDate = dt.strptime(arr[0], dateFMT)
                dayOfWeek = currDate.weekday()
                date = int(arr[0].replace('"', '').split('-')[0])
                if holidays == True or dayTypeLst[4][date - 1] != 3:
                    if currDate >= lowerBound_date and currDate <= upperBound_date and dayOfWeek in day_types: #current line's date is type of weekday(including weekends) we want
    #                    for j in range(len(arr)):
    #                        arr[j] = arr[j][1:-1]
                        stationNum = stationList.index(arr[1])
                        arr[0] = arr[0].replace('MAY', '05')
                        arr[2] = dt.strptime(arr[2], timeFMT)
                        arr[4] = arr[4].replace('\n', '')
                        arr[4] = dt.strptime(arr[4], timeFMT)                    
                        arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
                        trips[stationNum].append(arr)
            i += 1
#    i = 0
#    for line in juneMetro:
#        if i % 300000 == 0:
#            print(i)
#        if len(line.strip()) != 0:
#            newLine = line
#            arr = newLine.split(',')
#            if arr[1] == station:
#                for j in range(len(arr)):
#                    arr[j] = arr[j].replace('"', '')
#                arr[0] = arr[0].replace('JUN', '06')
#                arr[2] = dt.strptime(arr[2], timeFMT)
#                arr[4] = arr[4].replace('\n', '')
#                arr[4] = dt.strptime(arr[4], timeFMT)
#                dayOfWeek = dt.strptime(arr[0], dateFMT).weekday()
#                arr.append(dayOfWeek)       #append the day of the week to the end, Monday is 0 and Sunday is 6
#                trips.append(arr)
#        i += 1
        
    januaryMetro.close()
    februaryMetro.close()
    marchMetro.close()
    aprilMetro.close()
    mayMetro.close()
#    juneMetro.close()
    return trips

#Given the trips of a station, sort the 2D list by the time of the day
def sortTrips(trips):
    return sorted(trips, key = itemgetter(2))

#Given the sorted trips of a station, pick out of all of the weekdays
def pickWeekDays(sortedTrips):
    weekDays = []
    for i in range(len(sortedTrips)):
        newTrip = sortedTrips[i]
        if newTrip[5] < 5: 
            weekDays.append(newTrip)
    return weekDays      

#Given the sorted trips of a station, pick out of all of the weekends
def pickWeekendDays(sortedTrips):
    weekendDays = []
    for i in range(len(sortedTrips)):
        newTrip = sortedTrips[i]
        if newTrip[5] > 4:      
            weekendDays.append(newTrip)
    return weekendDays 

#Given sorted week or weeekend days, make 2D list, with 1st dim is time interval, 2nd dim as probabilities and average travel time
def calcProb(sortedParsedDays, timeInterval, lowerBound):       #timeInterval is number of minutes
    currTime = dt(1900, 1, 1, 0, 0, 0)      #begin looking at trips starting at 12am + one timeInterval
    timeIncrement = td(minutes = timeInterval)
    currTime = currTime + timeIncrement
    tripCount = 0               #count of number of trips to ALL stations in the time interval
    destListCount = [0]*92      #count of number of trips to a station in the time interval
    destListSum = [0]*92        #sum of the travel times to a station in the time interval
    stationData = []           #1st dim is probability of going to that station, 2nd dim is avg. travel time
    entireList = []             #lsit of stationDatas
    buildSD = []              #list 
    pickle_in = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_in)    #stationList is a list of stations in alphabetical order
    enterTime = currTime
    for i in range(len(sortedParsedDays)):
        if i % 30000 == 0:
            print(i)
            print(len(entireList))
        enterTime = sortedParsedDays[i][2]
        if enterTime < currTime:
            travelTimeDelta = sortedParsedDays[i][4] - enterTime
            travelTime = travelTimeDelta.seconds // 60      #travelTime is in minutes
            if travelTime < 240:        #ignore all trip times that are longer than 4 hours
                tripCount += 1
                stationNum = stationList.index(sortedParsedDays[i][3])
                destListCount[stationNum] += 1
                destListSum[stationNum] += travelTime  
                buildSD.append(travelTime)
        else:
            if tripCount == 0:
                for i in range(0, 92):
                    stationData.append([0.0, 0.0, 0.0, 0])
            else:
                for i in range(0, 92):
                    stationProbability = destListCount[i] / tripCount
                    stationAvg = 0.0
                    stdDeviation = 0.0
                    median = 0.0
                    if destListCount[i] > lowerBound:       #ignore all trajectories with less than lowerBound trips
                        buildSD = removeOutliers(buildSD)
                        stationAvg = destListSum[i] / destListCount[i]
                        stdDeviation= stat.stdev(buildSD)
                        median = stat.median(buildSD)
                    newStationLst = []
                    newStationLst.append(stationProbability)
                    newStationLst.append(stationAvg)
                    newStationLst.append(stdDeviation)
                    newStationLst.append(median)
                    newStationLst.append(destListCount[i])
                    #newStationLst.append([stationProbability, stationAvg])
                    stationData.append(newStationLst)
            entireList.append(stationData)
            tripCount = 0
            destListCount = [0]*92
            destListSum = [0]*92
            stationData = []
            buildSD = []
            currTime = currTime + timeIncrement
            while currTime < enterTime:
                currTime = currTime + timeIncrement
                stationData = [[0.0, 0.0, 0.0, 0.0, 0]] * 92
                entireList.append(stationData)
            stationData = []
    print(currTime)
    print(enterTime)
    pickle_in.close()        
    return entireList

def removeOutliers(lst):
    lst.sort()
    sd = stat.stdev(lst)
    mean = stat.mean(lst)
    removeLst = []
    if len(lst) > 3:
        for i in range(len(lst)):
            if abs(lst[i] - mean) > 3 * sd:
                removeLst.append(lst[i])
        for i in range(len(removeLst)):
            lst.remove(removeLst[i])
    return lst

def calcDiscreteProb(sortedParsedDays, timeInterval, lowerBound):
    currTime = dt(1900, 1, 1, 0, 0, 0)      #begin looking at trips starting at 12am + one timeInterval
    timeIncrement = td(minutes = timeInterval)
    currTime = currTime + timeIncrement
    tripCount = 0               #count of number of trips to ALL stations in the time interval
    destListCount = [0]*92      #count of number of trips to a station in the time interval
    destListSum = [0]*92        #sum of the travel times to a station in the time interval
    stationData = []           #1st dim is probability of going to that station, 2nd dim is avg. travel time
    entireList = []             #lsit of stationDatas
    dstr = []              #list 
    pickle_in = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_in)    #stationList is a list of stations in alphabetical order
    enterTime = currTime
    for i in range(len(sortedParsedDays)):
        if i % 30000 == 0:
            print(i)
            print(len(entireList))
        enterTime = sortedParsedDays[i][2]
        if enterTime < currTime:
            travelTimeDelta = sortedParsedDays[i][4] - enterTime
            travelTime = travelTimeDelta.seconds // 60      #travelTime is in minutes
            if travelTime < 200:        #ignore all trip times that are longer than 4 hours
                tripCount += 1
                stationNum = stationList.index(sortedParsedDays[i][3])
                destListCount[stationNum] += 1
                destListSum[stationNum] += travelTime  
                dstr.append(travelTime)
        else:
            if tripCount == 0:
                for i in range(0, 92):
                    stationData.append([0.0, 0.0, 0.0, 0])
            else:
                for i in range(0, 92):
                    stationProbability = destListCount[i] / tripCount
                    stationAvg = 0.0
                    normedDstrOut = [0]
                    if destListCount[i] > lowerBound:       #ignore all trajectories with less than lowerBound trips
                        stationAvg = destListSum[i] / destListCount[i]
                        normedDstrOut= generateDiscreteTimeDistribution(dstr, timeInterval)
                    newStationLst = []
                    newStationLst.append(stationProbability)
                    newStationLst.append(stationAvg)
                    newStationLst.append(normedDstrOut)
                    newStationLst.append(destListCount[i])
                    #newStationLst.append([stationProbability, stationAvg])
                    stationData.append(newStationLst)
            entireList.append(stationData)
            tripCount = 0
            destListCount = [0]*92
            destListSum = [0]*92
            stationData = []
            dstr = []
            currTime = currTime + timeIncrement
            while currTime < enterTime:
                currTime = currTime + timeIncrement
                stationData = [[0.0, 0.0, 0.0, 0]] * 92
                entireList.append(stationData)
            stationData = []
    print(currTime)
    print(enterTime)
    pickle_in.close()        
    return entireList

def generateDiscreteTimeDistribution(lst, tInterval):
    lst.sort()
    dstrOut = [0] * (200 // tInterval)
    for tripTime in lst:
        index = tripTime // tInterval
        dstrOut[index] += 1
    normedDstrOut = [float(i)/sum(dstrOut) for i in dstrOut]
    return normedDstrOut

def generateSetupList(parsedTripsList, lowerBound, upperBound, day_types, interval, lowerThreshold, holidays, discrete):
    pickle_in_stations = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_in_stations)
    pickle_in_stations.close()
    result_list = []
    for i in range(len(parsedTripsList)):
        print('Working on ' + stationList[i] + ', station number ' + str(i))
        sortedViennaTrips = sortTrips(parsedTripsList[i])
    
        wkDays = pickWeekDays(sortedViennaTrips)
    #    weDays = pickWeekendDays(sortedViennaTrips)
        if discrete == True:
            wkDayresultLst = calcDiscreteProb(wkDays, interval, lowerThreshold)
        else:
            wkDayresultLst = calcProb(wkDays, interval, lowerThreshold)
        result_list.append(wkDayresultLst)
    return result_list
#%%
#pickle_in_stations = open('StationList.pickle', 'rb')
#stationList = pickle.load(pickle_in_stations)
##for i in range(len(stationList)):
##for i in range(82, 83):     #Vienna only
#
#parsedTripsList = findTrips('1-JAN-2017', '1-JAN-2017', [6])
#
#
#for i in range(len(parsedTripsList)):
#    print('Working on ' + stationList[i] + ', station number ' + str(i))
#    sortedViennaTrips = sortTrips(parsedTripsList[i])
#
#    wkDays = pickWeekDays(sortedViennaTrips)
##    weDays = pickWeekendDays(sortedViennaTrips)
#    
#    wkDayresultLst = calcProb(wkDays, 5, 1)
##    weDayresultLst = calcProb(weDays, 5, 1)
#    
#    pickle_result_wkday_out = open(stationList[i] + 'AprilTuesdaysResultList5.pickle', 'wb')
#    pickle.dump(wkDayresultLst, pickle_result_wkday_out)
#    pickle_result_wkday_out.close()
##    pickle_result_weday_out = open(stationList[i] + 'AprilTuesdaysResultList5.pickle', 'wb')
##    pickle.dump(weDayresultLst, pickle_result_weday_out)
##    pickle_result_weday_out.close()

#print(generateDiscreteTimeDistribution([25, 30, 20, 15, 10, 5, 3, 2, 6], 5))
parsedTripsList = findTrips('7-FEB-2017', '7-MAR-2017', [0, 1, 2], False)
print('done with parsing trips')
pickle_out_stations = open('012ParsedFEB7toMAR7.pickle', 'wb')
pickle.dump(parsedTripsList, pickle_out_stations)
pickle_out_stations.close()
#pickle_in_stations = open('012ParsedFEB7toMAR7.pickle', 'rb')
#parsedTripsList = pickle.load(pickle_in_stations)
#pickle_in_stations.close()
#%%
entireSetup = generateSetupList(parsedTripsList, '7-FEB-2017', '7-MAR-2017', [0, 1, 2], 5, 2, False, False)
#entireSetup = generateSetupList(parsedTripsList, '24-MAR-2017', '24-APR-2017', [0, 1, 2], 5, 2, False, True)

pickle_out_eSetup = open('012SetupFEB7toMAR7.pickle', 'wb')
#pickle_out_eSetup = open('012SetupNOMAR24toAPR24.pickle', 'wb')
pickle.dump(entireSetup, pickle_out_eSetup)
pickle_out_eSetup.close()

#%%
pickle_stations_in = open('StationList.pickle', 'rb')
stationList = pickle.load(pickle_stations_in)
pickle_stations_in.close()

'''
Weather
'''
pickle_weather_in = open('meterologyJantoJun.pickle', 'rb')
weather_day_lst = pickle.load(pickle_weather_in)    #index 2 is avg temp, 5 is avg dew pt, 8 is avg humidity, 11 is avg sea lvl press., 14 is avg visibility, 17 is avg wind, 19 is precip., 20 is events

weatherDayLst_avg = []
for month in weather_day_lst:
    tempMonth = []
    for i in month:
        tempLst = [i[2], i[5], i[8], i[11], i[14], i[17], i[19]]
        if 'Rain' in i[20] and 'Snow' in i[20] and 'Thunderstorm' in i[20]:             #0 is nothing, 1 is rain, 2 is fog, 3 is Thunderstorm, 4 is snow, 5 is rain & thunderstorm, 6 is fog, rain, & snow, 7 is rain, snow, & thunderstorm, 
            tempLst.append(7)    
        elif 'Rain' in i[20] and 'Snow' in i[20] and 'Fog' in i[20]:
            tempLst.append(6)
        elif 'Rain' in i[20] and 'Thunderstorm' in i[20]:
            tempLst.append(5)
        elif 'Snow' in i[20]:
            tempLst.append(4)
        elif 'Thunderstorm' in i[20]:
            tempLst.append(3)
        elif 'Fog' in i[20]:
            tempLst.append(2)
        elif 'Rain' in i[20]:
            tempLst.append(1)
        else:
            tempLst.append(0)            
        tempMonth.append(tempLst)
    weatherDayLst_avg.append(tempMonth)
        

pickle_weather_in .close()


'''
Station Clusters
'''
stationClusterString = '0 0 4 5 7 0 3 1 1 7 0 2 1 7 7 7 7 0 7 3 0 1 3 1 7 1 4 4 2 4 4 1 0 1 7 3 7 1 1 3 1 1 2 3 2 1 1 7 4 4 4 0 1 3 4 0 1 3 3 7 0 0 0 0 3 3 1 7 7 2 0 3 6 0 1 3 7 3 7 3 1 7 1 7 3 1 0 0 7 1 7'
stationClusterLst = stationClusterString.split(' ')
for i in range(len(stationClusterLst)):
    stationClusterLst[i] = int(stationClusterLst[i])
    
def calcBayes(startingStation, stime, travel_time, day_type, interval, sd, median):     #time is an int from 0 to length of startStationList; day_type is either wkDay or weDay   
    
#    pickle_startStation_in = open(startingStation + day_type + 'ResultList5.pickle', 'rb')
#    startStationList = pickle.load(pickle_startStation_in)
    bayesNumList = []       #each index is for a station
#    priorProbList = startStationList[stime]          #2D
    priorProbList = entireSetup[stationList.index(startingStation)][stime]
    denominator = 0
    for i in range(len(priorProbList)):
        num1 = findTravelProb(priorProbList, i, travel_time, interval, sd, median)
        numerator = num1 * priorProbList[i][0]
        bayesNumList.append(numerator)  
        denominator += numerator
    if denominator == 0:
        bayesNumList = [0]
        return bayesNumList
    for i in range(len(bayesNumList)):
        bayesNumList[i] = bayesNumList[i] / denominator
        if bayesNumList[i] != bayesNumList[i]:
            print('Found the NaN!')
    return bayesNumList         #1D: probability of G exiting at A

def calcDiscreteBayes(startingStation, stime, travel_time, day_type, interval):
    bayesNumList = []       #each index is for a station
#    priorProbList = startStationList[stime]          #2D
    priorProbList = entireSetup[stationList.index(startingStation)][stime]
    denominator = 0
    for i in range(len(priorProbList)):
        num1 = findTravelProbDiscrete(priorProbList, i, travel_time, interval)
        numerator = num1 * priorProbList[i][0]
        bayesNumList.append(numerator)  
        denominator += numerator
    if denominator == 0:
        bayesNumList = [0]
        return bayesNumList
    for i in range(len(bayesNumList)):
        bayesNumList[i] = bayesNumList[i] / denominator
        if bayesNumList[i] != bayesNumList[i]:
            print('Found the NaN!')
    return bayesNumList         #1D: probability of G exiting at A
   
def calcStationProbML(startingStation, stime, travel_time, line, mlType):
#    print(line)
    lineLst = []
    arr = line.split(',')
    for i in range(len(arr)):
        arr[i] = arr[i].replace('"', '')
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
    lineDayType = dayTypeLst[monthNum][lineDate - 1]
    lineStartStation = stationList.index(arr[1])
    lineStartTime = convertTime(arr[2])
    if lineStartTime > 0:
        lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
        lineStationCluster = stationClusterLst[lineStartStation]
        lineLst.append(lineDayType)
        lineLst.append(lineStartStation)
        lineLst.append(lineStartTime)
        lineLst.extend(lineWeatherLst)
        lineLst.append(lineStationCluster)
    if mlType == 'KNC':
        pickle_KNC_in = open('FebMarchWholeKNC.pickle', 'rb')
        ml = pickle.load(pickle_KNC_in)
        pickle_KNC_in.close()
    elif mlType == 'MLP':
        pickle_MLP_in = open('FebMarchWholeMLP.pickle', 'rb')
        ml = pickle.load(pickle_MLP_in)
        pickle_MLP_in.close()
    elif mlType == 'GBC':
        pickle_GBC_in = open('FebMarchWholeGBC.pickle', 'rb')
        ml = pickle.load(pickle_GBC_in)
        pickle_GBC_in.close()
    elif mlType == 'ABC':
        pickle_ABC_in = open('FebMarchWholeABC.pickle', 'rb')
        ml = pickle.load(pickle_ABC_in)
        pickle_ABC_in.close()
    stationProbList = ml.predict_proba(np.array(lineLst))
#    for i in stationProbList[0]:
#        print(i, end = ' ')
    return stationProbList[0]
    
def convertTime(rawTime):
    timeFMT = '%I:%M:%S%p'
    groundTime = '04:00:00AM'
    timeDiff = dt.strptime(rawTime, timeFMT) - dt.strptime(groundTime, timeFMT)
    timeDiff = timeDiff.total_seconds()
    timeDiff = timeDiff // 60       #minutes since 4am
    return timeDiff
    
def findTravelProb(startStationProbList, endStationNum, travel_time, interval, sd, median):       #uses SD
    stdDeviation = startStationProbList[endStationNum][2]    
    mean = startStationProbList[endStationNum][1]
    if median == True:
        mean = startStationProbList[endStationNum][3] #actually the median
    if mean == 0:
        return 0
    if sd == False:
        stdDeviation = 0.001
    z_score = 0
    resultProb = 1
    if stdDeviation != 0:
        z_score = (travel_time - mean) / stdDeviation
        if travel_time > mean:
            resultProb = 1 - st.norm.cdf(z_score)
    else:
        if abs(mean // interval - travel_time // interval) < 2:
            resultProb = 1
        else:
            resultProb = 0
    return resultProb

def findTravelProbDiscrete(startStationProbList, endStationNum, travel_time, interval):
    mean = startStationProbList[endStationNum][1]
    dstr = startStationProbList[endStationNum][2]
    if mean == 0:
        return 0
    index = travel_time // interval
    if len(dstr) <= index:
        return 0
    else:
        return dstr[index]

def findTimeDistribution(startingStation, stime, currTime, day_type, interval, threshold, sd, median):    #calculates the probability of G exiting in time t1 given G didn't exit before t2
#    pickle_startStation_in = open(startingStation + 'AprilTuesdays' + 'ResultList5.pickle', 'rb')
#    startStationList = pickle.load(pickle_startStation_in)
#    startStationProbList = startStationList[stime]
    startStationProbList = entireSetup[stationList.index(startingStation)][stime]
    resultList = []
    for i in range(len(startStationProbList)):
        thresholdCheck = 1
        t1 = currTime 
        tempList = []
#        first_probability = 0
#        last_probability = 0
#        asdf = 0
        stdDeviation = startStationProbList[i][2]                   #t2 is current time
        mean = startStationProbList[i][1]
        if median == True:
            mean = startStationProbList[i][3]
        if sd == False:
            stdDeviation = 0.001
        while thresholdCheck > threshold and len(tempList) < 50:
            resultValue = 0
            if mean == 0:
                tempList.append(resultValue)
                thresholdCheck = 0
#            elif stdDeviation == 0:
#                exitProb = 0
#                if mean - t1 < interval:
#                    exitProb = 1
#                tempList.append(exitProb)
#                thresholdCheck = 0
            else:
                if stdDeviation != 0:
                    t1_zscore = (t1 - mean) / stdDeviation
                    t1_zscore2 = (t1 + interval - mean) / stdDeviation
                    denom_zscore = (currTime - mean) / stdDeviation
                    cdfList = st.norm.cdf([t1_zscore, t1_zscore2, denom_zscore])
                    t1_zscore_cdf = cdfList[0]
                    t1_zscore2_cdf = cdfList[1]
                    denom_cdf = cdfList[2]
                    thresholdCheck = 1 - t1_zscore2_cdf
                    t1_prob = t1_zscore2_cdf - t1_zscore_cdf
                    denom = 1 - denom_cdf
                    resultValue = t1_prob / denom
#                    if resultValue != resultValue:
#                        print(str(t1_prob) + ' ' + str(denom))
#                    asdf = denom
                else: 
                    if mean - interval > t1:
                        while mean > t1 and len(tempList) < 59:
                            tempList.append(0)
                            t1 += interval
                        resultValue = 1
                        thresholdCheck = 0
#                if resultValue == 0:
#                    print('0: ' + str(t1) + ' ' + str(thresholdCheck))
#                if len(tempList) == 0:
#                    first_probability = t1_zscore_cdf
#                last_probability = t1_zscore2_cdf
                if resultValue == resultValue:
                    tempList.append(resultValue)
            t1 += interval
#            if len(tempList) > 0:
#                temp_sum = 0
#                for j in range(len(tempList)):
#                    temp_sum += tempList[j]
#                if temp_sum == 0:
#                    print(tempList)
#                print(temp_sum)
        resultList.append(tempList)
#        if i == 30 or i == 50:
#            temporarySum = 0
#            print(tempList)
#            for i in tempList:
#                temporarySum += i
#            print(temporarySum)
#            print('First: ' + str(first_probability))
#            print('Last: ' + str(last_probability))
#            print('Last - first: ' + str(last_probability - first_probability))
#            print('Denominator: ' + str(asdf))
    return resultList       #2D: 1st dim is exit station, 2nd dim is probability to go there for a certain time series 

def findTimeDistributionDiscrete(startingStation, stime, currTime, day_type, interval, threshold):    #calculates the probability of G exiting in time t1 given G didn't exit before t2
#    pickle_startStation_in = open(startingStation + 'AprilTuesdays' + 'ResultList5.pickle', 'rb')
#    startStationList = pickle.load(pickle_startStation_in)
#    startStationProbList = startStationList[stime]
    startStationProbList = entireSetup[stationList.index(startingStation)][stime]
    resultList = []
    for i in range(len(startStationProbList)):
#        thresholdCheck = 1
        t1 = currTime 
        tempList = []
        dstr = startStationProbList[i][2]                   #t2 is current time
        mean = startStationProbList[i][1]
        if mean == 0:
            tempList = [0]
        else:
            tempList = findIntervalProbDstr(t1, interval, dstr)
#        while thresholdCheck > threshold and len(tempList) < 60:
#            resultValue = 0
#            if mean == 0:
#                tempList.append(resultValue)
#                thresholdCheck = 0
#            else:
#                resultValue = findIntervalProb(t1, interval, dstr)
#                thresholdCheck = checkDiscreteThreshold(t1, interval, dstr, threshold)
#                if resultValue == resultValue:
#                    tempList.append(resultValue)
#            t1 += interval
        resultList.append(tempList)
    return resultList       #2D: 1st dim is exit station, 2nd dim is probability to go there for a certain time series 

#def checkDiscreteThreshold(t1, interval, dstrLst, threshold):
#    index = t1 // interval
#    if len(dstrLst) <= index:
#        return 0
#    tempSum = sum(dstrLst[index:])
#    if tempSum < threshold:
#        return 0
#    else:
#        return 1

def findTimeDistributionML(startingStation, stime, line, mlType):
    lineLst = []
    arr = line.split(',')
    for i in range(len(arr)):
        arr[i] = arr[i].replace('"', '')
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
    lineDayType = dayTypeLst[monthNum][lineDate - 1]
    lineStartStation = stationList.index(arr[1])
    lineStartTime = convertTime(arr[2])
    if lineStartTime > 0:
        lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
        lineStationCluster = stationClusterLst[lineStartStation]
#        lineEndStation = stationList.index(arr[3])
        lineLst.append(lineDayType)
        lineLst.append(lineStartStation)
        lineLst.append(lineStartTime)
        lineLst.extend(lineWeatherLst)
        lineLst.append(lineStationCluster)
#        lineLst.append(lineEndStation)
    if mlType == 'KNR':
        pickle_KNC_in = open('MarchAprWholeKNR5.pickle', 'rb')
        ml = pickle.load(pickle_KNC_in)
        pickle_KNC_in.close()
    elif mlType == 'MLR':
        pickle_MLP_in = open('MarchAprWholeMLPR5.pickle', 'rb')
        ml = pickle.load(pickle_MLP_in)
        pickle_MLP_in.close()
    elif mlType == 'GBR':
        pickle_GBC_in = open('MarchAprWholeGBR5.pickle', 'rb')
        ml = pickle.load(pickle_GBC_in)
        pickle_GBC_in.close()
    elif mlType == 'ABR':
        pickle_ABC_in = open('MarchAprWholeABR5.pickle', 'rb')
        ml = pickle.load(pickle_ABC_in)
        pickle_ABC_in.close()
    MLtimeDstr = []*91
    lineLst.append(0)
    for i in range(91):
        lineLst[-1] = i
        MLPredict = int(ml.predict(np.array(lineLst))[0])
        tempLst = [0.0]
        for j in range(MLPredict):
            tempLst.append(0.0)
        tempLst[-1] = 1.0
        MLtimeDstr.append(tempLst)
    return MLtimeDstr

def findIntervalProbDstr(t1, interval, dstrLst):
#    index = t1 // interval
#    if len(dstrLst) <= index:
#        return 0
#    probLst = dstrLst[index:]
#    if sum(probLst) == 0:
#        return 0
#    return probLst[0] / sum(probLst)
    index = t1 // interval
    if len(dstrLst) <= index:
        return [0]
    resultLst = dstrLst[index:]
    if sum(resultLst) == 0:
        return [0]
    normedResultLst = [i/sum(resultLst) for i in resultLst]
    return normedResultLst

def combinationDistribution(stationConditionedList, timeConditionedList):
    stationList = []          
    for i in range(len(stationConditionedList)):
        expectedOutput = timeConditionedList[i]
        for j in range(len(expectedOutput)):
            expectedOutput[j] = stationConditionedList[i] * expectedOutput[j]
        stationList.append(expectedOutput)
    return stationList      #2D: for a given starting time, 1st dim is exit station, 2nd dim is expected number of output people at a certain time

def expectedList(startStation, startTime, travelTimeSoFar, day_type, interval, threshold, sd, stationML, rawLine, mlType, discrete, timeML, mlTimeType, median, noTravelTime):
#    currRunningTime = time.time()
#    calcResult = calcBayes(startStation, startTime, travelTimeSoFar, day_type)
#    currRunningTime2 = time.time()
#    print('Station Bayesian took ' + str(currRunningTime2 - currRunningTime) + ' seconds.')
#    timeDistributionResult = findTimeDistribution(startStation, startTime, travelTimeSoFar, day_type, interval, threshold)
#    currRunningTime = time.time()
#    print('Time Distribution took ' + str(currRunningTime - currRunningTime2) + ' seconds.')
#    expectedResult = combinationDistribution(calcResult, timeDistributionResult)
#    currRunningTime2 = time.time()
#    print('Combination of both took ' + str(currRunningTime2 - currRunningTime) + ' seconds.')
    if noTravelTime:
        travelTimeSoFar = 0
    else:
        travelTimeSoFar = travelTimeSoFar
    if stationML == True:
        calcResult = calcStationProbML(startStation, startTime, travelTimeSoFar, rawLine, mlType)
    elif discrete == True:
        calcResult = calcDiscreteBayes(startStation, startTime, travelTimeSoFar, day_type, interval)
#        print('StationProb: ' + str(sum(calcResult)))
    else:
        calcResult = calcBayes(startStation, startTime, travelTimeSoFar, day_type, interval, sd, median)
#    temp_sum = 0
#    for i in range(len(calcResult)):
#        temp_sum += calcResult[i]
#    print('Station Bayesian ' + str(len(calcResult)) + ': ' + str(temp_sum))  
#    print('Gradient Boosting: ' + str(calcResult)) 
    if discrete == True:
        timeDistributionResult = findTimeDistributionDiscrete(startStation, startTime, travelTimeSoFar, day_type, interval, threshold)   
#        print('Time Distribution')
#        print(sum(timeDistributionResult[0]))
    elif timeML == True:
#        print(findTimeDistributionML(startStation, startTime, rawLine, mlTimeType))
        timeDistributionResult = findTimeDistributionML(startStation, startTime, rawLine, mlTimeType)
    else:    
        timeDistributionResult = findTimeDistribution(startStation, startTime, travelTimeSoFar, day_type, interval, threshold, sd, median)
#    print('Bayesian Time Distribution: ' + str(timeDistributionResult))
#    print('Time Distribution ' + str(len(timeDistributionResult)) + ':')
#    for i in range(len(timeDistributionResult)):
#        temp_sum = 0
#        if len(timeDistributionResult[i]) > 2:
#            for j in range(len(timeDistributionResult[i])):
#                temp_sum += timeDistributionResult[i][j]
#            if temp_sum < 0.59:
#                print(i)
#            print(temp_sum)
    expectedResult = combinationDistribution(calcResult, timeDistributionResult)
#    tempSum = 0
#    for i in range(len(expectedResult)):
#        for j in expectedResult[i]:
#            tempSum += j
#    print(tempSum)
    return expectedResult   #2D: for a given starting time, 1st dim is exit station, 2nd dim is expected number of output people at a certain time

def groundTruth(endTime, day, interval, rawData):
    countOutput = [0] * 92
    countOutput2 = [0]*92
    countOutput3 = [0]*92
    countOutput4 = [0]*92
    timeFMT = '%I:%M:%S%p'
    timeIncrement = td(minutes = interval)
    lowerBound = dt.strptime(endTime, timeFMT)
    lowerBound2 = lowerBound + timeIncrement
    lowerBound3 = lowerBound2 + timeIncrement
    lowerBound4 = lowerBound3 + timeIncrement
    upperBound = lowerBound4 + timeIncrement
    i = 0
    for line in rawData:
        if i % 1000000 == 0:
            print(i)
        arr = line.split(',')
        arr[0] = arr[0].replace('"', '')
        arr[4] = arr[4].replace('"', '')
        if arr[0] == day:
            arr[2] = arr[2].replace('\n', '')
            arr[4] = arr[4].replace('\n', '')
            travel_minutes = convertToMinutes(arr[4]) - convertToMinutes(arr[2])
            arr[4] = dt.strptime(arr[4], timeFMT)
            if arr[4] >= lowerBound and arr[4] <= lowerBound2 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput[exitStationIndex] += 1
            elif arr[4] >= lowerBound2 and arr[4] <= lowerBound3 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput2[exitStationIndex] += 1
            elif arr[4] >= lowerBound3 and arr[4] <= lowerBound4 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput3[exitStationIndex] += 1
            elif arr[4] >= lowerBound4 and arr[4] <= upperBound and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput4[exitStationIndex] += 1
        i += 1
    fourOutputs = []
    fourOutputs.append(countOutput)
    fourOutputs.append(countOutput2)
    fourOutputs.append(countOutput3)
    fourOutputs.append(countOutput4)
    return fourOutputs

def skyTruthList(startTime, day, interval, rawDataList):
    countOutput = np.zeros((15, 91))
    timeFMT = '%I:%M:%S%p'
    timeIncrement = td(minutes = interval)
    bound = np.zeros(16, dtype = type(timeIncrement))
    bound[0] = dt.strptime(startTime, timeFMT)
    for i in range(1, 16):
        bound[i] = bound[i - 1] + timeIncrement
    i = 0
    for line in rawDataList:
        if i % 1000 == 0:
            print(i)
        arr = line.split(',')
        arr[0] = arr[0].replace('"', '')
        arr[0] = arr[0].replace("'", '')
        if arr[0] == day and arr[1] != arr[3]:
            arr[4] = arr[4].replace('"', '')
            arr[4] = arr[4].replace("'", '')
            arr[4] = arr[4].replace("\n", '')
            arr[2] = arr[2].replace('"', '')
            arr[2] = arr[2].replace("'", '')
            arr[2] = arr[2].replace("\n", '')
            travel_minutes = convertToMinutes(arr[4]) - convertToMinutes(arr[2]) #length of trip in minutes
            arr[4] = dt.strptime(arr[4], timeFMT) #set exit time slot in array with exit time in date format
            if(travel_minutes < 240 and arr[1] != arr[3]):
                for index in range(15):
                    if(arr[4] >= bound[index] and arr[4] < bound[index + 1]):
                        countOutput[index, stationList.index(arr[3])] += 1
        i+=1
    return countOutput

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

def finalPrediction(currTime, day, interval, rawTrips, sd, stationML, mlType, discrete, timeML, mlTimeType, median, noTravelTime):
    totalOutflowPredicted = 0
    exitStationOutflow = []        #list of estimated outflow for each station
    for i in range(61):
        exitStationOutflow.append([0]*92)
    for i in range(len(rawTrips)):
#    for i in range(5):
#        print(rawTrips[i])
        if i % 100 == 0 and i != 0:
            print(i)
        arr = rawTrips[i].split(',')
        for j in range(len(arr)):
            arr[j] = arr[j].replace('"', '')
        startStation = arr[1]
        convertedStartTime = convertToInterval(arr[2], interval)
        travelTimeSoFar = convertToMinutes(currTime) - convertToMinutes(arr[2])
        dateFMT = '%d-%m-%Y'
        arr[0] = arr[0].replace('JAN', '01')
        arr[0] = arr[0].replace('FEB', '02')
        arr[0] = arr[0].replace('MAR', '03')
        arr[0] = arr[0].replace('APR', '04')
        arr[0] = arr[0].replace('MAY', '05')
        arr[0] = arr[0].replace('JUN', '06')
        day_type = dt.strptime(arr[0], dateFMT).weekday()
        if day_type < 5:
            day_type = 'wkday'
        else:
            day_type = 'weday'
        threshold = 0.00001                                  #MANUAL INPUT
        temp_list = expectedList(startStation, convertedStartTime, travelTimeSoFar, day_type, interval, threshold, sd, stationML, rawTrips[i], mlType, discrete, timeML, mlTimeType, median, noTravelTime)
#        convertedDiffToEnd = ((convertToMinutes(endTime) - convertToMinutes(currTime)) // interval) - 1
        for station in range(len(temp_list)):
            for nTime in temp_list[station]:
#                print(nTime)
                if nTime == nTime:      #to prevent NaN error
                    totalOutflowPredicted += nTime
            #print(temp_list[station])
            for k in range(len(temp_list[station])):
                if k >= len(exitStationOutflow):
                    print('k')
                    print(len(temp_list[station]))
                if station >= len(exitStationOutflow[k]):
                    print('station')
                exitStationOutflow[k][station] += temp_list[station][k]
#        if len(temp_list) < 2:
#            print(rawTrips[i])
#        if i % 1000 == 0:
#            print('Total outflow: ' + str(totalOutflowPredicted) + ' out of ' + str(i + 1)) 
#    print(exitStationOutflow[0])
#    print(exitStationOutflow[1])
    return exitStationOutflow

def convertToInterval(rawTime, interval):
    minutes = convertToMinutes(rawTime)
    stime = minutes // interval  #integer division
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

def totalTrueOutflow(startTime, day, interval, rawData):
    trueOutflow = np.zeros((15, 91))
    timeFMT = '%I:%M:%S%p'
    timeIncrement = td(minutes = interval)
    bound = np.zeros(16, dtype = type(timeIncrement))
    bound[0] = dt.strptime(startTime, timeFMT)
    for i in range(1, 16):
        bound[i] = bound[i - 1] + timeIncrement
    i = 0
    for line in rawData:
        if i % 800000 == 0:
            print(i)
        arr = line.split(',')
        arr[0] = arr[0].replace('"', '')
        arr[0] = arr[0].replace("'", '')
        if arr[0] == day and arr[1] != arr[3]:
            arr[4] = arr[4].replace('"', '')
            arr[4] = arr[4].replace("'", '')
            arr[4] = arr[4].replace("\n", '')
            arr[2] = arr[2].replace('"', '')
            arr[2] = arr[2].replace("'", '')
            arr[2] = arr[2].replace("\n", '')
            travel_minutes = convertToMinutes(arr[4]) - convertToMinutes(arr[2]) #length of trip in minutes
            arr[4] = dt.strptime(arr[4], timeFMT) #set exit time slot in array with exit time in date format
            if(travel_minutes < 240):
                for index in range(15):
                    if(arr[4] >= bound[index] and arr[4] < bound[index + 1]):
                        trueOutflow[index, stationList.index(arr[3])] += 1
        i+=1
    return trueOutflow
    
#%%
#==============================================================================
# monthData = open('APR.csv', "r")
# truth = groundTruth('07:10:00AM', '25-APR-2017', 5, monthData)
# for i in range(len(truth)):
#     tempSum = 0
#     for j in truth[i]:
#         tempSum += j
#     print(tempSum, end = '  ')
# #print('Ground Truth: ' + str(truth) + ' people came out of ' + exitStation + ' from 6:10 AM to 6:15 AM on June 13th, 2017')
# monthData.close()
#==============================================================================
#%%                                     
monthData = open('APR.csv', "r")
currentPassengersList = findCurrentPassengers('07:20:00AM', '25-APR-2017', 5, monthData)     #always has to be 5 minutes before the 2nd arg of finalPrediction                                       

truth2 = skyTruthList('07:20:00AM', '25-APR-2017', 5, currentPassengersList)
for i in range(len(truth2)):
    tempSum = 0
    for j in truth2[i]:
        tempSum += j
    print(tempSum)    
monthData.close()               
#%%
monthData = open('APR.csv', 'r')
totalOutflow = totalTrueOutflow('7:20:00AM', '25-APR-2017', 5, monthData)
monthData.close()
#%%
#pickle_in_eSetup = open('012SetupMAR24toAPR24.pickle', 'rb')
pickle_in_eSetup = open('012SetupNOMAR24toAPR24.pickle', 'rb')
#pickle_in_eSetup = open('012DiscreteSetupMAR24toAPR24.pickle', 'rb')
entireSetup = pickle.load(pickle_in_eSetup)
pickle_in_eSetup.close() 
#%%
warnings.filterwarnings("ignore")
#finalResult = finalPrediction('07:20:00AM', '25-APR-2017', 5, currentPassengersList, False, True, 'GBC', False, True, 'GBR')
finalResult = finalPrediction('07:20:00AM', '25-APR-2017', 5, currentPassengersList, False, False, 'GBC', False, False, 'GBR', False, False)  #endTime is one interval after the beginning of time to predict
for i in range(18):                                                                 #SD     ML  mlType  discrete timeML mlTimeType median noTravelTime
    tempSum = 0
    for j in range(len(finalResult[i])):
        if finalResult[i][j] == finalResult[i][j]:
            tempSum += finalResult[i][j]
    print(tempSum)    
#print(finalResult)
#print('Forecast: We predict that there will be ' + str(finalResult) + ' people coming out of ' + exitStation + ' from 6:10 AM to 6:15 AM on June 13th, 2017')

#6:05 predicting 6:10 finalResult = 39.937365494976341, groundTruth = 62
#7am predicting 7:10 am and onwards
#%%
pickle_out = open('BM+ONoSD.pickle', 'wb')
pickle.dump(finalResult, pickle_out)
pickle_out.close()
    
#%%
def sumClusters(fResult, sClustersLst):
    sumLst = []
    for i in range(15):
        sumLst.append([0] * 8)     #1st dim is tInterval, 2nd dim is cluster 
    for i in range(len(sumLst)):
        for station in range(91):
            sumLst[i][sClustersLst[station]] += fResult[i][station]
    return sumLst


#==============================================================================
# clusterLst = sumClusters(finalResult, stationClusterLst)    
#==============================================================================
#for i in range(len(clusterLst)):
#    print(clusterLst[i][2])
#    
#==============================================================================
# groundTruthClusterLst = sumClusters(truth2, stationClusterLst)
#==============================================================================
#for i in range(len(groundTruthClusterLst)):
#    print(groundTruthClusterLst[i][1])    
    

def findStationMSEList(fResult, truthLst):
    mseLst = []
    for i in range(15):
        predicted = fResult[i][:91]
        true = truthLst[i][:91]
        mse = mean_squared_error(true, predicted)
        mseLst.append(mse)
    return mseLst

def findTotalStationMSE(fResult, truthLst):
    predicted = []
    true = []
    for i in range(15):
        fLen = len(fResult[i])
        tLen = len(truthLst[i])
        if tLen < fLen:
            fLen = tLen 
        predicted.extend(fResult[i][:fLen])
        true.extend(truthLst[i][:fLen])
    return mean_squared_error(true, predicted)

def findLowestStationMSE(fResult, truthLst):
    mseLst = []
    truthLst = truthLst[:15]
    fResult = fResult[:15]
    fResultFlipped = [list(t) for t in zip(*fResult)]
    truFlipped = [list(t) for t in zip(*truthLst)]
    for i in range(91):
        mse = mean_squared_error(truFlipped[i], fResultFlipped[i])
        mseLst.append(mse)
        
    return mseLst
#%%
stationMSE = findLowestStationMSE(finalResult, truth2)
totalSME = findTotalStationMSE(finalResult, truth2)
print(totalSME)
SMELst = findStationMSEList(finalResult, truth2)


#%%
for i in range(15):
    print(groundTruthClusterLst[i][1])

for i in range(15):
    print(finalResult[i][28])
    

#%%
#Baseline approaches: 1)Historic Trends -- Previous day 2) Previous Week 3) ARIMA
def baselinePrevDay(time, day): #args are strings, outputs 2d array of previous day outflow, 1st dim is time, 2nd dim is exit station 
    #we just call totalTrueOutflow
    rawData = open('APR.csv', 'r')
    currentPassengersList = findCurrentPassengers(time, day, 5, rawData)
    totalOutflow = skyTruthList(time, day, 5, currentPassengersList)
    rawData.close()
    return totalOutflow
#%%
'''
Find MSE of baselines
'''
prevDayBase = baselinePrevDay('07:20:00AM', '24-APR-2017')
#%%
for i in range(len(prevDayBase)):
    tempSum = 0 
    for j in prevDayBase[i]:
        tempSum += j
    print(tempSum)
totalMSE = findTotalStationMSE(prevDayBase, truth2)
print(totalMSE)
#%%
'''
New Passenger Predictions
'''
def histNewPassengers(probLst, numDays):
    newPassengerLst = []
    for i in range(len(probLst[0])):
        newPassengerLst.append([0]*len(probLst))
    for i in range(len(newPassengerLst)):
        for station in range(len(probLst)):     
            if len(probLst[station]) > i:    #for some reason, some enter stations have a length of less than 287 in entireSetup
                newPassengerLst[i][station] += (sumPassengers(probLst[station][i]) / numDays)
    return newPassengerLst      #1st dim is time (5 minute interval), 2nd dim is enterStation

def sumPassengers(startStationProbLst):
    num = 0
    for i in range(len(startStationProbLst)):
        num += startStationProbLst[i][-1]
    return num

def generateFuturePassengers(histPassengers, startIndex, endIndex, day, interval):
    ghosts = []
    for i in range(startIndex, endIndex):
        ghosts.append([0]*len(histPassengers[0]))
    for timeInterval in range(startIndex, endIndex):
        print(timeInterval)
        for station in range(len(histPassengers[timeInterval])):
            if histPassengers[timeInterval][station] != 0:
                startStation = stationList[station]
                startTime = generateTime(timeInterval, interval)
                endStation = stationList[0]
                endTime = generateTime(timeInterval + 2, interval)      #be careful of timeInterval + 2
                generateRawTrip = [day + ',' + startStation + ',' + startTime + ','+ endStation+ ',' + endTime]
                rst = finalPrediction(startTime, day, interval, generateRawTrip, True, False, 'GBC', False, False, 'GBR', False, False)
                rst = rst[:endIndex - startIndex]
                if startIndex != timeInterval:
                    rst = rst[:startIndex - timeInterval]
                
                num = timeInterval - startIndex
#                print("a")
#                print(len(rst))
#                print("b")
#                print(len(ghosts))
                for i in range(len(rst)):
                    for j in range(91):
                        ghosts[i + num][j] += rst[i][j] * histPassengers[timeInterval][station]
    return ghosts   #1st dim is time interval, 2nd dim is exit station        

def generateTime(timeIndex, interval):
    minutes = timeIndex * interval
    hours = minutes // 60
    minutes = minutes % 60
    rawTime = ''
    if hours == 0:
        rawTime = '12:' + "%02d" % (minutes,) + ':00AM'
    elif hours < 12:
        rawTime = '%02d' % (hours,) + ':' + "%02d" % (minutes,) + ':00AM'
    elif hours == 12:
        rawTime = '12:' + "%02d" % (minutes,) + ':00PM'
    else:
        rawTime = '%02d' % (hours - 12,) + ':' + '%02d' % (minutes,) + ':00PM'
    return rawTime
#%%
#entireSetup: 1st dim is startStation, 2nd dim is time (5 minute interval), 3rd dim is exit station, 4th dim is probability stuff
#finalResult: 1st dim is time, 2nd dim is exit station
numGhosts = histNewPassengers(entireSetup, 13)
ghosts = generateFuturePassengers(numGhosts, 88, 103, '25-APR-2017', 5)

#%%
pickle_out = open('BM+O+ghosts.pickle', 'wb')
pickle.dump(ghosts, pickle_out)
pickle_out.close()
#%%
'''
Historical Average Traffic for Each Station 
'''
pickle_out = open('HistoricAverageTraffic.pickle', 'wb')
pickle.dump(numGhosts, pickle_out)
pickle_out.close()

#%%
'''
Find number of trips in a month
'''
def findNumTrips(monthData):
    count = 0
    i = 0
    for line in monthData:
        if i % 1000000 == 0:
            print(i)
        i += 10
        arr = line.split(',')
        if ('25' in arr[0]) or ('26' in arr[0]) or ('27' in arr[0]) or ('28' in arr[0]) or ('29' in arr[0]) or ('30' in arr[0]):
            count += 0
        else:
            count += 1
    return count
#%%
monthData = open('APR.csv', 'r')
numTrips = findNumTrips(monthData)
print(numTrips)
monthData.close()

    
    
    
    
    