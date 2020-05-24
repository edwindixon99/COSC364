import numpy as np
import subprocess
import csv

    
a = [3, 4, 5]
b = [2, 4, 6]
c = 1 


f = open("4.1.3.lp", "w")
bounds = ''
ans = ''
function = ''
for i in range(len(a)):
    empty = '    a{} : '.format(i+1)
    
    for j in range(len(b)):
        
        if j == len(b) -1:
            if i == len(a) -1:
                function += "x{}{}".format(i+1, j+1)
            empty += "x{}{} = {}".format(i+1, j+1, a[i])
            
        else:
            empty += "x{}{} + ".format(i+1, j+1)
            function += "x{}{} + ".format(i+1, j+1)
        bounds += '\n    x{}{} >= 0'.format(i+1, j+1)
        
    ans += "\n" + empty
    
for j in range(len(b)):
    empty = '    b{} : '.format(j+1)
    
    for i in range(len(a)):

        if i == len(a) -1:
            empty += "x{}{} = {}".format(i+1, j+1, b[j])
        else:
            empty += "x{}{} + ".format(i+1, j+1)
    ans += "\n" + empty
    
cplex = "Minimize\n    {}\nSubject to".format(function)

cplex += ans

cplex += '\nBounds' + bounds + "\nEnd"

f.write(cplex)
f.close()
        


