"""
Created on Mon Jul 31 08:54:16 2017

@author: Eric Lin
Naive Bayes for station probability distribution.
"""
import os
import pickle

from datetime import datetime
from sklearn.ensemble import AdaBoostRegressor, BaggingRegressor, ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import normalize
import numpy as np

#os.chdir('C:/Users/Eric.GoldenRatio/Documents/ASSIP Code/Metro Data Project/FinalCode')
os.chdir('/home/tjhsst/Documents/Eric/ASSIP/FinalCode')


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
Days
'''
dayTypeLst = [[0]*31, [0]*28, [0]*31, [0]*30, [0]*31, [0]*30]
for month in range(len(dayTypeLst)):
    for day in range(len(dayTypeLst[month])):
        tempDateTime = datetime(2017, month + 1, day + 1)
        if tempDateTime.weekday() >= 5:      #if weekend
            dayTypeLst[month][day] = 1
dayTypeLst[0][0] = 3    #New Year's
dayTypeLst[0][1] = 3    #New Year's
dayTypeLst[0][15] = 3   #MLK
dayTypeLst[0][19] = 3   #Inauguration
dayTypeLst[0][20] = 3   #Women's March
dayTypeLst[1][19] = 3   #George Washington's Birthday
dayTypeLst[4][28] = 3   #Memorial Day


'''
Station Clusters
'''
stationClusterString = '0 0 4 5 7 0 3 1 1 7 0 2 1 7 7 7 7 0 7 3 0 1 3 1 7 1 4 4 2 4 4 1 0 1 7 3 7 1 1 3 1 1 2 3 2 1 1 7 4 4 4 0 1 3 4 0 1 3 3 7 0 0 0 0 3 3 1 7 7 2 0 3 6 0 1 3 7 3 7 3 1 7 1 7 3 1 0 0 7 1 7'
stationClusterLst = stationClusterString.split(' ')
for i in range(len(stationClusterLst)):
    stationClusterLst[i] = int(stationClusterLst[i])
    
'''
Entire Setup
'''
pickle_in_eSetup = open('012SetupNOMAR24toAPR24.pickle', 'rb')
#pickle_in_eSetup = open('012DiscreteSetupMAR24toAPR24.pickle', 'rb')
entireSetup = pickle.load(pickle_in_eSetup)
pickle_in_eSetup.close()

'''
Station List
'''
pickle_stations_in = open('StationList.pickle', 'rb')
stationList = pickle.load(pickle_stations_in)
pickle_stations_in.close()
#%%
'''
Historical Baseline*
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
Generating Training Set*
'''
def convertTime(rawTime):
    rawTime = rawTime.replace('\n', '')
    timeFMT = '%I:%M:%S%p'
    groundTime = '04:00:00AM'
    timeDiff = datetime.strptime(rawTime, timeFMT) - datetime.strptime(groundTime, timeFMT)
    timeDiff = timeDiff.total_seconds()
    timeDiff = timeDiff // 60       #minutes since 4am
    return timeDiff
#%%
'''
Naive1:
1. DayType
2. StartStation 
3. StartTime
4. Historical Average Commute Time
5. StationCluster
6. EndStation
'''
janData = open('JAN.csv', 'r')
febData = open('FEB.csv', 'r')
marData = open('MAR.csv', 'r')

mayData = open('MAY.csv', 'r')
#junData = open('JUN.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
trainingLst = []


#monthNum = 0        #for January
#count = 0
#for line in janData:
#    if count % 300000 == 0:
#        print(count)
#        print(len(trainingLst))
#    if 'ENTRY' not in line:
##        print(line)
#        lineLst = []
#        arr = line.split(',')
#        for i in range(len(arr)):
#            arr[i] = arr[i].replace('"', '')
#        lineDate = int(arr[0][0:2])
#        lineDayType = dayTypeLst[monthNum][lineDate - 1]
#        lineStartStation = stationLst.index(arr[1])
#        lineStartTime = convertTime(arr[2])
#        travelTime = convertTime(arr[4]) - lineStartTime
#        if lineStartTime > 0:
#            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
#            lineStationCluster = stationClusterLst[lineStartStation]
#            lineEndStation = stationLst.index(arr[3])
#            lineLst.append(lineDayType)
#            lineLst.append(lineStartStation)
#            lineLst.append(lineStartTime)
#            lineLst.extend(lineWeatherLst)
#            lineLst.append(lineStationCluster)
#            lineLst.append(lineEndStation)
#            lineLst.append(travelTime)
#            trainingLst.append(lineLst)
#    count += 1
#pickle_training_out = open('JanuaryWholeTrainingTime.pickle', 'wb')
#pickle.dump(trainingLst, pickle_training_out)
#pickle_training_out.close()
#    
#trainingLst = []
#monthNum = 1        #for february
#count = 0
#for line in febData:
#    if count % 300000 == 0:
#        print(count)
#        print(len(trainingLst))
#    if 'ENTRY' not in line:
##        print(line)
#        lineLst = []
#        arr = line.split(',')
#        for i in range(len(arr)):
#            arr[i] = arr[i].replace('"', '')
#        lineDate = int(arr[0][0:2])
#        lineDayType = dayTypeLst[monthNum][lineDate - 1]
#        lineStartStation = stationLst.index(arr[1])
#        lineStartTime = convertTime(arr[2])
#        travelTime = convertTime(arr[4]) - lineStartTime
#        if lineStartTime > 0:
#            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
#            lineStationCluster = stationClusterLst[lineStartStation]
#            lineEndStation = stationLst.index(arr[3])
#            lineLst.append(lineDayType)
#            lineLst.append(lineStartStation)
#            lineLst.append(lineStartTime)
#            lineLst.extend(lineWeatherLst)
#            lineLst.append(lineStationCluster)
#            lineLst.append(lineEndStation)
#            lineLst.append(travelTime)
#            trainingLst.append(lineLst)
#    count += 1
#pickle_training_out = open('FebruaryWholeTrainingTime.pickle', 'wb')
#pickle.dump(trainingLst, pickle_training_out)
#pickle_training_out.close()

trainingLst = []
monthNum = 2
count = 0
for line in marData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line:
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1    
pickle_training_out = open('MarchWholeTrainingTimeNaive1.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()
#%%
aprData = open('APR.csv', 'r')
trainingLst = []
monthNum = 3        #for april
count = 0
for line in aprData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line and '25-APR' not in line and '26-APR' not in line and '27-APR' not in line and '28-APR' not in line and '29-APR' not in line and '30-APR' not in line:
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('April1-24TrainingTimeNaive1.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()
#
#trainingLst = []    
#monthNum = 4        #for may
#count = 0
#for line in mayData:
#    if count % 300000 == 0:
#        print(count)
#        print(len(trainingLst))
#    if 'ENTRY' not in line:
##        print(line)
#        lineLst = []
#        arr = line.split(',')
#        for i in range(len(arr)):
#            arr[i] = arr[i].replace('"', '')
#        lineDate = int(arr[0][0:2])
#        lineDayType = dayTypeLst[monthNum][lineDate - 1]
#        lineStartStation = stationLst.index(arr[1])
#        lineStartTime = convertTime(arr[2])
#        travelTime = convertTime(arr[4]) - lineStartTime
#        if lineStartTime > 0:
#            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
#            lineStationCluster = stationClusterLst[lineStartStation]
#            lineEndStation = stationLst.index(arr[3])
#            lineLst.append(lineDayType)
#            lineLst.append(lineStartStation)
#            lineLst.append(lineStartTime)
#            lineLst.extend(lineWeatherLst)
#            lineLst.append(lineStationCluster)
#            lineLst.append(lineEndStation)
#            lineLst.append(travelTime)
#            trainingLst.append(lineLst)
#    count += 1
#pickle_training_out = open('MayWholeTrainingTime.pickle', 'wb')
#pickle.dump(trainingLst, pickle_training_out)
#pickle_training_out.close()

janData.close()
febData.close()
marData.close()
aprData.close()
mayData.close()
#junData.close()

#pickle_training_out = open('JanuaryWholeTraining.pickle', 'wb')
#pickle.dump(trainingLst, pickle_training_out)
#pickle_training_out.close()
#pickle_training_out = open('JanuaryFebruaryWholeTraining.pickle', 'wb')
#pickle.dump(trainingLst2, pickle_training_out)
#pickle_training_out.close()
#pickle_training_out = open('JanuaryFebruaryMarchWholeTraining.pickle', 'wb')
#pickle.dump(trainingLst3, pickle_training_out)
#pickle_training_out.close()
#pickle_training_out = open('MarchAprilWholeTraining.pickle', 'wb')
#pickle.dump(trainingLst4, pickle_training_out)
#pickle_training_out.close()


#%%
'''
Naive2:
7. WeatherLst
'''
febData = open('FEB.csv', 'r')
marData = open('MAR.csv', 'r')

#junData = open('JUN.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
trainingLst = []

trainingLst = []
monthNum = 2
count = 0
for line in marData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line:
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineHistoricalTime = historicalBaseline(line)
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)            
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(lineHistoricalTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1    
marData.close()
pickle_training_out = open('MarchWholeTrainingTimeNaive2.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()

#%%
aprData = open('APR.csv', 'r')
trainingLst = []
monthNum = 3        #for april
count = 0
for line in aprData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line and '25-APR' not in line and '26-APR' not in line and '27-APR' not in line and '28-APR' not in line and '29-APR' not in line and '30-APR' not in line:#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineHistoricalTime = historicalBaseline(line)
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)            
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(lineHistoricalTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('April1-24TrainingTimeNaive2.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()
aprData.close()
#%%
'''
Bayes:*
8. Historical Traffic Outflow Average
9. Bayes + Future Passenger Outflow Prediction 
'''
pickle_in = open('BM+O.pickle', 'rb')
historicTrafficOutflow = pickle.load(pickle_in)
pickle_in.close()

pickle_in = open('BM+O+ghosts.pickle', 'rb')
bayesTrafficOutflow = pickle.load(pickle_in)
pickle_in.close()
#%%
febData = open('FEB.csv', 'r')
marData = open('MAR.csv', 'r')

#junData = open('JUN.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
trainingLst = []

trainingLst = []
monthNum = 2
count = 0
for line in marData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line:
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineHistoricalTime = historicalBaseline(line)
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            
            numIndex = (int) (lineHistoricalTime / 5)
            if numIndex > 14:
                numIndex = 14
            lineHistoricOutflow = historicTrafficOutflow[numIndex][lineEndStation]
            lineBayesOutflow = bayesTrafficOutflow[numIndex][lineEndStation]
            
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)            
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(lineHistoricalTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(lineHistoricOutflow)
            lineLst.append(lineBayesOutflow)
            
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1    
marData.close()
pickle_training_out = open('MarchWholeTrainingTimeBayes.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()

#%%
aprData = open('APR.csv', 'r')
trainingLst = []
monthNum = 3        #for april
count = 0
for line in aprData:
    if count % 300000 == 0:
        print(count)
        print(len(trainingLst))
    if 'ENTRY' not in line and '25-APR' not in line and '26-APR' not in line and '27-APR' not in line and '28-APR' not in line and '29-APR' not in line and '30-APR' not in line:#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationList.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineHistoricalTime = historicalBaseline(line)
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationList.index(arr[3])
            
            numIndex = (int) (lineHistoricalTime / 5)
            if numIndex > 14:
                numIndex = 14
            lineHistoricOutflow = historicTrafficOutflow[numIndex][lineEndStation]
            lineBayesOutflow = bayesTrafficOutflow[numIndex][lineEndStation]
            
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)            
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(lineHistoricalTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(lineHistoricOutflow)
            lineLst.append(lineBayesOutflow)
            
            lineLst.append(travelTime)
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('April1-24TrainingTimeBayes4.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()
aprData.close()

#%%
'''
Input Data Formatting*
'''
def findCurrentPassengers(currTime, day, interval, rawData):
    currPassengers = []
    timeFMT = '%I:%M:%S%p'
    lowerBound = datetime.strptime(currTime, timeFMT)
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
            arr[2] = datetime.strptime(arr[2], timeFMT)
            arr[4] = datetime.strptime(arr[4], timeFMT)
            if arr[2] < upperBound and arr[4] > upperBound and travel_minutes < 240 and arr[1] != arr[3]:
                currPassengers.append(line)
        i += 1
    return currPassengers
#%%
'''
Current passengers on April 25*
'''
monthData = open('APR.csv', "r")
currentPassengersList = findCurrentPassengers('07:20:00AM', '25-APR-2017', 5, monthData)     #always has to be 5 minutes before the 2nd arg of finalPrediction                                       

#%%
'''
NEW Generating Testing Set*!
'''
testLst = []
monthNum = 3        #for april
count = 0
for line in currentPassengersList:
    if count % 3000 == 0:
        print(count)
        print(len(testLst))
#        print(line)
    lineLst = []
    arr = line.split(',')
    for i in range(len(arr)):
        arr[i] = arr[i].replace('"', '')
    lineDate = int(arr[0][0:2])
    lineDayType = dayTypeLst[monthNum][lineDate - 1]
    lineStartStation = stationList.index(arr[1])
    lineStartTime = convertTime(arr[2])
    travelTime = convertTime(arr[4]) - lineStartTime
    if lineStartTime > 0:
        lineHistoricalTime = historicalBaseline(line)
        lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
        lineStationCluster = stationClusterLst[lineStartStation]
        lineEndStation = stationList.index(arr[3])
        
        numIndex = (int) (lineHistoricalTime / 5)
        if numIndex > 14:
            numIndex = 14
        lineHistoricOutflow = historicTrafficOutflow[numIndex][lineEndStation]
        lineBayesOutflow = bayesTrafficOutflow[numIndex][lineEndStation]
        
        lineLst.append(lineDayType)
        lineLst.append(lineStartStation)
        lineLst.append(lineStartTime)            
        lineLst.append(lineStationCluster)
        lineLst.append(lineEndStation)
        lineLst.append(lineHistoricalTime)
        lineLst.extend(lineWeatherLst)
        lineLst.append(lineHistoricOutflow)
        lineLst.append(lineBayesOutflow)            
        
        lineLst.append(travelTime)
        testLst.append(lineLst)
    count += 1
#%%
'''
Generating Testing Set*!
'''
aprData = open('APR.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
testLst = []
monthNum = 3        #for april
count = 0
for line in aprData:
    if count % 1000000 == 0:
        print(count)
        print(len(testLst))
    if '25-APR' in line:#!
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
        travelTime = convertTime(arr[4]) - lineStartTime
        if lineStartTime > 0:
            lineHistoricalTime = historicalBaseline(line)
            lineWeatherLst = weatherDayLst_avg[monthNum][lineDate - 1] 
            lineStationCluster = stationClusterLst[lineStartStation]
            lineEndStation = stationLst.index(arr[3])
            
            numIndex = (int) (lineHistoricalTime / 5)
            if numIndex > 14:
                numIndex = 14
            lineHistoricOutflow = historicTrafficOutflow[numIndex][lineEndStation]
            lineBayesOutflow = bayesTrafficOutflow[numIndex][lineEndStation]
            
            lineLst.append(lineDayType)
            lineLst.append(lineStartStation)
            lineLst.append(lineStartTime)            
            lineLst.append(lineStationCluster)
            lineLst.append(lineEndStation)
            lineLst.append(lineHistoricalTime)
            lineLst.extend(lineWeatherLst)
            lineLst.append(lineHistoricOutflow)
            lineLst.append(lineBayesOutflow)            
            
            lineLst.append(travelTime)
            testLst.append(lineLst)
    count += 1


aprData.close()

#%%
'''
Formatting training and testing data for predicting end station
'''
#Naive1
#obsolete
pickle_trainingLst_in = open('April1-24TrainingTimeNaive1.pickle', 'rb')
aprilTrainingLst = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()
pickle_trainingLst_in = open('MarchWholeTrainingTimeNaive1.pickle', 'rb')
marchTrainingLst = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()
#%%
#Naive2*
pickle_trainingLst_in = open('April1-24TrainingTimeNaive2.pickle', 'rb')
aprilTrainingLstNaive2 = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()                                
pickle_trainingLst_in = open('MarchWholeTrainingTimeNaive2.pickle', 'rb')
marchTrainingLstNaive2 = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()

#%%
#Bayes*
pickle_trainingLst_in = open('April1-24TrainingTimeBayes4.pickle', 'rb')
aprilTrainingLstBayes = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()            
#%%                    
pickle_trainingLst_in = open('MarchWholeTrainingTimeBayes.pickle', 'rb')
marchTrainingLstBayes = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()
#%%
aprilTrainingLstBayes = trainingLst
trainingLst = []
#%%
'''
Concatenating the Training List*!
'''
trainingLst_input = []
trainingLst_target = []

#for i in range(len(marchTrainingLstNaive2)):
#    if i % 2 == 0:        #10% used for training
#        if i % 1000000 == 0:
#            print(i)
#        trainingLst_input.append(np.array(marchTrainingLstNaive2][i][:-1])) #!
#        trainingLst_target.append(np.array(marchTrainingLstNaive2[i][-1]))
#        
#marchTrainingLstNaive2 = []
#print("Done with splitting March into features and target.")
#        
#for i in range(len(aprilTrainingLstNaive2)):
#    if i % 2 == 0:        #10% used for training
#        if i % 1000000 == 0:
#            print(i)
#        trainingLst_input.append(np.array(aprilTrainingLstNaive2[i][:-1]))
#        trainingLst_target.append(np.array(aprilTrainingLstNaive2[i][-1]))
#        
#aprilTrainingLstNaive2 = []
#print("Done with splitting April into features and target.")

#for i in range(len(marchTrainingLstBayes)):
#    if i % 2 == 0:        #50% used for training
#        if i % 1000000 == 0:
#            print(i)
#        inputLst = marchTrainingLstBayes[i][:7]
##        inputLst.append(marchTrainingLstBayes[i][10])
##        inputLst.extend(marchTrainingLstBayes[i][12:14])
#        inputLst.extend(marchTrainingLstBayes[i][14:16])
#        trainingLst_input.append(np.array(inputLst))  #!
#        trainingLst_target.append(np.array(marchTrainingLstBayes[i][-1]))
#        
#marchTrainingLstBayes = []
print("Done with splitting March into features and target.")
        
for i in range(len(aprilTrainingLstBayes)):
    if i % 2 == 0 or i % 2 == 1:        #50% used for training
        if i % 1000000 == 0:
            print(i)
        inputLst = []
        inputLst.extend(aprilTrainingLstBayes[i][:14])
#        inputLst.extend()
#        inputLst.append(aprilTrainingLstBayes[i][4])
#        inputLst.append(aprilTrainingLstBayes[i][5])
#        inputLst.append(aprilTrainingLstBayes[i][6])
#        inputLst.append(aprilTrainingLstBayes[i][10])
#        inputLst.extend(aprilTrainingLstBayes[i][12:14])
#        inputLst.append(aprilTrainingLstBayes[i][15] - aprilTrainingLstBayes[i][14])
        inputLst.extend(aprilTrainingLstBayes[i][14:16])
        trainingLst_input.append(np.array(inputLst))
        trainingLst_target.append(np.array(aprilTrainingLstBayes[i][-1]))
        
aprilTrainingLstBayes = []
print("Done with splitting April into features and target.")

trainingLst_input = np.array(trainingLst_input)
trainingLst_input[np.where(trainingLst_input == 'T')] = 0    
trainingLst_input = trainingLst_input.astype(float)
#trainingLst_input[np.where(trainingLst_input < 0)] = 0
trainingLst_target = np.array(trainingLst_target)
trainingLst_target[np.where(trainingLst_target == 'T')] = 0
trainingLst_target = trainingLst_target.astype(float)

#%%
#pickle_trainingLst_out = open('MarchApril24FinalTrainingNaive1Input.pickle', 'wb')
pickle_trainingLst_out = open('MarchApril24FinalTrainingBayes2Input.pickle', 'wb')
pickle.dump(trainingLst_input, pickle_trainingLst_out)
pickle_trainingLst_out.close()
print("Done with dumping features.")

#pickle_targetLst_out = open('MarchApril24FinalTrainingNaive1Target.pickle', 'wb')
pickle_targetLst_out = open('MarchApril24FinalTrainingBayes2Target.pickle', 'wb')
pickle.dump(trainingLst_target, pickle_targetLst_out)
pickle_targetLst_out.close()
print("Done with dumping target.")

#pickle_trainingLst_out = open('MarchApril24FinalTrainingNaive2Input.pickle', 'wb')
#pickle.dump(trainingLst_input, pickle_trainingLst_out)
#pickle_trainingLst_out.close()
#print("Done with dumping features.")
#
#pickle_targetLst_out = open('MarchApril24FinalTrainingNaive2Target.pickle', 'wb')
#pickle.dump(trainingLst_target, pickle_targetLst_out)
#pickle_targetLst_out.close()
#print("Done with dumping target.")

#%%
'''
Pickle in the training data*
'''
#pickle_in = open('MarchApril24FinalTrainingNaive1Input.pickle', 'rb')
#trainingLst_input = pickle.load(pickle_in)
#pickle_in.close()
#pickle_in = open('MarchApril24FinalTrainingNaive1Target.pickle', 'rb')
#trainingLst_target = pickle.load(pickle_in)
#pickle_in.close()

#pickle_in = open('MarchApril24FinalTrainingNaive2Input.pickle', 'rb')
#trainingLst_input = pickle.load(pickle_in)
#pickle_in.close()
#pickle_in = open('MarchApril24FinalTrainingNaive2Target.pickle', 'rb')
#trainingLst_target = pickle.load(pickle_in)
#pickle_in.close()

pickle_in = open('MarchApril24FinalTrainingBayesInput.pickle', 'rb')
trainingLst_input = pickle.load(pickle_in)
pickle_in.close()
pickle_in = open('MarchApril24FinalTrainingBayesTarget.pickle', 'rb')
trainingLst_target = pickle.load(pickle_in)
pickle_in.close()
#%%
'''
Bad tests
'''
testLst_input = []
testLst_target = []
for i in range(len(trainingLst)):
    if i % 30001 == 0:  #433 trips for testing February
        testLst_input.append(np.array(trainingLst[i][:-1]))
        testLst_target.append(np.array(trainingLst[i][-1]))
        
testLst_input = np.array(testLst_input)
testLst_input[np.where(testLst_input == 'T')] = 0
testLst_input = testLst_input.astype(float)
#testLst_input[np.where(testLst_input < 0)] = 0
testLst_target = np.array(testLst_target)
testLst_target[np.where(testLst_target == 'T')] = 0
testLst_target = testLst_target.astype(float)


#%%
'''
April 25 Test!*
'''
testLst_input2 = []
testLst_target2 = []
testLstHistorical_input2 = []
for i in range(len(testLst)):
    
    inputLst = []
    inputLst.extend(testLst[i][:14])
#    inputLst.append(testLst[i][4])
#    inputLst.append(testLst[i][5])
#    inputLst.append(testLst[i][6])
#    inputLst.append(testLst[i][10])
#    inputLst.extend(testLst[i][12:14])#!
    inputLst.extend(testLst[i][14:16])
#    inputLst.append(testLst[i][15] - testLst[i][14])
    
    testLst_input2.append(np.array(inputLst))#!
    testLst_target2.append(testLst[i][-1])    
    testLstHistorical_input2.append(testLst[i][5])

testLst_input2 = np.array(testLst_input2)
testLst_input2[np.where(testLst_input2 == 'T')] = 0
testLst_input2 = testLst_input2.astype(float)
#testLst_input[np.where(testLst_input < 0)] = 0
testLst_target2 = np.array(testLst_target2)
testLst_target2[np.where(testLst_target2 == 'T')] = 0
testLst_target2 = testLst_target2.astype(float)


testLstHistorical_input2 = np.array(testLstHistorical_input2).reshape(len(testLstHistorical_input2), 1)


#%%
'''
Normalization
'''
normed_trainingLst_input = normalize(trainingLst_input)
#normed_trainingLst_target = normalize(trainingLst_target)
normed_testLst_input2 = normalize(testLst_input2)
#normed_testLst_target2 = normalize(testLst_target2)
#%%
'''
No normalization*
'''
normed_trainingLst_input = trainingLst_input
normed_testLst_input2 = testLst_input2
#%%
'''
Smaller Training Lists *
'''
smallTrainingLst_input = []
smallTrainingLst_target = []
for i in range(len(trainingLst_input)):
    if i % 5000 == 0:
        smallTrainingLst_input.append(trainingLst_input[i])
        smallTrainingLst_target.append(trainingLst_target[i])
mediumTrainingLst_input = []
mediumTrainingLst_target = []
for i in range(len(trainingLst_input)):
    if i % 290 == 0:
        mediumTrainingLst_input.append(trainingLst_input[i])
        mediumTrainingLst_target.append(trainingLst_target[i])
largeTrainingLst_input = []
largeTrainingLst_target = []
for i in range(len(trainingLst_input)):
    if i % 20 == 0:
        largeTrainingLst_input.append(trainingLst_input[i])
        largeTrainingLst_target.append(trainingLst_target[i])
        
hugeTrainingLst_input = []
hugeTrainingLst_target = []
for i in range(len(trainingLst_input)):
    if i % 5 == 0:
        hugeTrainingLst_input.append(trainingLst_input[i])
        hugeTrainingLst_target.append(trainingLst_target[i])
#%%
largeTrainingLst_input = []
largeTrainingLst_target = []
for i in range(len(normed_trainingLst_input)):
    if i % 20 == 0:
        largeTrainingLst_input.append(normed_trainingLst_input[i])
        largeTrainingLst_target.append(normed_trainingLst_target[i])
        
hugeTrainingLst_input = []
hugeTrainingLst_target = []
for i in range(len(normed_trainingLst_input)):
    if i % 5 == 0:
        hugeTrainingLst_input.append(normed_trainingLst_input[i])
        hugeTrainingLst_target.append(normed_trainingLst_target[i])

#%%         
        

#%%
'''
Historical Only Training Set
'''
trainingLstHistorical_input = []
trainingLstHistorical_target = []


for i in range(len(marchTrainingLstNaive2)):
    if i % 2 == 0:        #10% used for training
        if i % 3000000 == 0:
            print(i)
        trainingLstHistorical_input.append(np.array(marchTrainingLstNaive2[i][5]))
        trainingLstHistorical_target.append(np.array(marchTrainingLstNaive2[i][-1]))
        
marchTrainingLstNaive2 = []
print("Done with splitting March into features and target.")
        
for i in range(len(aprilTrainingLstNaive2)):
    if i % 2 == 0:        #10% used for training
        if i % 3000000 == 0:
            print(i)
        trainingLstHistorical_input.append(np.array(aprilTrainingLstNaive2[i][5]))
        trainingLstHistorical_target.append(np.array(aprilTrainingLstNaive2[i][-1]))
        
aprilTrainingLstNaive2 = []
print("Done with splitting April into features and target.")

trainingLstHistorical_input = np.array(trainingLstHistorical_input)
trainingLstHistorical_input[np.where(trainingLstHistorical_input == 'T')] = 0    
trainingLstHistorical_input = trainingLstHistorical_input.astype(float)
trainingLstHistorical_target = np.array(trainingLstHistorical_target)
trainingLstHistorical_target[np.where(trainingLstHistorical_target == 'T')] = 0
trainingLstHistorical_target = trainingLstHistorical_target.astype(float)

lengthHistoricalLst = len(trainingLstHistorical_input)

trainingLstHistorical_input = trainingLstHistorical_input.reshape(lengthHistoricalLst, 1)
trainingLstHistorical_target = trainingLstHistorical_target.reshape(lengthHistoricalLst, 1)
#%%
'''
Linear Regression
'''
lr = LinearRegression()
y_pred_lr = lr.fit(normed_trainingLst_input, trainingLst_target)

#pickle_in = open('MarchApr24LRN1.pickle', 'rb')
#lr = pickle.load(pickle_in)
#pickle_in.close()
#%%
lr_Historical = LinearRegression()
y_pred_lr_Historical = lr_Historical.fit(trainingLstHistorical_input, trainingLstHistorical_target)
#%%
'''
Neighbors
'''
knr = KNeighborsRegressor()
y_pred_knr = knr.fit(normed_trainingLst_input, trainingLst_target)

#pickle_in = open('MarchApr24KNRN1.pickle', 'rb')
#knr = pickle.load(pickle_in)
#pickle_in.close()
#%%
knr_Historical = KNeighborsRegressor()
y_pred_knr_Historical = knr_Historical.fit(trainingLstHistorical_input, trainingLstHistorical_target)
#%%
'''
Ensemble
'''
gbr = GradientBoostingRegressor()
y_pred_gbc = gbr.fit(hugeTrainingLst_input, hugeTrainingLst_target)

#pickle_in = open('MarchApr24GBRN1.pickle', 'rb')
#gbr = pickle.load(pickle_in)
#pickle_in.close()
#%%
gbr_Historical = GradientBoostingRegressor()
y_pred_gbc_Historical = gbr_Historical.fit(trainingLstHistorical_input, trainingLstHistorical_target)
#%%
abr = AdaBoostRegressor()
y_pred_abr = abr.fit(trainingLst_input, trainingLst_target)

#%%
br = BaggingRegressor()
y_pred_br = br.fit(trainingLst_input, trainingLst_target)

#%%
etr = ExtraTreesRegressor()
y_pred_etr = etr.fit(trainingLst_input, trainingLst_target)

#%%
rfr = RandomForestRegressor()
y_pred_rfr = rfr.fit(trainingLst_input, trainingLst_target)

#%%
'''
Neural Network
'''
mlp = MLPRegressor()
y_pred_mlp = mlp.fit(largeTrainingLst_input, largeTrainingLst_target)

#pickle_in = open('MarchAprWholeMLPN1.pickle', 'rb') 
#mlp = pickle.load(pickle_in)
#pickle_in.close()

#%%
mlp_Historical = MLPRegressor()
y_pred_mlp_Historical = mlp_Historical.fit(trainingLstHistorical_input, trainingLstHistorical_target)


#%%
'''
Support Vector Regression
'''
svr = SVR()
y_pred_svr = svr.fit(hugeTrainingLst_input, hugeTrainingLst_target)


#%%
numTraining = 200
print('Testing with training data:')
print('Linear Regression: ', end = '')
print(lr.score(normed_trainingLst_input[:numTraining], trainingLst_target[:numTraining]))
print('K Neighbors Regression: ', end = '')
print(knr.score(normed_trainingLst_input[:numTraining], trainingLst_target[:numTraining]))
#==============================================================================
print('Gradient Boosting Regression: ', end = '')
print(gbr.score(normed_trainingLst_input[:numTraining], trainingLst_target[:numTraining]))
# print('AdaBoost Regression: ', end = '')
# print(abr.score(trainingLst_input[:100], trainingLst_target[:100]))
# print('Bagging Regression: ', end = '')
# print(br.score(trainingLst_input[:100], trainingLst_target[:100]))
# print('Extra Trees Regression: ', end = '')
# print(etr.score(trainingLst_input[:100], trainingLst_target[:100]))
# print('Random Forest Regression: ', end = '')
# print(rfr.score(trainingLst_input[:100], trainingLst_target[:100]))
print('Multi-Layer Perceptron Regression: ', end = '')
print(mlp.score(normed_trainingLst_input[:numTraining], trainingLst_target[:numTraining]))
#print('Support Vector Regression: ', end = '')
#print(svr.score(trainingLst_input[:100], trainingLst_target[:100]))
#==============================================================================
print()

# =============================================================================
# print('Testing with February data:')
# print('Linear Regression: ', end = '')
# print(lr.score(testLst_input, testLst_target))
# print('K Neighbors Regression: ', end = '')
# print(knr.score(testLst_input, testLst_target))
# =============================================================================
#==============================================================================
# print('Gradient Boosting Regression: ', end = '')
# print(gbr.score(testLst_input, testLst_target))
# print('AdaBoost Regression: ', end = '')
# print(abr.score(testLst_input, testLst_target))
# print('Bagging Regression: ', end = '')
# print(br.score(testLst_input, testLst_target))
# print('Extra Trees Regression: ', end = '')
# print(etr.score(testLst_input, testLst_target))
# print('Random Forest Regression: ', end = '')
# print(rfr.score(testLst_input, testLst_target))
# print('Multi-Layer Perceptron Regression: ', end = '')
# print(mlp.score(testLst_input, testLst_target))
#==============================================================================
#print()

print('Testing with April data:')
print('Linear Regression: ', end = '')
print(lr.score(normed_testLst_input2, testLst_target2))
#==============================================================================
print('K Neighbors Regression: ', end = '')
print(knr.score(normed_testLst_input2, testLst_target2))
print('Gradient Boosting Regression: ', end = '')
print(gbr.score(normed_testLst_input2, testLst_target2))
# print('AdaBoost Regression: ', end = '')
# print(abr.score(testLst_input2, testLst_target2))
# print('Bagging Regression: ', end = '')
# print(br.score(testLst_input2, testLst_target2))
# print('Extra Trees Regression: ', end = '')
# print(etr.score(testLst_input2, testLst_target2))
# print('Random Forest Regression: ', end = '')

# print(rfr.score(testLst_input2, testLst_target2))
print('Multi-Layer Perceptron Regression: ', end = '')
print(mlp.score(normed_testLst_input2, testLst_target2))
#print('Support Vector Regression: ', end = '')
#print(svr.score(testLst_input2, testLst_target2))
#==============================================================================
print()
#%%
'''
Average error in minutes*
'''
print("Scoring average error...")
numTest = 23816
#numTest = 30000


totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(normed_testLst_input2[i]).reshape(1,16)#*
    totalError += abs(testLst_target2[i] - lr.predict(tempArray)[0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average trip time: " + str(totalTripTime / numTest) + " minutes.")
print("Average Linear Regression error: " + str(totalError / (numTest)) + " minutes.")

totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(normed_testLst_input2[i]).reshape(1,16)
    totalError += abs(testLst_target2[i] - knr.predict(tempArray)[0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average K Neighbors Regression error: " + str(totalError / (numTest)) + " minutes.")

totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(normed_testLst_input2[i]).reshape(1,16)
    totalError += abs(testLst_target2[i] - gbr.predict(tempArray)[0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average Gradient Boosting Regression error: " + str(totalError / (numTest)) + " minutes.")

totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(normed_testLst_input2[i]).reshape(1,16)
    totalError += abs(testLst_target2[i] - mlp.predict(tempArray)[0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average Multi-Layer Preceptron Regression error: " + str(totalError / (numTest)) + " minutes.")
#%%
numTest = 620188
totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(normed_testLst_input2[i]).reshape(1,3)
    totalError += abs(testLst_target2[i] - tempArray[0][0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average Historical error: " + str(totalError / (numTest)) + " minutes.")

#totalError = 0
#totalTripTime = 0
#for i in range(numTest):
#    tempArray = np.array(testLst_input2[i]).reshape(1,10)
#    totalError += abs(testLst_target2[i] - svr.predict(tempArray)[0])
#    totalTripTime = totalTripTime + testLst_target2[i]
#print("Average Support Vector Regression error: " + str(totalError / (numTest)) + " minutes.")

#%%
'''
Historical Only Testing
''' 
print("Scoring average error...")
numTest = 620188
#numTest = 30000

totalError = 0
totalTripTime = 0
for i in range(numTest):
    tempArray = np.array(testLstHistorical_input2[i]).reshape(1,1)
    totalError += abs(testLst_target2[i] - lr_Historical.predict(tempArray)[0])
    totalTripTime = totalTripTime + testLst_target2[i]
print("Average trip time: " + str(totalTripTime / numTest) + " minutes.")
print("Average Linear Regression error: " + str(totalError / (numTest)) + " minutes.")

#totalError = 0
#totalTripTime = 0
#for i in range(numTest):
#    tempArray = np.array(testLst_input2[i]).reshape(1,6)
#    totalError += abs(testLst_target2[i] - lr_Historical.predict(tempArray)[0])
#    totalTripTime = totalTripTime + testLst_target2[i]
#print("Average trip time: " + str(totalTripTime / numTest) + " minutes.")
#print("Average Linear Regression error: " + str(totalError / (numTest)) + " minutes.")
#%%
pickle_lr_out = open('MarchApr24LRB2.pickle', 'wb')
pickle.dump(lr, pickle_lr_out)
pickle_lr_out.close()

pickle_knr_out = open('MarchApr24KNRB2.pickle', 'wb')
pickle.dump(knr, pickle_knr_out)
pickle_knr_out.close()

#==============================================================================
pickle_gbr_out = open('MarchApr24GBRB2.pickle', 'wb')
pickle.dump(gbr, pickle_gbr_out)
pickle_gbr_out.close()
# 
# pickle_abr_out = open('MarchAprWholeABR5.pickle', 'wb')
# pickle.dump(abr, pickle_abr_out)
# pickle_abr_out.close()
# 
# pickle_br_out = open('MarchAprWholeBR5.pickle', 'wb')
# pickle.dump(br, pickle_br_out)
# pickle_br_out.close()
# 
# pickle_etr_out = open('MarchAprWholeETR5.pickle', 'wb')
# pickle.dump(etr, pickle_etr_out)
# pickle_etr_out.close()
# 
# pickle_rfr_out = open('MarchAprWholeRFR5.pickle', 'wb')
# pickle.dump(rfr, pickle_rfr_out)
# pickle_rfr_out.close()
# 
pickle_mlp_out = open('MarchAprWholeMLPB2.pickle', 'wb')
pickle.dump(mlp, pickle_mlp_out)
pickle_mlp_out.close()
# 
#==============================================================================




