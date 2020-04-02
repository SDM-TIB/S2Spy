# -*- coding: utf-8 -*-
import os

def openFile(fileName):
    path = os.getcwd()
    return open(path + "/output/" + fileName, "w")

def closeFile(file):
    file.close()
