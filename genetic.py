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
    reference = numpy.array(image.getdata())
    if reference.shape != (512*512, 3):
        print 'Reference image must be 512 x 512, RGB colours, no alpha channel'
        exit(1)
    
def evaluateNext():
    global imageQueue, imageDone, imageDifference
    global generation, imagesDrawn
    if len(imageQueue) == 0:
        breedImages()

    image = imageQueue.pop()
    result = drawimage.drawImage(image)
    result.shape = (512*512, 3)
    diffimg = numpy.fabs(result - reference)
    difference = numpy.sum(diffimg)
    imageDone.append(image)
    imageDifference.append(difference)
    renderedImage.append(result)
    imagesDrawn += 1

def initialImages():
    global imageQueue, imageDone, imageDifference, renderedImage
    global generation, imagesDrawn
    imageQueue = [[triangle() for _ in range(50)] for _ in range(32)]
    imageDone = []
    imageDifference = []
    renderedImage = []
    generation = 0
    imagesDrawn = 0

def breedImages():
    def mutation(image, chance):
        outimage = []
        for tri in image:
            if random.random() < chance:
                outimage.append(triangle())
            else:
                outimage.append(tri)
        return outimage

    def wiggle(image, rate):
        outimage = []
        for tri in image:
            if random.random() < rate:
                tri2 = triangle()
                tri2.v = [val + random.random() * 0.04 - 0.02 for val in tri.v]
                tri2.c = [val + random.random() * 0.04 - 0.02 for val in tri.c]
                outimage.append(tri2)
            else:
                outimage.append(tri)
        return outimage
        
    def reorder(image):
        outimage = []
        pos = random.randint(1, len(image) - 2)
        for tri in image[pos:]:
            outimage.append(tri)
        for tri in image[:pos]:
            outimage.append(tri)
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

    global imageQueue, imageDone, imageDifference, renderedImage
    global generation, imagesDrawn

    rate = min(imageDifference) / (512*512*3*80)

    print 'Generation', generation, 'Images drawn', imagesDrawn, 'best', min(imageDifference), 'rate', rate
    generation += 1

    decade = int(math.pow(10, math.floor(math.log10(generation))))
    if generation >= 10 and generation % decade == 0:
        saveBestImages('generation-%08d' % generation, 1)

    for i in range(len(imageDone) - 16):
        pos = imageDifference.index(max(imageDifference))
        imageDone.pop(pos)
        imageDifference.pop(pos)
        renderedImage.pop(pos)

    for img in imageDone:
        imageQueue.append(mutation(img, rate))

    for img in imageDone:
        imageQueue.append(reorder(img))

    for img in imageDone:
        imageQueue.append(wiggle(img, rate))

    for pos in range(len(imageDone) / 2):
        posa = random.randint(0, len(imageDone) - 1)
        posb = random.randint(0, len(imageDone) - 2)
        if posb >= posa:
            posb += 1
        imga = imageDone[posa]
        imgb = imageDone[posb]
        (outa, outb) = recombination(imga, imgb, rate * 0.5)
        imageQueue.append(outa)
        imageQueue.append(outb)
        
def saveFinalImages():
    saveBestImages('final', 8)

def saveBestImages(prefix, count):
    global renderedImage, imageDifference

    indices = sorted([(val,index) for index,val in enumerate(imageDifference)])
    for num in range(count):
        pos = indices[num][1]
        img = renderedImage[pos]
        img.shape = (512, 512, 3)
        outimg = Image.fromarray(img)
        outimg.save('%s-%02d.png' % (prefix, num))

if __name__ == '__main__':
    loadReference('mato.png')
    initialImages()
    drawimage.init()
    glutIdleFunc(evaluateNext)
    glutCloseFunc(saveFinalImages)
    glutMainLoop()
