# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:00:15 2017

@author: Eric Lin
Compares Output Estimation accuracy
"""

import os
import pickle
import scipy.stats as st
from datetime import datetime as dt 
from datetime import timedelta as td
import time

os.chdir('C:/Users/GGSAdminLab/Documents/Eric Lin/Metro Data Project/ActualCodeBayesianPt3')



def calcStationBayesSD(startingStation, stime, travel_time, day_type):     #time is an int from 0 to length of startStationList day_type is either wkDay or weDay   
    
    pickle_startStation_in = open(startingStation + day_type + 'ResultList5.pickle', 'rb')
    startStationList = pickle.load(pickle_startStation_in)
    bayesNumList = []       #each index is for a station
    priorProbList = startStationList[stime]          #2D
    denominator = 0
    for i in range(len(priorProbList)):
        num1 = findTravelProb(priorProbList, i, travel_time)
        numerator = num1 * priorProbList[i][0]
        bayesNumList.append(numerator)  
        denominator += numerator
    if denominator == 0:
        bayesNumList = [0]
        return bayesNumList
    for i in range(len(bayesNumList)):
        bayesNumList[i] = bayesNumList[i] / denominator
    return bayesNumList         #1D: probability of G exiting at A

def calcStationBayesGNB(startingStation, stime, travel_time, day_type):     #time is an int from 0 to length of startStationList day_type is either wkDay or weDay   
    
    pickle_startStation_in = open(startingStation + day_type + 'ResultList5.pickle', 'rb')
    startStationList = pickle.load(pickle_startStation_in)
    bayesNumList = []       #each index is for a station
    priorProbList = startStationList[stime]          #2D
    denominator = 0
    for i in range(len(priorProbList)):
        num1 = findTravelProb(priorProbList, i, travel_time)
        numerator = num1 * priorProbList[i][0]
        bayesNumList.append(numerator)  
        denominator += numerator
    if denominator == 0:
        bayesNumList = [0]
        return bayesNumList
    for i in range(len(bayesNumList)):
        bayesNumList[i] = bayesNumList[i] / denominator
    return bayesNumList         #1D: probability of G exiting at A

def findTravelProb(startStationProbList, endStationNum, travel_time):       #uses SD
    stdDeviation = startStationProbList[endStationNum][2]    
    mean = startStationProbList[endStationNum][1]
    if mean == 0:
        return 0
    z_score = 0
    resultProb = 1
    if travel_time < mean:
        z_score = 1
        resultProb = 1
    else:
        z_score = (travel_time - mean) / stdDeviation
        resultProb = 1 - st.norm.cdf(z_score)
    return resultProb

def findTimeDistribution(startingStation, stime, currTime, day_type, interval, threshold):    #calculates the probability of G exiting in time t1 given G didn't exit before t2
    pickle_startStation_in = open(startingStation + 'AprilTuesdays' + 'ResultList5.pickle', 'rb')
    startStationList = pickle.load(pickle_startStation_in)
    startStationProbList = startStationList[stime]
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
              
        while thresholdCheck > threshold and len(tempList) < 60:
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
                resultValue = 0
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
#                    asdf = denom
                else: 
                    if mean - t1 < interval:
                        resultValue = 1
                if resultValue == 0:
                    print('0: ' + str(t1) + ' ' + str(thresholdCheck))
#                if len(tempList) == 0:
#                    first_probability = t1_zscore_cdf
#                last_probability = t1_zscore2_cdf
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

def combinationDistribution(stationConditionedList, timeConditionedList):
    stationList = []          
    for i in range(len(stationConditionedList)):
        expectedOutput = timeConditionedList[i]
        for j in range(len(expectedOutput)):
            expectedOutput[j] = stationConditionedList[i] * expectedOutput[j]
        stationList.append(expectedOutput)
    return stationList      #2D: for a given starting time, 1st dim is exit station, 2nd dim is expected number of output people at a certain time

def expectedList(startStation, startTime, travelTimeSoFar, day_type, interval, threshold):
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
    
    calcResult = calcStationBayesSD(startStation, startTime, travelTimeSoFar, day_type)
#    temp_sum = 0
#    for i in range(len(calcResult)):
#        temp_sum += calcResult[i]
#    print('Station Bayesian ' + str(len(calcResult)) + ': ' + str(temp_sum))    
    timeDistributionResult = findTimeDistribution(startStation, startTime, travelTimeSoFar, day_type, interval, threshold)
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
    return expectedResult   #2D: for a given starting time, 1st dim is exit station, 2nd dim is expected number of output people at a certain time

def groundTruth(endTime, day, interval, rawData):
    pickle_stations = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_stations)
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

def groundTruthList(endTime, day, interval, rawDataList):
    pickle_stations = open('StationList.pickle', 'rb')
    stationList = pickle.load(pickle_stations)
    countOutput = [0] * 92
    countOutput2 = [0]*92
    countOutput3 = [0]*92
    countOutput4 = [0]*92
    countOutput5 = [0]*92
    countOutput6 = [0]*92
    countOutput7 = [0]*92
    countOutput8 = [0]*92
    countOutput9 = [0]*92
    countOutput10 = [0]*92
    countOutput11 = [0]*92
    countOutput12 = [0]*92
    countOutput13 = [0]*92
    countOutput14 = [0]*92
    countOutput15 = [0]*92
    timeFMT = '%I:%M:%S%p'
    timeIncrement = td(minutes = interval)
    lowerBound = dt.strptime(endTime, timeFMT)
    lowerBound2 = lowerBound + timeIncrement
    lowerBound3 = lowerBound2 + timeIncrement
    lowerBound4 = lowerBound3 + timeIncrement
    lowerBound5 = lowerBound4 + timeIncrement
    lowerBound6 = lowerBound5 + timeIncrement
    lowerBound7 = lowerBound6 + timeIncrement
    lowerBound8 = lowerBound7 + timeIncrement
    lowerBound9 = lowerBound8 + timeIncrement
    lowerBound10 = lowerBound9 + timeIncrement
    lowerBound11 = lowerBound10 + timeIncrement
    lowerBound12 = lowerBound11 + timeIncrement
    lowerBound13 = lowerBound12 + timeIncrement
    lowerBound14 = lowerBound13 + timeIncrement
    lowerBound15 = lowerBound14 + timeIncrement
    upperBound = lowerBound14 + timeIncrement
    i = 0
    for line in rawDataList:
        if i % 1000 == 0:
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
            elif arr[4] >= lowerBound4 and arr[4] <= lowerBound5 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput4[exitStationIndex] += 1
            elif arr[4] >= lowerBound5 and arr[4] <= lowerBound6 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput5[exitStationIndex] += 1
            elif arr[4] >= lowerBound6 and arr[4] <= lowerBound7 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput6[exitStationIndex] += 1
            elif arr[4] >= lowerBound7 and arr[4] <= lowerBound8 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput7[exitStationIndex] += 1
            elif arr[4] >= lowerBound8 and arr[4] <= lowerBound9 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput8[exitStationIndex] += 1
            elif arr[4] >= lowerBound9 and arr[4] <= lowerBound10 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput9[exitStationIndex] += 1
            elif arr[4] >= lowerBound10 and arr[4] <= lowerBound11 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput10[exitStationIndex] += 1
            elif arr[4] >= lowerBound11 and arr[4] <= lowerBound12 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput11[exitStationIndex] += 1
            elif arr[4] >= lowerBound12 and arr[4] <= lowerBound13 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput12[exitStationIndex] += 1
            elif arr[4] >= lowerBound13 and arr[4] <= lowerBound14 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput13[exitStationIndex] += 1
            elif arr[4] >= lowerBound14 and arr[4] <= lowerBound15 and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput14[exitStationIndex] += 1
            elif arr[4] >= lowerBound15 and arr[4] <= upperBound and travel_minutes < 240 and arr[1] != arr[3]:
                exitStationIndex = stationList.index(arr[1])
                countOutput15[exitStationIndex] += 1
            
        i += 1
    fourOutputs = [countOutput, countOutput2, countOutput3, countOutput4, countOutput5, countOutput6, countOutput7, countOutput8, countOutput9, countOutput10, countOutput11, countOutput12, countOutput13, countOutput14, countOutput15]
    return fourOutputs

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

def finalPrediction(currTime, endTime, day, interval, rawTrips):
    totalOutflowPredicted = 0
    exitStationOutflow = []        #list of estimated outflow for each station
    for i in range(61):
        exitStationOutflow.append([0]*92)
    for i in range(len(rawTrips)):
#    for i in range(3):
#        print(rawTrips[i])
        if i % 100 == 0:
            print(i)
        arr = rawTrips[i].split(',')
        for j in range(len(arr)):
            arr[j] = arr[j].replace('"', '')
        startStation = arr[1]
        convertedStartTime = convertToInterval(arr[2], interval)
        travelTimeSoFar = convertToMinutes(currTime) - convertToMinutes(arr[2])
        dateFMT = '%d-%m-%Y'
        arr[0] = arr[0].replace('APR', '04')
        day_type = dt.strptime(arr[0], dateFMT).weekday()
        if day_type < 5:
            day_type = 'wkday'
        else:
            day_type = 'weday'
        threshold = 0.00001                                  #MANUAL INPUT
        temp_list = expectedList(startStation, convertedStartTime, travelTimeSoFar, day_type, interval, threshold)
#        convertedDiffToEnd = ((convertToMinutes(endTime) - convertToMinutes(currTime)) // interval) - 1
        for station in range(len(temp_list)):
            for nTime in temp_list[station]:
#                print(nTime)
                if nTime == nTime:
                    totalOutflowPredicted += nTime
            #print(temp_list[station])
            for k in range(len(temp_list[station])):
                if k >= len(exitStationOutflow):
                    print('k')
                    print(len(temp_list[station]))
                if station >= len(exitStationOutflow[k]):
                    print('station')
                exitStationOutflow[k][station] += temp_list[station][k]
        if len(temp_list) < 2:
            print(rawTrips[i])
        if i % 1000 == 0:
            print('Total outflow: ' + str(totalOutflowPredicted) + ' out of ' + str(i)) 
    print(exitStationOutflow[0])
    print(exitStationOutflow[1])
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
#%%
juneData = open('april.csv', "r")
truth = groundTruth('07:10:00AM', '25-APR-2017', 5, juneData)
for i in range(len(truth)):
    tempSum = 0
    for j in truth[i]:
        tempSum += j
    print(tempSum, end = '  ')
#print('Ground Truth: ' + str(truth) + ' people came out of ' + exitStation + ' from 6:10 AM to 6:15 AM on June 13th, 2017')
juneData.close()
#%%                                     
monthData = open('april.csv', "r")
currentPassengersList = findCurrentPassengers('06:20:00AM', '25-APR-2017', 5, monthData)     #always has to be 5 minutes before the 2nd arg of finalPrediction                                       

truth2 = groundTruthList('06:30:00AM', '25-APR-2017', 5, currentPassengersList)
for i in range(len(truth2)):
    tempSum = 0
    for j in truth2[i]:
        tempSum += j
    print(tempSum, end = '  ')    
monthData.close()                   
#%%
finalResult = finalPrediction('06:20:00AM', '06:35:00AM', '25-APR-2017', 5, currentPassengersList)  #endTime is one interval after the beginning of time to predict
for i in range(len(finalResult)):
    tempSum = 0
    for j in range(len(finalResult[i])):
        tempSum += finalResult[i][j]
    print(tempSum, end = '  ')

#print(finalResult)
#print('Forecast: We predict that there will be ' + str(finalResult) + ' people coming out of ' + exitStation + ' from 6:10 AM to 6:15 AM on June 13th, 2017')

             
#6:05 predicting 6:10 finalResult = 39.937365494976341, groundTruth = 62
#7am predicting 7:10 am and onwards