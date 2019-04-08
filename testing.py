import csv
import pandas

test_path = '/Users/Yohan/Desktop/Course/csc494-project/data/lipad/2018/6/2018-6-1.csv'
with open(test_path) as proc_file:
    csv_reader = csv.reader(proc_file)
    count = 0
    for row in csv_reader:
        print(row[10])
        count += 1
        if count == 2:
            break
        