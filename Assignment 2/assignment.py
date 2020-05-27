import numpy as np
import subprocess
import csv


def get_source_nodes():
    source_nodes = input("enter amount of source nodes: ") ## THIS IS Y
    while True:
        try:
            if int(source_nodes) >= 1:
                return source_nodes
            else:
                print("source_nodes needs to be greater than one")
                source_nodes = input("enter amount of source nodes: ") ## THIS IS X   
        except ValueError:
            print("source_nodes needs to be a integer value greater than one")
            source_nodes = input("enter amount of source nodes: ") ## THIS IS X
            
            
def get_transit_nodes():
    transit_nodes = input("enter amount of transit nodes: ") ## THIS IS Y
    while True:
        try:
            if int(transit_nodes) >= 2:
                return transit_nodes
            else:
                print("transit_nodes needs to be greater than two")
                transit_nodes = input("enter amount of transit nodes: ") ## THIS IS Y    
        except ValueError:
            print("transit_nodes needs to be a integer value greater than two")
            transit_nodes = input("enter amount of transit nodes: ") ## THIS IS Y    
    
def get_destination_nodes():
    destination_nodes = input("enter amount of destination nodes: ") ## THIS IS Y
    while True:
        try:
            if int(destination_nodes) >= 1:
                return destination_nodes
            else:
                print("destination_nodes needs to be greater than one")
                destination_nodes = input("enter amount of destination nodes: ") ## THIS IS Z   
        except ValueError:
            print("destination_nodes needs to be a integer value greater than one")
            destination_nodes = input("enter amount of destination nodes: ") ## THIS IS Z
            
          
source_nodes = get_source_nodes()    
print() 
transit_nodes = get_transit_nodes()
print()
destination_nodes = get_destination_nodes()

a = []
i_ = 0
while i_ < int(source_nodes):
    a.append("s"+str(i_+1))
    i_ += 1
print(a)

b = []
ii = 0
while ii < int(transit_nodes):
    b.append("t"+str(ii+1))
    ii += 1
print(b)

c = []
iii = 0
while iii < int(destination_nodes):
    c.append("d"+str(iii+1))
    iii += 1
print(c)
#a = ['A', 'B', 'C', 'D']
#b = ['X', 'Y', 'Z']
#c = [1, 2, 3, 4]

demandVolumes = [[40,30,20,10],[10,60,20,40],[20,20,20,20],[70,30,50,10]]


#f = open("assignment.lp", "w")
bounds = ''
ans = ''
function = 'r'

"""demand constraints"""
for i, ai in enumerate(a):
    
    for j, cj in enumerate(c):
        empty = '    dem{}{} : '.format(ai, cj)
         
        for k in range(len(b)):
            if k == len(b) -1:
                empty += "x{}{}{} = {}".format(ai, b[k], cj, demandVolumes[i][j])
            else:
                empty += "x{}{}{} + ".format(ai, b[k], cj)
        
        ans += "\n" + empty
        
        
"""capacity constraints"""

for i in a:
    for j in b:
        #print("cap{}{}".format(i, j))
        empty = '    cap{}{} : '.format(i, j)
        for k in range(len(c)):
            if k == len(c) -1:
                empty += "x{}{}{} - 100r <= 0".format(i, j, c[k])
            else:
                empty += "x{}{}{} + ".format(i, j, c[k])
        
        ans += "\n" + empty
        
        
for k in c:
    for j in b:
        #print("cap{}{}".format(i, j))
        empty = '    cap{}{} : '.format(j, k)
        for i in range(len(a)):
            if i == len(a) -1:
                empty += "x{}{}{} - 100r <= 0".format(a[i], j, k)
            else:
                empty += "x{}{}{} + ".format(a[i], j, k)
            bounds += '\n    x{}{}{} >= 0'.format(a[i], j, k)
        ans += "\n" + empty
        
        
    #ans += "\n" + empty
    
#for j in range(len(b)):
    #empty = '    b{} : '.format(j+1)
    
    #for i in range(len(a)):

        #if i == len(a) -1:
            #empty += "x{}{} = {}".format(i+1, j+1, b[j])
        #else:
            #empty += "x{}{} + ".format(i+1, j+1)
    #ans += "\n" + empty
    
cplex = "Minimize\n    {}\nSubject to".format(function)

cplex += ans

cplex += '\nBounds' + bounds + "\nEnd"
#print(cplex)
#f.write(cplex)
#f.close()
print("done")
        


