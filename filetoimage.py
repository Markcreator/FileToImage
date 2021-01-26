# Made by Markcreator

import sys
from PIL import Image
import math
import PySimpleGUI as sg
import os

inputfile_list_column = [
    [
        sg.Text("Input File"),
        sg.In(size=(25, 1), enable_events=False, key="-INPUTFILE-"),
        sg.FilesBrowse(),
    ]
]

outputfile_list_column = [
    [
        sg.Text("Output Folder"),
        sg.In(size=(25, 1), enable_events=False, key="-OUTPUTFOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Output File   "),
        sg.InputText(size=(25, 1), enable_events=False, key="-OUTPUTFILE-"),
    ],
]

apply_column = [
    [
        sg.Text("Color Mode"),
        sg.Combo(list(["L", "RGB"]), default_value='L', size=(25, 1), enable_events=False, key='-MODE-') # L = monochrome, RGB is RGB
    ],
    [
        sg.Button('Encode', key='-ENCODE-')
    ],
    [
        sg.Button('Decode', key='-DECODE-')
    ],
]

layout = [
    [
        sg.Column(inputfile_list_column),
        sg.VerticalSeparator(),
        sg.Column(outputfile_list_column),
        sg.VerticalSeparator(),
        sg.Column(apply_column),
    ]
]

def encode(inFile, outFile, mode):
    #redundancy = False
    colorSize = 3 if mode == 'RGB' else 1

    f = open(inFile, "rb")
    byteData = f.read()
    size = math.ceil(math.sqrt(len(byteData) / colorSize))
    #size = math.ceil(math.sqrt(len(byteData)))

    img = Image.new(mode, (size, size))
    pixelMap = img.load()

    for i in range(len(byteData)):
        targetPixel = math.floor(i/colorSize)
        #targetPixel = i
        x = targetPixel % img.size[0]
        y = math.floor((targetPixel - x) / img.size[0])
        
        if (colorSize == 1):
            data = byteData[i]
            pixelMap[x,y] = data
        else:
            targetByte = i % colorSize
            data = list(pixelMap[x,y])
            data[targetByte] = byteData[i]
            pixelMap[x,y] = tuple(data)
            #data = byteData[i]
            #pixelMap[x,y] = (data, data, data)
            
    img.show()
    img.save(outFile + ".png", compress_level=0)
    img.close()

def decode(inFile, outFile, mode):
    redundancy = False
    colorSize = 3 if mode == 'RGB' else 1

    img = Image.open(inFile)
    pixelMap = img.load()
    pixels = img.size[1] * img.size[0]

    f = open(outFile, "wb")

    for i in range(pixels):
        x = i % img.size[0]
        y = math.floor((i - x) / img.size[0])
        
        if (colorSize == 1):
            byte = pixelMap[x,y]
            f.write(bytes([byte]))
        else:
            data = pixelMap[x,y]
            if (redundancy):
                if not data[0] ^ data[1] == data[1] ^ data[2] == data[0] ^ data[2]:
                    byte = data[0]
                    if byte != data[1]: byte = data[1]
                    if byte != data[2]: byte = data[0]
                    print("Recovered byte corruption on (" + str(x) + ", " + str(y) + ") to " + str(byte) + ", data was " + str(data))
                    f.write(bytes([byte]))
                else:
                    f.write(bytes([data[0]]))
            else:
                f.write(bytes(data))
    f.close()
    #if (bytes([byte]) is not bytes(b'\x00')):

window = sg.Window("File To Image", layout)

while True:
    event, values = window.read()
    
    if event == "-ENCODE-":
        if len(values["-INPUTFILE-"]) > 0 and len(values["-OUTPUTFOLDER-"]) > 0 and len(values["-OUTPUTFILE-"]) > 0:
            encode(values["-INPUTFILE-"], values["-OUTPUTFOLDER-"] + "/" + values["-OUTPUTFILE-"], values["-MODE-"])
    
    if event == "-DECODE-":
        if len(values["-INPUTFILE-"]) > 0 and len(values["-OUTPUTFOLDER-"]) > 0 and len(values["-OUTPUTFILE-"]) > 0:
            decode(values["-INPUTFILE-"], values["-OUTPUTFOLDER-"] + "/" + values["-OUTPUTFILE-"], values["-MODE-"])
    
    
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
