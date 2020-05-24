import numpy as np
import subprocess
import csv

with open("final.csv", "w", newline='') as final:
    thewriter = csv.writer(final)
    

    for h in np.arange(1.0, 19.0, 0.1):
        h = round(h, 1)
        filename = "{}.lp".format(h)
        #print(filename)
        f = open(filename, "w")
        cplex = """Minimize
    10 x12 + 5 x132
Subject to
    demand flow : x12 + x132 = {}
    capp1 :      x12 <= 10
    capp2 :      x132 <= 10
Bounds
    0 <= x12
    0 <= x132
End""".format(h)
        f.write(cplex)
        f.close()
        
        com1 = "read {}".format(filename)    
        result = subprocess.check_output('cplex -c "{}" "optimize" "display solution variables -"'.format(com1), shell=True)
        lines = str(result.decode('utf-8')).split("\n")    
        value = 0
        #print(lines)
        for i in range(len(lines)-2, 0, -1):
            
            ok = lines[i].split()
            #print(ok[0])
            if ok[0] == 'x12':
                value = ok[1]
                break
            if ok[0] == 'CPLEX>':
                break
            
        thewriter.writerow([h, value])    
    #final.write(("{},{}\n".format(h,value)))
#final.close()


