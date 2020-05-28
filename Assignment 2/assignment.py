
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
ans = ''
ans2 = ''
function = 'r'
new = ''

"""demand constraints"""

"""for loop is responsible for:
   demS1D1 : xS1T1D1 + xS1T2D1 = 2
   capS1T1D1 : xS1T1D1 - 1.0 uS1T1D1 = 0
   capS1D1 : uS1T1D1 + uS1T2D1 = 2
"""
for i, ai in enumerate(a, 1):
    
    for j, cj in enumerate(c, 1):
        h = i + j 
        empty = '    dem{}{} : '.format(ai, cj)
        empty2 = '    cap{}{} : '.format(ai, cj)
        for kn, k in enumerate(b):
            if kn == len(b) -1:
                empty2 += "u{}{}{} = 2".format(ai, k, cj)
                empty += "x{}{}{} = {}".format(ai, k, cj, h)
            else:
                empty2 += "u{}{}{} + ".format(ai, k, cj) 
                empty += "x{}{}{} + ".format(ai, k, cj)
            new += '\n    cap{0}{1}{2} : x{0}{1}{2} - {3} u{0}{1}{2} = 0'.format(ai, k, cj, h/2)
        ans2 += "\n" + empty2
        ans += "\n" + empty
        
"""for loop is responsible for:
   capS1T1 : xS1T1D1 + xS1T1D2 - cS1T1r <= 0
"""


for i, s in enumerate(a, 1):
    for j, t in enumerate(b, 1):
        empty = '    cap{}{} : '.format(s, t)
        for dn, d in enumerate(c):
            if dn == len(c) -1:
                cCap = "c{}{}r".format(s, t)              ## THIS NEEDS TO BE FOUND OUT/CHANGED
                bounds += '\n    {} >= 0'.format(cCap)
                empty += "x{}{}{} - {} <= 0".format(s, t, d, cCap)
            else:
                empty += "x{}{}{} + ".format(s, t, d)
        ans += "\n" + empty

"""for loop is responsible for:
   capT1D1 : xS1T1D1 + xS2T1D1 - dT1D1r <= 0
   xS1T1D1 >= 0
   uS1T1D1
   
"""
for i, d in enumerate(c, 1):
    for j, t in enumerate(b, 1):
        empty = '    cap{}{} : '.format(t, d)
        for sn, s in enumerate(a):
            if sn == len(a) -1:
                dCap = "d{}{}r".format(t, d)              ## THIS NEEDS TO BE FOUND OUT/CHANGED  
                bounds += '\n    {} >= 0'.format(dCap)
                empty += "x{}{}{} - {} <= 0".format(s, t, d, dCap)
            else:
                empty += "x{}{}{} + ".format(s, t, d)
            xbounds += '\n    x{}{}{} >= 0'.format(s, t, d)
            ubounds += '\n    u{}{}{}'.format(s, t, d)
        ans += "\n" + empty
        
        
"""for loop is responsible for:
   loadT1 : xS1T1D1 + xS1T1D2 + xS2T1D1 + xS2T1D2 = lT1
"""
for k in b:
    empty = '    load{} : '.format(k)
    counter = 0
    for i in a:
        for j in c:
            if counter == len(a) * len(c) -1:
                empty += "x{0}{1}{2} - l{1} = 0".format(i, k, j)
            else:
                empty += "x{}{}{} + ".format(i, k, j)   
            counter += 1
    ans += "\n" + empty

bounds += '\n    r >= 0'

    
cplex = "Minimize\n    {}\nSubject to".format(function)
cplex +=  ans + ans2 + new
cplex += '\nBounds' + xbounds + bounds
cplex += "\nInteger" + ubounds

cplex += "\nEnd"
f.write(cplex)
f.close()
print("done")
        


