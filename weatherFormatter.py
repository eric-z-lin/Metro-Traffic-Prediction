'''
Eric Lin
July 29th, 2017
Weather Formatter

'''
import os
import pickle


os.chdir('C:/Users/GGSAdminLab/Documents/Eric Lin/Metro Data Project/FinalCode')
file_in = open('meterologyData.csv', "r")
result_lst = []     #3D: 1st dim is month, 2nd is day, 3rd are meteorlogical values
month_lst = []
for line in file_in:
    if '2017' in line:
        if len(month_lst) > 1:
            result_lst.append(month_lst)
            month_lst = []
    elif 'high' in line:
        d = 0   #do nothing
    else:
        arr = line.split(',')
#        print(arr)
        if ' ' in arr[-3]:
            arr[-3] = arr[-3] + arr[-2] + arr[-1]
            arr.pop()
            arr.pop()
#            print(arr)
        elif ' ' in arr[-2]:
            arr[-2] = arr[-2] + arr[-1]
            arr.pop()
#            print(arr)
        for i in range(len(arr) - 1):
            if arr[i] == '-' or arr[i] == 'T':
                arr[i] = 0
            else:
                arr[i] = float(arr[i])
        month_lst.append(arr)
result_lst.append(month_lst)


file_in.close()
pickle_out = open('meterologyJantoJun.pickle', 'wb')
pickle.dump(result_lst, pickle_out)
pickle_out.close()
