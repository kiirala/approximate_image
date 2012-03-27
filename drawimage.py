#!/usr/bin/python
# coding: utf-8

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
import random

resolution = (512, 512)

def display():
    global image

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glEnable(GL_BLEND)
    glBlendEquation(GL_FUNC_ADD)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glLoadIdentity()

    glBegin(GL_TRIANGLES)
    for triangle in image:
        glColor(triangle.c[0], triangle.c[1], triangle.c[2], triangle.c[3])
        glVertex(triangle.v[0], triangle.v[1], 0)
        glVertex(triangle.v[2], triangle.v[3], 0)
        glVertex(triangle.v[4], triangle.v[5], 0)
    glEnd()

    glutSwapBuffers()

def reshape(width, height):
    global resolution
    resolution = (width, height)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)

def keyPress(asc, xpos, ypos):
    #print "'%s' 0x%2x %3d" % (asc, ord(asc), ord(asc))
    if asc == '\x1b':
        glutLeaveMainLoop()

class triangle:
    def __init__(self):
        self.v = [random.random() for _ in range(6)]
        self.c = [random.random() for _ in range(4)]

def init():
    global resolution
    glutInit([])
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowSize(resolution[0], resolution[1])

    #glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Image viewer")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    #glutMotionFunc(mouseMotion)
    #glutMouseFunc(mouseClick)
    glutKeyboardFunc(keyPress)
    #glutSpecialFunc(specialPress)

    for name in (GL_VENDOR,GL_RENDERER,GL_VERSION,GL_SHADING_LANGUAGE_VERSION):
        print name,glGetString(name)

    reshape(resolution[0], resolution[1])

def drawImage(img):
    global image, resolution
    image = img
    display()
    glFinish()
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixelsub(0, 0, resolution[0], resolution[1], GL_RGB)
    return data
    
if __name__ == "__main__":
    init()

    image = [triangle() for _ in range(50)]

    glutMainLoop()
