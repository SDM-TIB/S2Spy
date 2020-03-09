# -*- coding: utf-8 -*-
import os

def openFile(fileName):
    path = os.getcwd()
    return open(path + "/output/" + fileName, "a")

def closeFile(file):
    file.close()
