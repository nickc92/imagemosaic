import sys, Image
from math import *

ORIG_MAX_SIZE = 55
CIRCLE_DIV = 36.0
TRANSPARENCY = 0.3
OUTFILE = 'render.jpg'

if len(sys.argv) != 4:
    print 'Usage:', sys.argv[0], 'targetImage planfile scale'
    sys.exit()
    
reproIm = Image.open(sys.argv[1])
planF = open(sys.argv[2])
scale = float(sys.argv[3])

newMaxSize = ORIG_MAX_SIZE * scale

origSize = reproIm.size
newSize = (int(origSize[0] * scale), int(origSize[1] * scale))

newImage = Image.new('RGB', newSize)
pixNewImage = newImage.load()

cnt = 0
for ln in planF:
    if ln.find('adding') < 0: continue
    cnt += 1
    print cnt
    pcs = ln.split()
    
    print 'adding ', pcs[2]
    rot = int(pcs[-1])
    pasteY = int(scale * int(pcs[5]))
    pasteX = int(scale * int(pcs[6]))

    im = Image.open(pcs[2])
    longLen = max(im.size)
    if longLen > newMaxSize:
        newX = int(im.size[0] * newMaxSize / longLen)
        newY = int(im.size[1] * newMaxSize / longLen)
        im = im.resize((newX, newY), Image.BICUBIC)

    im = im.rotate(360.0 * rot / CIRCLE_DIV, Image.BICUBIC, True)
    pixIm = im.load()

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            pt = pixIm[i, j]
            if pt[0] != 0 or pt[1] != 0 or pt[2] != 0:
                try:
                    pt2 = pixNewImage[i + pasteX, j + pasteY]
                    newpt = (int(TRANSPARENCY * pt2[0] + (1.0 - TRANSPARENCY) * pt[0]), int(TRANSPARENCY * pt2[1] + (1.0 - TRANSPARENCY) * pt[1]), int(TRANSPARENCY * pt2[2] + (1.0 - TRANSPARENCY) * pt[2]))
                    pixNewImage[i + pasteX, j + pasteY] = newpt
                except:
                    print i + pasteX, j + pasteY, newImage.size
    
    if cnt % 200 == 0:
        newImage.save(OUTFILE)
newImage.save(OUTFILE)
