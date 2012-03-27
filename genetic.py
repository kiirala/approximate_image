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
    
def evaluateNext():
    global imageQueue, imageDone, imageDifference
    if len(imageQueue) == 0:
        breedImages()

    image = imageQueue.pop()
    result = drawimage.drawImage(image)
    result.shape = (512*512, 3)
    diffimg = numpy.fabs(result - reference)
    difference = numpy.sum(diffimg)
    imageDone.append(image)
    imageDifference.append(difference)
    print 'Difference was', difference, '(best', min(imageDifference), ')'

def initialImages():
    global imageQueue, imageDone, imageDifference
    imageQueue = [[triangle() for _ in range(50)] for _ in range(32)]
    imageDone = []
    imageDifference = []

def breedImages():
    def mutation(image, chance):
        outimage = []
        for tri in image:
            if random.random() < chance:
                outimage.append(triangle())
            else:
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

    global imageQueue, imageDone, imageDifference
    for i in range(len(imageDone) - 16):
        pos = imageDifference.index(max(imageDifference))
        imageDone.pop(pos)
        imageDifference.pop(pos)
    for img in imageDone:
        imageQueue.append(mutation(img, 0.3))

    for pos in range(len(imageDone)):
        posa = random.randint(0, len(imageDone) - 1)
        posb = random.randint(0, len(imageDone) - 2)
        if posb >= posa:
            posb += 1
        imga = imageDone[posa]
        imgb = imageDone[posb]
        (outa, outb) = recombination(imga, imgb, 0.3)
        imageQueue.append(outa)
        imageQueue.append(outb)
        

if __name__ == '__main__':
    loadReference('soundbox-proto.png')
    initialImages()
    drawimage.init()
    glutIdleFunc(evaluateNext)
    glutMainLoop()

