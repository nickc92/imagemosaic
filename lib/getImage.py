import urllib2
import json
import cStringIO
import Image, commands

def getImg(searchTerm):
    fetcher = urllib2.build_opener()
    startIndex = 0
    searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + searchTerm + "&start=" + str(startIndex)
    f = fetcher.open(searchUrl)
    deserialized_output = json.load(f)
    imageUrl = deserialized_output['responseData']['results'][0]['unescapedUrl']
    print 'got google result for', searchTerm
    file = cStringIO.StringIO(urllib2.urlopen(imageUrl, None, 10.0).read())
    fname = imageUrl.split('/')[-1]
    print fname
    fl = open('tmp.jpg', 'w')
    fl.write(file.read())
    fl.close()
    commands.getoutput('convert -geometry 640x480 tmp.jpg %s.jpg'%(searchTerm))
    
    
for ln in open('nouns.txt'):
    term = ln.strip()
    try:
        print term
        getImg(term)
    except: continue
