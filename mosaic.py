import threading, os, sys, Image, time, random, traceback, commands, glob
import numpy as np
import scipy.misc as spm
import scipy.ndimage.interpolation as spi

DO_GREYSCALE = False
DO_GREYSCALE_MATCH = False
TRANSPARENCY = 0.3
CIRCLE_DIV = 36
TILE_LONG_SIDE = 55

class A:
    pass


if len(sys.argv) < 3:
    print 'Usage: %s reproduce_image image_lib_dir1 [image_lib_dir2...]'
    sys.exit()
    
reproImage = spm.imread(sys.argv[1])

libFiles = []
for direc in sys.argv[2:]:
    libFiles.extend(glob.glob('%s/*jpg'%direc))
    libFiles.extend(glob.glob('%s/*JPG'%direc))

MAX_IMAGES = 2000
while len(libFiles) > MAX_IMAGES:
    del libFiles[random.randint(0, len(libFiles) - 1)]


NUM_ADJUST_CHECKS = 20
TILE_MOVE = 3

libImages = {}


# add a tile-ized version of the given image file to our image library,
# and all rotations of it as well:
def addToLib(imLib, fName):
    startImage = spm.imread(fName)
    if len(startImage.shape) < 3:
        return -1
    longLen = max(startImage.shape)

    if longLen > TILE_LONG_SIDE:
        newX = int(startImage.shape[0] * TILE_LONG_SIDE / longLen)
        newY = int(startImage.shape[1] * TILE_LONG_SIDE / longLen)
        startImage = spm.imresize(startImage, (newX, newY))

    imLib[fName] = []
    
    for i in range(CIRCLE_DIV):
        pixTile = spi.rotate(startImage, 360.0 * i / CIRCLE_DIV)
        newIm = A()
        newIm.im = pixTile
        if i == 5: spm.imsave('tmp.jpg', pixTile)
        
        newIm.mask = np.sum(pixTile**2, axis=2) > 0.0
        imLib[fName].append(newIm)

    return 1

            

# this function determines if the given tile at the given position
# makes the image any better:
def makesImageBetter(repImage, compImage, newTile, pos):

    nX = newTile.im.shape[0]
    nY = newTile.im.shape[1]
    repPiece = repImage[pos[0]:pos[0] + nX, pos[1]:pos[1] + nY]
    composPiece = compImage[pos[0]:pos[0] + nX, pos[1]:pos[1] + nY]
    #print ewTile.im.shape, composPiece.shape
    newCompPiece = TRANSPARENCY * composPiece + (1.0 - TRANSPARENCY) * newTile.im[:, :, :3]

    
    if DO_GREYSCALE_MATCH:
        greyCompos = 0.3 * composPiece[:, :, 0] + 0.59 * composPiece[:, :, 1] + 0.11 * composPiece[:, :, 2]
        greyRep = 0.3 * repPiece[:, :, 0] + 0.59 * repPiece[:, :, 1] + 0.11 * repPiece[:, :, 2]
        greyNewComp = 0.3 * newCompPiece[:, :, 0] + 0.59 * newCompPiece[:, :, 1] + 0.11 * newCompPiece[:, :, 2]
        oldMatch = np.sum(np.sqrt((np.where(newTile.mask, greyCompos - greyRep)**2, 0.0)))
        newMatch = np.sum(np.sqrt((np.where(newTile.mask, greyNewComp - greyRep)**2, 0.0)))        
    else:
        oldMatch = np.sum(np.sqrt(np.where(newTile.mask[:, :, np.newaxis], (composPiece - repPiece)**2, 0.0)))
        newMatch = np.sum(np.sqrt(np.where(newTile.mask[:, :, np.newaxis], (newCompPiece - repPiece)**2, 0.0)))        

    return oldMatch - newMatch

# this function pastes a tile into the composite image in a specified location:
def pasteIn(compImage, newTile, pos, mask=np.array([[1.0]])):

    nX = newTile.shape[0]
    nY = newTile.shape[1]

    composPiece = compImage[pos[0]:pos[0] + nX, pos[1]:pos[1] + nY]
    newCompPiece = TRANSPARENCY * composPiece + (1.0 - TRANSPARENCY) * newTile[:, :, :3]
    
    if DO_GREYSCALE:
        greyNewComp = 0.3 * newCompPiece[:, :, 0] + 0.59 * newCompPiece[:, :, 1] + 0.11 * newCompPiece[:, :, 2]
        compImage[pos[0]:pos[0]+nX, pos[1]:pos[1]+nY] = np.where(mask, greyNewComp, composPiece)        
    else:
        compImage[pos[0]:pos[0]+nX, pos[1]:pos[1]+nY] = np.where(mask[:, :, np.newaxis], newCompPiece, composPiece)
        

compositeImage = np.zeros(reproImage.shape)
dispImage = np.zeros((reproImage.shape[0]*2, reproImage.shape[1], 3))

pasteIn(dispImage, reproImage, [0,0])


libImList = libImages.keys()
lastSaveTime = -1.0

planFl = open('plan.txt', 'w')

temp = -1.0
TIME_PER_TEMP = 3600.0 / 30.0
TEMP_MULT = 0.9

TILE_TRIALS = 1000
startTempTime = time.time()

while True:
    # pick a random image from the library, and see if we need to add it to the
    # scaled images list:

    randFile = libFiles[random.randint(0, len(libFiles) - 1)]
    if not libImages.has_key(randFile):
        print 'adding', randFile, 'to library, loaded', len(libImList), 'of', len(libFiles)
        try:
            res = addToLib(libImages, randFile)
            if res < 0:
                print 'skipping'
                continue
        except:
            print traceback.format_exc()
            continue        
        libImList = libImages.keys()

    tileInd = random.randint(0, len(libImages[randFile]) - 1)
    randTile = libImages[randFile][tileInd]
    print randFile

    bestTileImprove = -1.0E12
    bestTilePos = None
    bestTile = None
    bestInd = 0
    for i in range(TILE_TRIALS):
        #print 'tile:', randFile, 'i:', i
        # pick a random location for the tile:
        Ntx = reproImage.shape[0] / randTile.im.shape[0]
        Nty = reproImage.shape[1] / randTile.im.shape[1]        
        tileX = random.randint(0, Ntx - 1) * randTile.im.shape[0] #reproImage.shape[0] - 1 - randTile.im.shape[0])
        tileY = random.randint(0, Nty - 1) * randTile.im.shape[1]
        #tileY = random.randint(0, reproImage.shape[1] - 1 - randTile.im.shape[1])

        improvement = -1.0E13
        try:
            improvement = makesImageBetter(reproImage, compositeImage, randTile, (tileX, tileY))
        except:
            traceback.print_exc()
            pass
        #print 'improvement:', improvement, 'best tile improve:', bestTileImprove
        if temp < 0.0:
            temp = abs(improvement)
            #print 'setting initial temp to', temp

        if time.time() - startTempTime > TIME_PER_TEMP:
            temp *= TEMP_MULT
            #print 'lowering temp to', temp
            startTempTime = time.time()

        if improvement > bestTileImprove:

            print 'tile good, improvement = %f, adjusting...'%(improvement)
            newInd = tileInd
            newPos = (tileX, tileY)
            newTile = randTile
            bestImprove = improvement
            for i in range(NUM_ADJUST_CHECKS):
                trialInd = (newInd + random.randint(-1, 1)) % len(libImages[randFile])
                trialPos = [0, 0]
                trialTile = libImages[randFile][trialInd]
                trialPos[0] = (newPos[0] + random.randint(-TILE_MOVE, TILE_MOVE)) % (reproImage.shape[0] - trialTile.im.shape[0])
                trialPos[1] = (newPos[1] + random.randint(-TILE_MOVE, TILE_MOVE)) % (reproImage.shape[1] - trialTile.im.shape[1])
                trialImprove = makesImageBetter(reproImage, compositeImage, trialTile, trialPos)
                if trialImprove > bestImprove:
                    bestImprove = trialImprove
                    newInd = trialInd
                    newPos = trialPos
                    newTile = trialTile
                    #print 'found better tile pos by adjustment, i = %d, improvement: %f'%(i, trialImprove)
        
            if bestImprove > bestTileImprove:
                #print 'best improvement now', bestImprove
                bestTileImprove = bestImprove
                bestTilePos = newPos
                bestTile = newTile
                bestInd = newInd
                
        
    if bestTile != None and bestImprove > 0:
        pasteIn(compositeImage, bestTile.im, bestTilePos, bestTile.mask)
        print 'pasting in', randFile
        try:
            print bestTilePos
            planFl.write('adding tile %s at position %d %d angle num %d\n'%(randFile, bestTilePos[0], bestTilePos[1], bestInd))
        except:
            traceback.print_exc()
            print 'problem pasting'
            continue
    planFl.flush()
    timeNow = time.time()
    if timeNow - lastSaveTime > 20.0:
        print 'saving...'
        spm.imsave('result.jpg', compositeImage)
        lastSaveTime = timeNow
    pasteIn(dispImage, compositeImage, [reproImage.shape[0], 0])
