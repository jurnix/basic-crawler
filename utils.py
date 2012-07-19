

#               IO operations

def savefile(filename, data):
    f = open(filename, 'w')
    f.write(data)
    f.close()
    
def loadfile(filename):
    f = open(filename, 'r')
    output = f.read()
    f.close()
    return output
