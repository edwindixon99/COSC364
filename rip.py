import sys

def readconf():
    print("\n******trying to open file******\n")
    file = open("./Config/" + sys.argv[1], "r")

    configs = file.readlines()

    for x in configs:
        print(x)
    print("********************************\n")


def main():
    print("starting rip")

    if (len(sys.argv) < 2):
        print("no config file")
        sys.exit()

    readconf()
    

if __name__ == "__main__":
    main()