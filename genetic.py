#!/usr/bin/python
# coding: utf-8

from OpenGL.GLUT import *
import numpy
import math

try:
    from PIL import Image
except ImportError:
    import Image

import random

import drawimage

class triangle:
    def __init__(self):
        self.v = [random.random() for _ in range(6)]
        self.c = [random.random() for _ in range(4)]

def loadReference(name):
    global reference
    image = Image.open(name)
    reference = numpy.array(image.getdata(), dtype="int32")
    if reference.shape != (512*512, 3):
        print 'Reference image must be 512 x 512, RGB colours, no alpha channel'
        exit(1)
    
def evaluateNext():
    global imageQueue, imageDone, imageDifference
    global bestDifferences
    global generation, imagesDrawn
    if len(imageQueue) == 0:
        breedImages()

    image = imageQueue.pop()
    result = drawimage.drawImage(image).astype('int32')
    result.shape = (512*512, 3)
    diffimg = numpy.absolute(result - reference)
    difference = numpy.sum(diffimg)
    imageDone.append(image)
    imageDifference.append(difference)
    renderedImage.append(result)
    if generation > 0 and difference < min(bestDifferences):
        saveBestImages('generation-%08d' % generation, 1)
    imagesDrawn += 1

def initialImages():
    global imageQueue, imageDone, imageDifference, renderedImage
    global bestImages, bestDifferences, bestRendered
    global generation, imagesDrawn, startrate

    imageQueue = ([[triangle() for _ in range(1)] for _ in range(128)] +
                  [[triangle() for _ in range(2)] for _ in range(128)] +
                  [[triangle() for _ in range(3)] for _ in range(128)] +
                  [[triangle() for _ in range(4)] for _ in range(128)])

    for img in imageQueue:
        for tri in img:
            samplex = int(((tri.v[0] + tri.v[2] + tri.v[4]) / 3) * 512)
            sampley = int(((tri.v[1] + tri.v[3] + tri.v[5]) / 3) * 512)
            samplex = min(511, max(0, samplex))
            sampley = min(511, max(0, sampley))
            col = [val / 255.0 for val in reference[sampley * 512 + samplex]] + [1.0]
            tri.c = col

    imageDone = []
    imageDifference = []
    renderedImage = []

    bestImages = []
    bestDifferences = []
    bestRendered = []

    generation = 0
    imagesDrawn = 0
    startrate = 0

def breedImages():
    def mutation(image, chance):
        positions = range(len(image))
        while len(positions) > 10:
            positions.pop(random.randint(0, len(positions) - 1))

        outputs = [[tri for tri in image] for _ in positions]
        for pos in range(len(positions)):
            outputs[pos][positions[pos]] = triangle()
        return outputs

    def wigglePosition(image, rate):
        positions = range(len(image))
        while len(positions) > 10:
            positions.pop(random.randint(0, len(positions) - 1))

        outputs = [[tri for tri in image] for _ in positions]
        for pos in range(len(positions)):
            tri = image[positions[pos]]
            tri2 = triangle()
            tri2.v = [val + random.normalvariate(0, rate / 5) for val in tri.v]
            tri2.c = tri.c
            outputs[pos][positions[pos]] = tri2
        return outputs
        
    def wiggleColour(image, rate):
        positions = range(len(image))
        while len(positions) > 10:
            positions.pop(random.randint(0, len(positions) - 1))

        outputs = [[tri for tri in image] for _ in positions]
        for pos in range(len(positions)):
            tri = image[positions[pos]]
            tri2 = triangle()
            tri2.v = tri.v
            tri2.c = [val + random.normalvariate(0, rate / 3) for val in tri.c]
            outputs[pos][positions[pos]] = tri2
        return outputs
        
    def reorder(image):
        #outimage = []
        #pos = random.randint(1, len(image) - 2)
        #for tri in image[pos:]:
        #    outimage.append(tri)
        #for tri in image[:pos]:
        #    outimage.append(tri)
        outimage = [tri for tri in image]
        random.shuffle(outimage)
        return outimage

    def recombination(a, b, chance):
        outa = []
        outb = []
        for (tria, trib) in zip(a, b):
            if random.random() < chance:
                outa.append(trib)
                outb.append(tria)
            else:
                outa.append(tria)
                outb.append(trib)
        return (outa, outb)

    def addTriangle(image):
        positions = range(len(image) + 1)
        while len(positions) > 10:
            positions.pop(random.randint(0, len(positions) - 1))
        outputs = [[tri for tri in image] for _ in positions]
        tri = triangle()
        for pos in range(len(positions)):
            outputs[pos].insert(positions[pos], tri)
        return outputs

    def removeTriangle(image):
        positions = range(len(image))
        while len(positions) > 10:
            positions.pop(random.randint(0, len(positions) - 1))
        outputs = [[tri for tri in image] for _ in positions]
        for pos in range(len(positions)):
            outputs[pos].pop(positions[pos])
        return outputs

    global imageQueue, imageDone, imageDifference, renderedImage
    global bestImages, bestDifferences, bestRendered
    global generation, imagesDrawn, startrate

    indices = sorted([(val,index) for index,val in enumerate(imageDifference)])
    for _,pos in indices[:16]:
        bestImages.append(imageDone[pos])
        bestDifferences.append(imageDifference[pos])
        bestRendered.append(renderedImage[pos])

    bestIndices = sorted([(val,index) for index,val in enumerate(bestDifferences)])
    newBestImg = []
    newBestDiff = []
    newBestRendered = []
    for _,pos in bestIndices[:8]:
        newBestImg.append(bestImages[pos])
        newBestDiff.append(bestDifferences[pos])
        newBestRendered.append(bestRendered[pos])
    bestImages = newBestImg
    bestDifferences = newBestDiff
    bestRendered = newBestRendered
    
    if startrate == 0:
        startrate = min(bestDifferences)
    rate = float(min(bestDifferences)) / startrate * 0.9 + 0.05

    print 'Generation %4d, Best %8d, Rate %.2f, Images %d' % (generation, min(imageDifference), rate, imagesDrawn)
    generation += 1

    #decade = int(math.pow(10, math.floor(math.log10(generation))))
    #if generation >= 10 and generation % decade == 0:

    selectedImages = []
    tweaked = [val + random.random() * max(0.05, 1.0 - generation / 100.0) * min(bestDifferences) / 10 for val in imageDifference]
    indices = sorted([(val,index) for index,val in enumerate(tweaked)])
    for _,pos in indices[:16]:
        selectedImages.append(imageDone[pos])

    imageDone = []
    imageDifference = []
    renderedImage = []
    
    for img in selectedImages:
        imageQueue += mutation(img, rate)
    for img in selectedImages:
        if len(img) < 50:
            imageQueue += addTriangle(img)
    for img in selectedImages:
        if len(img) > 2:
            imageQueue += removeTriangle(img)

    for img in selectedImages:
        imageQueue.append(reorder(img))
    for img in selectedImages:
        imageQueue += wigglePosition(img, rate)
    for img in selectedImages:
        imageQueue += wiggleColour(img, rate)

    for pos in range(len(selectedImages)):
        posa = random.randint(0, len(selectedImages) - 1)
        posb = random.randint(0, len(selectedImages) - 2)
        if posb >= posa:
            posb += 1
        imga = selectedImages[posa]
        imgb = selectedImages[posb]
        (outa, outb) = recombination(imga, imgb, rate * 0.5)
        imageQueue.append(outa)
        imageQueue.append(outb)
        
def saveFinalImages():
    saveBestImages('final', 8)

def saveBestImages(prefix, count):
    global bestRendered, bestDifferences

    indices = sorted([(val,index) for index,val in enumerate(bestDifferences)])
    for num,(_,pos) in enumerate(indices[:count]):
        img = bestRendered[pos]
        img.shape = (512, 512, 3)
        outimg = Image.fromarray(img.astype('uint8'))
        outimg.save('%s-%02d.png' % (prefix, num))

if __name__ == '__main__':
    loadReference('mato.png')
    initialImages()
    drawimage.init()
    glutIdleFunc(evaluateNext)
    glutCloseFunc(saveFinalImages)
    glutMainLoop()
