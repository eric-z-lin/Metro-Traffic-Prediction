# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 08:54:16 2017

@author: Eric Lin
Naive Bayes for station probability distribution.
"""
import os
import pickle
from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from datetime import datetime
from sklearn.svm import SVC, libsvm
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier
import numpy as np

os.chdir('C:/Users/GGSAdminLab/Documents/Eric Lin/Metro Data Project/FinalCode')


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

#%%
'''
Generating Training Set
'''
def convertTime(rawTime):
    timeFMT = '%I:%M:%S%p'
    groundTime = '04:00:00AM'
    timeDiff = datetime.strptime(rawTime, timeFMT) - datetime.strptime(groundTime, timeFMT)
    timeDiff = timeDiff.total_seconds()
    timeDiff = timeDiff // 60       #minutes since 4am
    return timeDiff
#%%
janData = open('JAN.csv', 'r')
febData = open('FEB.csv', 'r')
marData = open('MAR.csv', 'r')
aprData = open('APR.csv', 'r')
mayData = open('MAY.csv', 'r')
#junData = open('JUN.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
trainingLst = []


monthNum = 0        #for January
count = 0
for line in janData:
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
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('JanuaryWholeTraining.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()
    
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
#            trainingLst.append(lineLst)
#    count += 1
#pickle_training_out = open('FebruaryWholeTraining.pickle', 'wb')
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
            trainingLst.append(lineLst)
    count += 1    
pickle_training_out = open('MarchWholeTraining.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()

trainingLst = []
monthNum = 3        #for april
count = 0
for line in aprData:
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
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('AprilWholeTraining.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()

trainingLst = []    
monthNum = 4        #for may
count = 0
for line in mayData:
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
            trainingLst.append(lineLst)
    count += 1
pickle_training_out = open('MayWholeTraining.pickle', 'wb')
pickle.dump(trainingLst, pickle_training_out)
pickle_training_out.close()

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
Generating Testing Set
'''
marData = open('MAR.csv', 'r')
pickle_stations_in = open('StationList.pickle', 'rb')
stationLst = pickle.load(pickle_stations_in)
pickle_stations_in.close()
testLst = []
monthNum = 2        #for march
count = 0
for line in marData:
    if count % 300000 == 0:
        print(count)
        print(len(testLst))
    if 'ENTRY' not in line and count % 20000 == 0:
#        print(line)
        lineLst = []
        arr = line.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].replace('"', '')
        lineDate = int(arr[0][0:2])
        lineDayType = dayTypeLst[monthNum][lineDate - 1]
        lineStartStation = stationLst.index(arr[1])
        lineStartTime = convertTime(arr[2])
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
            testLst.append(np.array(lineLst))
    count += 1


marData.close()

#%%
'''
Formatting training and testing data for predicting end station
'''
pickle_trainingLst_in = open('FebruaryWholeTraining.pickle', 'rb')
trainingLst = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()
pickle_trainingLst_in = open('MarchWholeTraining.pickle', 'rb')
trainingLst.extend(pickle.load(pickle_trainingLst_in))
pickle_trainingLst_in.close()
trainingLst_input = []
trainingLst_target = []
#for i in trainingLst:
for i in range(len(trainingLst)):
    if i % 15 == 0:        #2,600,000 trips from february used for training
        trainingLst_input.append(np.array(trainingLst[i][:-1]))
        trainingLst_target.append(np.array(trainingLst[i][-1]))

trainingLst_input = np.array(trainingLst_input)
trainingLst_input[np.where(trainingLst_input == 'T')] = 0    
trainingLst_input = trainingLst_input.astype(float)
#trainingLst_input[np.where(trainingLst_input < 0)] = 0
trainingLst_target = np.array(trainingLst_target)
trainingLst_target[np.where(trainingLst_target == 'T')] = 0
trainingLst_target = trainingLst_target.astype(float)
#%%
testLst_input = []
testLst_target = []
for i in range(len(trainingLst)):
    if i % 30001 == 0:  #433 trips for testing February
        testLst_input.append(np.array(trainingLst[i][:-1]))
        testLst_target.append(np.array(trainingLst[i][-1]))

testLst_input2 = []
testLst_target2 = []
for i in range(len(testLst)):
    testLst_input2.append(testLst[i][:-1])
    testLst_target2.append(testLst[-i][-1])    



testLst_input = np.array(testLst_input)
testLst_input[np.where(testLst_input == 'T')] = 0
testLst_input = testLst_input.astype(float)
#testLst_input[np.where(testLst_input < 0)] = 0
testLst_target = np.array(testLst_target)
testLst_target[np.where(testLst_target == 'T')] = 0
testLst_target = testLst_target.astype(float)

testLst_input2 = np.array(testLst_input2)
testLst_input2[np.where(testLst_input2 == 'T')] = 0
testLst_input2 = testLst_input2.astype(float)
#testLst_input[np.where(testLst_input < 0)] = 0
testLst_target2 = np.array(testLst_target2)
testLst_target2[np.where(testLst_target2 == 'T')] = 0
testLst_target2 = testLst_target2.astype(float)

#%%
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
    if i % 50 == 0:
        largeTrainingLst_input.append(trainingLst_input[i])
        largeTrainingLst_target.append(trainingLst_target[i])
        
hugeTrainingLst_input = []
hugeTrainingLst_target = []
for i in range(len(trainingLst_input)):
    if i % 8 == 0:
        hugeTrainingLst_input.append(trainingLst_input[i])
        hugeTrainingLst_target.append(trainingLst_target[i])

#%%
'''
Formatting training and testing data for predicting end station cluster
'''
pickle_trainingLst_in = open('FebruaryWholeTraining.pickle', 'rb')
trainingLst = pickle.load(pickle_trainingLst_in)
pickle_trainingLst_in.close()
trainingClusterLst_input = []
trainingClusterLst_target = []

for i in range(len(trainingLst)):
    if i % 4 == 0:        #3,250,000 trips from february used for training
        trainingClusterLst_input.append(np.array(trainingLst[i][:-2]))
        trainingClusterLst_target.append(np.array(trainingLst[i][-2]))
        
#==============================================================================
# testClusterLst_input = []
# testClusterLst_target = []
# for i in range(len(trainingLst)):
#     if i % 30001 == 0:  #433 trips for testing February
#         testClusterLst_input.append(np.array(trainingLst[i][:-2]))
#         testClusterLst_target.append(np.array(trainingLst[i][-2]))
# 
# testClusterLst_input2 = []
# testClusterLst_target2 = []
# for i in range(len(testLst)):
#     testClusterLst_input2.append(testLst[i][:-2])
#     testClusterLst_target2.append(testLst[-i][-2])
#==============================================================================
    
trainingClusterLst_input = np.array(trainingClusterLst_input)
trainingClusterLst_input[np.where(trainingClusterLst_input == 'T')] = 0    
trainingClusterLst_input = trainingClusterLst_input.astype(float)
#trainingLst_input[np.where(trainingLst_input < 0)] = 0
trainingClusterLst_target = np.array(trainingClusterLst_target)
trainingClusterLst_target[np.where(trainingClusterLst_target == 'T')] = 0
trainingClusterLst_target = trainingClusterLst_target.astype(float)

#==============================================================================
# testClusterLst_input = np.array(testClusterLst_input)
# testClusterLst_input[np.where(testClusterLst_input == 'T')] = 0
# testClusterLst_input = testClusterLst_input.astype(float)
# #testLst_input[np.where(testLst_input < 0)] = 0
# testClusterLst_target = np.array(testClusterLst_target)
# testClusterLst_target[np.where(testClusterLst_target == 'T')] = 0
# testClusterLst_target = testClusterLst_target.astype(float)
# 
# testClusterLst_input2 = np.array(testClusterLst_input2)
# testClusterLst_input2[np.where(testClusterLst_input2 == 'T')] = 0
# testClusterLst_input2 = testClusterLst_input2.astype(float)
# #testLst_input[np.where(testLst_input < 0)] = 0
# testClusterLst_target2 = np.array(testClusterLst_target2)
# testClusterLst_target2[np.where(testClusterLst_target2 == 'T')] = 0
# testClusterLst_target2 = testClusterLst_target2.astype(float)
#==============================================================================

#%%
#==============================================================================
# smallClusterTrainingLst_input = []
# smallClusterTrainingLst_target = []
# for i in range(len(trainingClusterLst_input)):
#     if i % 3000 == 0:
#         smallClusterTrainingLst_input.append(trainingClusterLst_input[i])
#         smallClusterTrainingLst_target.append(trainingClusterLst_target[i])
# mediumClusterTrainingLst_input = []
# mediumClusterTrainingLst_target = []
# for i in range(len(trainingClusterLst_input)):
#     if i % 290 == 0:
#         mediumClusterTrainingLst_input.append(trainingClusterLst_input[i])
#         mediumClusterTrainingLst_target.append(trainingClusterLst_target[i])
#         
# largeClusterTrainingLst_input = []
# largeClusterTrainingLst_target = []
# for i in range(len(trainingClusterLst_input)):
#     if i % 100 == 0:
#         largeClusterTrainingLst_input.append(trainingClusterLst_input[i])
#         largeClusterTrainingLst_target.append(trainingClusterLst_target[i])
#==============================================================================
        
hugeClusterTrainingLst_input = []
hugeClusterTrainingLst_target = []
for i in range(len(trainingClusterLst_input)):
    if i % 8 == 0:
        hugeClusterTrainingLst_input.append(trainingClusterLst_input[i])
        hugeClusterTrainingLst_target.append(trainingClusterLst_target[i])
#%%
'''
Naive Bayes
'''
#==============================================================================
# iris = datasets.load_iris()
# gnb = GaussianNB()
# y_pred = gnb.fit(iris.data, iris.target).predict(iris.data)
# print('Number of mislabeled points out of a total %d points: %d'
#        %(iris.data.shape[0], (iris.target != y_pred).sum()))
#==============================================================================
gnb = GaussianNB()
y_pred_gnb = gnb.fit(trainingLst_input, trainingLst_target)
mnb = MultinomialNB()
y_pred_mnb = mnb.fit(trainingLst_input, trainingLst_target)
#
#gnbProbList = gnb.predict_proba(trainingLst_input[:100])
#mnbProbList = mnb.predict_proba(trainingLst_input[:100])
#gnbProbList2 = gnb.predict_proba(testLst_input)
#mnbProbList2 = mnb.predict_proba(testLst_input)
#gnbProbList3 = gnb.predict_proba(testLst_input2)
#mnbProbList3 = mnb.predict_proba(testLst_input2)
#%%
gnbC = GaussianNB()
y_pred_gnbC = gnbC.fit(trainingClusterLst_input, trainingClusterLst_target)
mnbC = MultinomialNB()
y_pred_mnbC = mnbC.fit(trainingClusterLst_input, trainingClusterLst_target)
#%%
'''
Logistic Regression
'''
lr = LogisticRegression()
y_pred_lr = lr.fit(largeTrainingLst_input, largeTrainingLst_target)

#%%
lrC = LogisticRegression()
y_pred_lrC = lrC.fit(largeClusterTrainingLst_input, largeClusterTrainingLst_target)
#%%
lrcv = LogisticRegressionCV()
y_pred_lrcv = lrcv.fit(largeTrainingLst_input, largeTrainingLst_target)

#%%
lrcvC = LogisticRegressionCV()
y_pred_lrcvC = lrcvC.fit(largeClusterTrainingLst_input, largeClusterTrainingLst_target)
#%%
'''
Multiclass
'''

ovrRBF = OneVsRestClassifier(SVC(kernel = 'rbf'))  #linear, poly, rbf (radial)
y_pred_ovr = ovrRBF.fit(smallTrainingLst_input, smallTrainingLst_target)

ovrPoly = OneVsRestClassifier(SVC(kernel = 'poly'))  #linear, poly, rbf (radial)
y_pred_ovrPoly = ovrPoly.fit(smallTrainingLst_input, smallTrainingLst_target)

#%%
ovrRBFC = OneVsRestClassifier(SVC(kenerl = 'rbf'))
y_pred_ovrC = ovrRBFC.fit(smallClusterTrainingLst_input, smallClusterTrainingLst_target)

#%%
ovrPolyC = OneVsRestClassifier(SVC(kernel = 'poly')) 
y_pred_ovrPolyC = ovrPolyC.fit(smallClusterTrainingLst_input, smallClusterTrainingLst_target)
#%%
'''
Multioutput
'''
#moc = MultiOutputClassifier(SVC(kernel = 'rbf'))
#y_pred_moc = moc.fit(smallTrainingLst_input, smallTrainingLst_target)

#%%
'''
Neighbors
'''
knc = KNeighborsClassifier()
y_pred_knc = knc.fit(trainingLst_input, trainingLst_target)

#%%
kncC = KNeighborsClassifier()
y_pred_kncC = kncC.fit(hugeClusterTrainingLst_input, hugeClusterTrainingLst_target)

#%%
'''
Ensemble
'''
gbc = GradientBoostingClassifier()
y_pred_gbc = gbc.fit(largeTrainingLst_input, largeTrainingLst_target)

#%%
abc = AdaBoostClassifier()
y_pred_abc = abc.fit(hugeTrainingLst_input, hugeTrainingLst_target)

#%%
'''
Neural Network
'''
mlp = MLPClassifier()
y_pred_mlp = mlp.fit(hugeTrainingLst_input, hugeTrainingLst_target)

#%%
mlpC = MLPClassifier()
y_pred_mlpC = mlpC.fit(hugeClusterTrainingLst_input, hugeClusterTrainingLst_target)
#%%
'''
Calibration
'''
#clf_isotonic = CalibratedClassifierCV(gnb, method = 'isotonic', cv = 1)
#y_pred_clfIsotonic = clf_isotonic.fit(smallTrainingLst_input, smallTrainingLst_target)
#clf_sigmoid = CalibratedClassifierCV(gnb, method = 'sigmoid', cv = 1)
#y_pred_clfSigmoid = clf_sigmoid.fit(smallTrainingLst_input, smallTrainingLst_target)

#%%
'''
Supervised
'''
lpKNN = LabelPropagation(kernel = 'knn') 
y_pred_lpKNN = lpKNN.fit(mediumTrainingLst_input, mediumTrainingLst_target)
lpRBF = LabelPropagation(kernel = 'rbf')
y_pred_lpRBF = lpRBF.fit(mediumTrainingLst_input, mediumTrainingLst_target)

#%%
lpKNNC = LabelPropagation(kernel = 'knn')
y_pred_lpKNNC = lpKNNC.fit(mediumClusterTrainingLst_input, mediumClusterTrainingLst_target)
lpRBFC = LabelPropagation(kernel = 'rbf')
y_pred_lpRBFC = lpRBFC.fit(mediumClusterTrainingLst_input, mediumClusterTrainingLst_target)
#%%
lsKNN = LabelSpreading(kernel = 'knn') 
y_pred_lsKNN = lsKNN.fit(mediumTrainingLst_input, mediumTrainingLst_target)
lsRBF = LabelSpreading(kernel = 'rbf')
y_pred_lsRBF = lsRBF.fit(mediumTrainingLst_input, mediumTrainingLst_target)

#%%
lsKNNC = LabelSpreading(kernel = 'knn')
y_pred_lsKNNC = lsKNNC.fit(mediumClusterTrainingLst_input, mediumClusterTrainingLst_target)
lsRBFC = LabelSpreading(kernel = 'rbf')
y_pred_lsRBFC = lsRBFC.fit(mediumClusterTrainingLst_input, mediumClusterTrainingLst_target)
#%%
'''
Libsvm
'''
#lsvm = libsvm()
y_pred_lsvm = libsvm.fit(np.array(smallTrainingLst_input), np.array(smallTrainingLst_target))

#%%
def svmScore(predictLst, targetLst):
    correctCount = 0
    for i in range(len(predictLst)):
        if predictLst[i] == targetLst[i]:
            correctCount += 1
    return correctCount / len(predictLst)

print('Testing with training data:')
#print('Gaussian Naive Bayes, 100% Data: ', end = '')
#print(gnb.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Multinomial Naive Bayes, 100% Data: ', end = '')
#print(mnb.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Logistic Regression, 1/10 Data: ', end = '')
#print(lr.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Logistic Regression Cross-Validated, 1/10 Data: ', end = '')
#print(lrcv.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('One vs. Rest RBF, 1/30 Data: ', end = '')
#print(ovrRBF.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('One vs. Rest Polynomial, 1/30 Data: ', end = '')
#print(ovrPoly.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('k-Neighbors Classifier, 100% Data: ', end = '')
#print(knc.score(trainingLst_input[:100], trainingLst_target[:100]))
print('Gradient Boosting Classifier, 100% Data: ', end = '')
print(gbc.score(trainingLst_input[:100], trainingLst_target[:100]))
print('AdaBoost Classifier, 100% Data: ', end = '')
print(abc.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Multi-layer Perceptron, 100% Data: ', end = '')
#print(mlp.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Label Propagation KNN, 1/10 Data: ', end = '')
#print(lpKNN.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Label Propagation RBF, 1/10 Data: ', end = '')
#print(lpRBF.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Label Spread KNN, 1/30 Data: ', end = '')
#print(lsKNN.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Label Spread RBF, 1/30 Data: ', end = '')
#print(lsRBF.score(trainingLst_input[:100], trainingLst_target[:100]))

#print('Support Vector Machine, 1/30 Data: ', end = '')
#print(svmScore(libsvm.predict(trainingLst_input[:100]), trainingLst_target[:100]))
#print('Calibrated GNB Isotonic: ', end = '')
#print(clf_isotonic.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('Calibrated GNB Sigmoid: ', end = '')
#print(clf_sigmoid.score(trainingLst_input[:100], trainingLst_target[:100]))
#print('MOC: ', end = '')
#print(moc.score(trainingLst_input[:100], trainingLst_target[:100]))
print()

print('Testing with February data:')
#print('Gaussian Naive Bayes, 100% Data: ', end = '')
#print(gnb.score(testLst_input, testLst_target))
#print('Multinomial Naive Bayes, 100% Data: ', end = '')
#print(mnb.score(testLst_input, testLst_target))
#print('Logistic Regression, 1/10 Data: ', end = '')
#print(lr.score(testLst_input, testLst_target))
#print('Logistic Regression Cross-Validated, 1/10 Data: ', end = '')
#print(lrcv.score(testLst_input, testLst_target))
#print('One vs. Rest RBF, 1/30 Data: ', end = '')
#print(ovrRBF.score(testLst_input, testLst_target))
#print('One vs. Rest Polynomial, 1/30 Data: ', end = '')
#print(ovrPoly.score(testLst_input, testLst_target))
#print('k-Neighbors Classifier, 100% Data: ', end = '')
#print(knc.score(testLst_input, testLst_target))
print('Gradient Boosting Classifier, 100% Data: ', end = '')
print(gbc.score(testLst_input, testLst_target))
print('AdaBoost Classifier, 100% Data: ', end = '')
print(abc.score(testLst_input, testLst_target))
#print('Multi-layer Perceptron, 100% Data: ', end = '')
#print(mlp.score(testLst_input, testLst_target))
#print('Label Propagation KNN, 1/10 Data: ', end = '')
#print(lpKNN.score(testLst_input, testLst_target))
#print('Label Propagation RBF, 1/10 Data: ', end = '')
#print(lpRBF.score(testLst_input, testLst_target))
#print('Label Spread KNN, 1/30 Data: ', end = '')
#print(lpKNN.score(testLst_input, testLst_target))
#print('Label Spread RBF, 1/30 Data: ', end = '')
#print(lpRBF.score(testLst_input, testLst_target))
#print('Support Vector Machine, 1/30 Data: ', end = '')
#print(svmScore(libsvm.predict(testLst_input), testLst_target))
#print('Calibrated GNB Isotonic: ', end = '')
#print(clf_isotonic.score(testLst_input, testLst_target))
#print('Calibrated GNB Sigmoid: ', end = '')
#print(clf_sigmoid.score(testLst_input, testLst_target))
#print('MOC: ', end = '')
#print(moc.score(testLst_input, testLst_target))
print()

print('Testing with March data:')
#print('Gaussian Naive Bayes, 100% Data: ', end = '')
#print(gnb.score(testLst_input2, testLst_target2))
#print('Multinomial Naive Bayes, 100% Data: ', end = '')
#print(mnb.score(testLst_input2, testLst_target2))
#print('Logistic Regression, 1/10 Data: ', end = '')
#print(lr.score(testLst_input2, testLst_target2))
#print('Logistic Regression Cross-Validated, 1/10 Data: ', end = '')
#print(lrcv.score(testLst_input2, testLst_target2))
#print('One vs. Rest RBF, 1/30 Data: ', end = '')
#print(ovrRBF.score(testLst_input2, testLst_target2))
#print('One vs. Rest Polynomial, 1/30 Data: ', end = '')
#print(ovrPoly.score(testLst_input2, testLst_target2))
#print('k-Neighbors Classifier, 100% Data: ', end = '')
#print(knc.score(testLst_input2, testLst_target2))
print('Gradient Boosting Classifier, 100% Data: ', end = '')
print(gbc.score(testLst_input2, testLst_target2))
print('AdaBoost Classifier, 100% Data: ', end = '')
print(abc.score(testLst_input2, testLst_target2))
#print('Multi-layer Perceptron, 100% Data: ', end = '')
#print(mlp.score(testLst_input2, testLst_target2))
#print('Label Propagation KNN, 1/10 Data: ', end = '')
#print(lpKNN.score(testLst_input2, testLst_target2))
#print('Label Propagation RBF, 1/10 Data: ', end = '')
#print(lpRBF.score(testLst_input2, testLst_target2))
#print('Label Spread KNN, 1/30 Data: ', end = '')
#print(lsKNN.score(testLst_input2, testLst_target2))
#print('Label Spread RBF, 1/30 Data: ', end = '')
#print(lsRBF.score(testLst_input2, testLst_target2))
#print('Support Vector Machine, 1/30 Data: ', end = '')
#print(svmScore(libsvm.predict(testLst_input2), testLst_target2))
#print('Calibrated GNB Isotonic: ', end = '')
#print(clf_isotonic.score(testLst_input2, testLst_target2))
#print('Calibrated GNB Sigmoid: ', end = '')
#print(clf_sigmoid.score(testLst_input2, testLst_target2))
#print('MOC: ', end = '')
#print(moc.score(testLst_input2, testLst_target2))
print()

#%%
#==============================================================================
# pickle_gnb_out = open('FebruaryWholeGNB.pickle', 'wb')
# pickle.dump(gnb, pickle_gnb_out)
# pickle_gnb_out.close()
# 
# pickle_mnb_out = open('FebruaryWholeMNB.pickle', 'wb')
# pickle.dump(mnb, pickle_mnb_out)
# pickle_mnb_out.close()
# 
# pickle_lr_out = open('FebruaryWholeLR.pickle', 'wb')
# pickle.dump(lr, pickle_lr_out)
# pickle_lr_out.close()
# 
# pickle_lrcv_out = open('FebruaryWholeLRCV.pickle', 'wb')
# pickle.dump(lrcv, pickle_lrcv_out)
# pickle_lrcv_out.close()
#==============================================================================

#pickle_ovrRBF_out = open('FebruaryWholeOVRRBF.pickle', 'wb')
#pickle.dump(ovrRBF, pickle_ovrRBF_out)
#pickle_ovrRBF_out.close()
#
#pickle_ovrPoly_out = open('FebruaryWholeOVRPoly.pickle', 'wb')
#pickle.dump(ovrPoly, pickle_ovrPoly_out)
#pickle_ovrPoly_out.close()

#==============================================================================
# pickle_knc_out = open('FebMarchWholeKNC.pickle', 'wb')
# pickle.dump(knc, pickle_knc_out)
# pickle_knc_out.close()
#==============================================================================

pickle_gbc_out = open('FebMarchWholeGBC.pickle', 'wb')
pickle.dump(gbc, pickle_gbc_out)
pickle_gbc_out.close()

pickle_abc_out = open('FebMarchWholeABC.pickle', 'wb')
pickle.dump(abc, pickle_abc_out)
pickle_abc_out.close()
#==============================================================================
# #pickle_mlp_out = open('FebruaryWholeMLP.pickle', 'wb')
# #pickle.dump(mlp, pickle_mlp_out)
# #pickle_mlp_out.close()
# 
# #pickle_lpKNN_out = open('FebruaryWholeLPKNN.pickle', 'wb')
# #pickle.dump(lpKNN, pickle_lpKNN_out)
# #pickle_lpKNN_out.close()
# #
# #pickle_lpRBF_out = open('FebruaryWholeLPRBF.pickle', 'wb')
# #pickle.dump(lpRBF, pickle_lpRBF_out)
# #pickle_lpRBF_out.close()
# #
# #pickle_lsKNN_out = open('FebruaryWholeLSKNN.pickle', 'wb')
# #pickle.dump(lsKNN, pickle_lsKNN_out)
# #pickle_lsKNN_out.close()
# #
# #pickle_lsRBF_out = open('FebruaryWholeLSRBF.pickle', 'wb')
# #pickle.dump(lsRBF, pickle_lsRBF_out)
# #pickle_lsRBF_out.close()
#==============================================================================

#pickle_lsvm_out = open('FebruaryWholeLSVM.pickle', 'wb')
#pickle.dump(y_pred_lsvm, pickle_lsvm_out)
#pickle_lsvm_out.close()

#pickle_clf_iso_out = open('FebruaryWholeCLFIsotonic.pickle', 'wb')
#pickle.dump(clf_isotonic, pickle_clf_iso_out)
#pickle_clf_iso_out.close()
#
#pickle_clf_sigmoid_out = open('FebruaryWholeCLFSigmoid.pickle', 'wb')
#pickle.dump(clf_sigmoid, pickle_clf_sigmoid_out)
#pickle_clf_sigmoid_out.close()

#pickle_moc_out = open('FebruaryWholeMOC.pickle', 'wb')
#pickle.dump(moc, pickle_moc_out)
#pickle_moc_out.close()


