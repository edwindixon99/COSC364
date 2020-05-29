
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
print()





a = []
i_ = 0
while i_ < int(source_nodes):
    a.append("S"+str(i_+1))
    i_ += 1
print(a)

b = []
ii = 0
while ii < int(transit_nodes):
    b.append("T"+str(ii+1))
    ii += 1
print(b)

c = []
iii = 0
while iii < int(destination_nodes):
    c.append("D"+str(iii+1))
    iii += 1
print(c)



f = open("assignment.lp", "w")
bounds = ''
xbounds = ''
ubounds = ''
constraints = ''
constraints2 = ''
obj_function = 'r'
new = ''

"""demand constraints"""

"""for loop is responsible for:
   demSiDj : xSiTkDj + xSiT2Dj = i + j
   capSiTkDj : xSiTkDj - (i + j)/2 uSiTkDj = 0
   capSiDj : uSiTkDj + uSiT2Dj = nk
"""
for i, ai in enumerate(a, 1):
    
    for j, cj in enumerate(c, 1):
        h = i + j 
        constraint = '    dem{}{} : '.format(ai, cj)
        constraint2 = '    cap{}{} : '.format(ai, cj)
        for kn, k in enumerate(b):
            if kn == len(b) -1:
                constraint2 += "u{}{}{} = 2".format(ai, k, cj)
                constraint += "x{}{}{} = {}".format(ai, k, cj, h)
            else:
                constraint2 += "u{}{}{} + ".format(ai, k, cj) 
                constraint += "x{}{}{} + ".format(ai, k, cj)
            new += '\n    cap{0}{1}{2} : x{0}{1}{2} - {3} u{0}{1}{2} = 0'.format(ai, k, cj, h/2)
        constraints2 += "\n" + constraint2
        constraints += "\n" + constraint
        
"""for loop is responsible for:
   capSiTk : xSiTkDj + xSiTkDj - cSiTkr <= 0
"""


for i, s in enumerate(a, 1):
    for j, t in enumerate(b, 1):
        constraint = '    cap{}{} : '.format(s, t)
        for dn, d in enumerate(c):
            if dn == len(c) -1:
                cCap = "c{}{}".format(s, t)              
                bounds += '\n    {} >= 0'.format(cCap)
                constraint += "x{}{}{} - {} <= 0".format(s, t, d, cCap)
            else:
                constraint += "x{}{}{} + ".format(s, t, d)
        constraints += "\n" + constraint

"""for loop is responsible for:
   capTkDj : xS1T1D1 + xS2T1D1 - dT1D1r <= 0
   xSiTkDj >= 0
   uSiTkDj
   
"""
for i, d in enumerate(c, 1):
    for j, t in enumerate(b, 1):
        constraint = '    cap{}{} : '.format(t, d)
        for sn, s in enumerate(a):
            if sn == len(a) -1:
                dCap = "d{}{}".format(t, d)              
                bounds += '\n    {} >= 0'.format(dCap)
                constraint += "x{}{}{} - {} <= 0".format(s, t, d, dCap)
            else:
                constraint += "x{}{}{} + ".format(s, t, d)
            xbounds += '\n    x{}{}{} >= 0'.format(s, t, d)
            ubounds += '\n    u{}{}{}'.format(s, t, d)
        constraints += "\n" + constraint
        
        
"""for loop is responsible for:
   loadT1 : xS1T1D1 + xS1T1D2 + xS2T1D1 + xS2T1D2 = lT1
   loadBalT1 : lT1 - r <= 0
"""
for k in b:
    constraint = '    load{} : '.format(k)
    constraint2 = '    loadBal{} : '.format(k)
    counter = 0
    for i in a:
        for j in c:
            if counter == len(a) * len(c) -1:
                constraint += "x{0}{1}{2} - l{1} = 0".format(i, k, j)
                constraint2 += "l{0} - r <= 0".format(k)
            else:
                constraint += "x{}{}{} + ".format(i, k, j)   
            counter += 1
    constraints += "\n" + constraint
    constraints2 += "\n" + constraint2

bounds += '\n    r >= 0'

    
cplex = "Minimize\n    {}\nSubject to".format(obj_function)
cplex +=  constraints + constraints2 + new
cplex += '\nBounds' + xbounds + bounds
cplex += "\nInteger" + ubounds

cplex += "\nEnd"
f.write(cplex)
f.close()
print("done")
        


