import sys
import signal
import pickle
import urllib2
import argparse
from BeautifulSoup import BeautifulSoup


# Arguments logic
parser = argparse.ArgumentParser(description='Web crawler')
parser.add_argument('website', nargs='?', action='store', help='website to crawl')
parser.add_argument('-l', action='store', default=2, help='maximum depth level to crawl')
parser.add_argument('-resume', action='store_const', const=32, help='resume crawler')

crawler_state = None    # save Crawler class
interrupted = False     # Stop while

def signal_handler(signal, frame):
    """
    Capture Ctrl+C
    """
    global crawler_state
    global interrupted
    
    print "Saving state Ctrl+C"
    interrupted = True
    
    #Serialize
    dumped = pickle.dumps(crawler_state)
    savefile('state.data', dumped)
    sys.exit(0)
    

    
class Crawler(object):
    
    def __init__(self, url, depth):
        self.maxdepth = depth
        self.url = url
        self.visited = []
        self.queue = [(self.url, 0)]
        self.output = ""
        self.current_url = ""
        self.level = None
   
    def crawl(self, depth = 0):
        """
        keyword arguments:
        current_url -- 
        """
        global interrupted
        
        while len(self.queue) > 0:
            if interrupted:
                break
            
            self.current_url, self.level = self.queue.pop()
            
            if self.level > self.maxdepth - 1:
                continue            
            
            page = Fetch(self.current_url)
            urls = page.fetch()
            self.output += " " * self.level + self.current_url + "\n"
            # Interactive purpose
            print " " * self.level + self.current_url
            
            for url in urls:
                if url not in self.visited:                    
                    self.queue.append((url, self.level + 1))
                    self.visited.append(url)
                    
        # wrap = {}
        # wrap[self.url] = output
        return self.output

class Fetch(object):
    
    def __init__(self, url):
        self.url = url
    
    def fetch(self):
        #print "fetch %s..." % (self.url)
        request = urllib2.Request(self.url)
        try:
            response = urllib2.urlopen(request)
        except:
            return []
        document = response.read()

        #normaliza o documento para que o mesmo seja acessivel via objetos
        soup = BeautifulSoup(document)

        # retorna uma lista com todos os links do documento
        links = soup.findAll('a')  

        
        output = []
        for link in links:            
            try:
                raw_link = link['href']
                if ("http://" in raw_link or "https://" in raw_link) and raw_link.startswith("http"):
                    output.append( raw_link )
            except:                
                pass
            
        return output

# --------------------------------------------        
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
# --------------------------------------------
    
def main():
    
    global crawler_state
    
    # Arguments parser
    args = parser.parse_args()
    
    # Crawler
    c = Crawler(args.website, int(args.l))
    crawler_state = c
    
    # Register Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    if not args.resume:
        info = c.crawl(args.website)
    else:
        #recover state
        print "recovering..."
        raw = loadfile('state.data')
        data = pickle.loads(raw)
        c.output = data.output
        
        c.queue = data.queue        
        c.queue.append((data.current_url, data.level))
        
        c.visited = data.visited
        c.url = data.url
        c.maxdepth = data.maxdepth
        info = c.crawl(data.url)
        print "OK"
        
    
    # Save data
    savefile('structure.txt', info)
    

if __name__ == "__main__":
    main()
        