# PyDM
#   PDR : Python Data Manager
#   This library is coded by LeoDev (AKA BanHammer256, Cosmic)

import time

items = []
values = []

def delay(i_time):
    time.sleep(i_time)

def get_item(filename, itemname):
    rawfile = open(filename)
    file = rawfile.read()
    lines = file.split('\n')
    for i in lines: #Split the lines
        itemval = i.split('==')
        items.append(itemval[0])
        values.append(itemval[1])
    for item in items: #Check if item exists
        if item == itemname:
            index = items.index(itemname)
            return(values[index])
    rawfile.close()

def add_item(filename, itemname, value):
    ext_check = filename.endswith('.pdr')
    if (ext_check == True):
        with open(filename, 'a') as f:
            #check if value doesnt exist
            test = get_item(filename, itemname)
            if (test == None):
                f.write("\n" + itemname + "==" + value)
    f.close()

def read(filename):
        rawfile = open(filename)
        file = rawfile.read()
        lines = file.split('\n')
        for i in lines: #Split the lines
            itemval = i.split('==')
            items.append(itemval[0])
            values.append(itemval[1])
        rawfile.close()

def edit_item(filename, itemname, value):
    read(filename)
    #find index
    if itemname in items:
        index = items.index(itemname)
    #replace item value
    rawfile = open(filename, 'r')
    lines = rawfile.readlines()
    lines[index] = f'{itemname}=={value}'
    rawfile.close()
    rawfile = open(filename, 'w')
    rawfile.writelines(lines)
    rawfile.close()

def get_number_of_items(filename):
    num = 0
    read(filename)
    for i in items:
        num += 1
    return(num)

def flush(filename):
    rawfile = open(filename, 'r+')
    rawfile.truncate(0)
    rawfile.close()