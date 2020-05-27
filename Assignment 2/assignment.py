
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


demandVolumes = [[40,30,20,10],[10,60,20,40],[20,20,20,20],[70,30,50,10]]


f = open("assignment.lp", "w")
bounds = ''
dvbounds = ''
ans = ''
function = 'r'

"""demand constraints"""
for i, ai in enumerate(a, 1):
    
    for j, cj in enumerate(c, 1):
        h = "h{}{}".format(i, j)        ## THIS NEEDS TO BE FOUND OUT/CHANGED      
        print(ai, cj)
        empty = '    dem{}{} : {} + {} = {}'.format(ai, cj, i, j, h)
        ans += "\n" + empty
        
        
"""capacity constraints"""

for s in a:
    for t in b:
        empty = '    cap{}{} : '.format(s, t)
        for dn, d in enumerate(c):
            if dn == len(c) -1:
                cCap = "c{}{}".format(s, t)              ## THIS NEEDS TO BE FOUND OUT/CHANGED
                bounds += '\n    {} >= 0'.format(cCap)
                empty += "x{}{}{} - {}r <= 0".format(s, t, d, cCap)
            else:
                empty += "x{}{}{} + ".format(s, t, d)
        ans += "\n" + empty
        
        
        
for d in c:
    for t in b:
        empty = '    cap{}{} : '.format(t, d)
        for sn, s in enumerate(a):
            if sn == len(a) -1:
                dCap = "d{}{}".format(t, d)              ## THIS NEEDS TO BE FOUND OUT/CHANGED  
                bounds += '\n    {} >= 0'.format(dCap)
                empty += "x{}{}{} - {}r <= 0".format(s, t, d, dCap)
            else:
                empty += "x{}{}{} + ".format(s, t, d)
            dvbounds += '\n    x{}{}{} >= 0'.format(s, t, d)
        ans += "\n" + empty

bounds += '\n    r >= 0'

#for k in c:
    #for j in b:
        ##print("cap{}{}".format(i, j))
        #empty = '    cap{}{} : '.format(j, k)
        #for i in range(len(a)):
            #if i == len(a) -1:
                #empty += "x{}{}{} - 100r <= 0".format(a[i], j, k)
            #else:
                #empty += "x{}{}{} + ".format(a[i], j, k)
            #bounds += '\n    x{}{}{} >= 0'.format(a[i], j, k)
        #ans += "\n" + empty
        
        
    #ans += "\n" + empty
    
    
cplex = "Minimize\n    {}\nSubject to".format(function)

cplex += ans

cplex += '\nBounds' + dvbounds + bounds + "\nEnd"
#print(cplex)
f.write(cplex)
f.close()
print("done")
        


