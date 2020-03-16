import sys

def readconf():
    print("\n******trying to open file******\n")
    file = open("./Config/" + sys.argv[1], "r")

    configs = file.readlines()



    for x in configs:
        print(x)
    print("********************************\n")


    for i in range(len(configs)):
        configs[i] = configs[i].rstrip()
        #print(configs[i])
        if configs[i].startswith("router-id:"):
            router_id = get_inputs(configs[i])
            #print(router_id)
        elif configs[i].startswith("input-ports:"):
            input_ports = get_inputs(configs[i])
            #print(input_ports)
        elif configs[i].startswith("outputs:"):
            output_ports = get_inputs(configs[i], 1)
            #print(output_ports)
        elif configs[i].startswith("update:"):
            update_line = get_inputs(configs[i])
            #print(update_line)
    
        

def get_inputs(line, output=0):           #set output to 1 for the outputs config line
    inputs = line.split(' ')[1:]
    
    for i in range(len(inputs)):
        inputs[i] = inputs[i].strip(",")
        
        if output == 1:                                
            inputs[i] = get_output_input(inputs[i])
        else:
            inputs[i] = int(inputs[i])
        
    return inputs
    
def get_output_input(data):
    data = data.split('-')
    
    for i in range(len(data)):
        data[i] = int(data[i])
        
    return tuple(data)
    


def main():
    print("starting rip")

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    readconf()
    

if __name__ == "__main__":
    main()