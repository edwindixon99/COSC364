import numpy as np
import subprocess
import csv

    
a = ['A', 'B', 'C', 'D']
b = ['X', 'Y', 'Z']
c = [1, 2, 3, 4]

demandVolumes = [[40,30,20,10],[10,60,20,40],[20,20,20,20],[70,30,50,10]]


f = open("7.4.1.lp", "w")
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
f.write(cplex)
f.close()
        


