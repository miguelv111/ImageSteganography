#
#   This script implements the Spatial Domain Technique for 
#     image steganography.
#
#   v1.0.0

# python3 spatialDomain.py /home/mviana/Pictures/avatar.jpg

import os
import sys
from PIL import Image
import imghdr
import math
#import bitarray

supportedPhotoFormats = ['jpg','tiff', 'jpeg']
verbose = True

def convertFromBits(numBits):

   if numBits == 0:
       return "0B"

   sizeName = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

   i = int(math.floor(math.log(numBits, 1024)))
   p = math.pow(1024, i)
   s = round(numBits / p, 2)

   return "%s %s" % (s, sizeName[i])

def extractEXIFData(filePath):

    try:
        img = Image.open(filePath)
        img_data = list(img.getdata())
        
        img_no_exif = Image.new(img.mode, img.size)
        img_no_exif.putdata(img_data)

        if len(list(img_no_exif.getdata())) and verbose:
            print(f"EXIF data extracted from {filePath}")

        return img_no_exif

    except IOError:
        print("Error occurred when extracting EXIF data from provided file!")
        exit()

def calculateSteganographySpace(img):

    # Assuming the usage of the less significant bit for each RGB component for each pixel of
    #   the target foto, the available number of bytes is: number_of_pixels * 3_RGB_color_components
    bitsAvailable = len(list(img.getdata())) * 3

    if not bitsAvailable > 0:
        exit()

    if verbose:
        print(f"The number of bits available for steganography if {convertFromBits(bitsAvailable)}")
    
    return bitsAvailable

def textToBits(text):
    
    bits = bin(int.from_bytes(text.encode(), 'big'))[2:]
    return list(map(int, bits.zfill(8 * ((len(bits) + 7) // 8))))

def textFromBits(bitsList):

    n = int(''.join(map(str, bitsList)), 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()

def getMessageToHide(message,maxSize):

    bitsList = textToBits(message)
    
    if len(bitsList) > maxSize:
        print(f"For the steganography technique applied in this script, the message provided could not be hidden in this image.\nTry with a image with more pixels.")
        exit()

    else:
        return bitsList

def paddingMessageToHide(message, maxSize):

    messageLen = len(message)
    nextMultipleOfThree = 0

    while not nextMultipleOfThree >= messageLen:
        nextMultipleOfThree += 3

    paddingAmount = nextMultipleOfThree - messageLen

    while paddingAmount > 0:

        message.append(0)
        paddingAmount -= 1

    if len(message) > maxSize:
        print(f"Message requires padding and exceedes the maximum message size.")
        exit()
    
    return message

def writeMessageToPhoto(img,message):

    messageIterator = 0
    pictureIterator = 0
    print(f"Message length if {len(message)} bits")

    img_data = list(img.getdata())

    for i in message:
        
        print(img_data[pictureIterator], pictureIterator)
        print(message[messageIterator],message[messageIterator+1],message[messageIterator+2], messageIterator)

        messageIterator += 3
        pictureIterator += 1

if __name__ == "__main__":

    # Get full path to the target photo

    if len(sys.argv) == 2:
        fileFullPath = sys.argv[1]
        print(f"Loaded from cmd line parameters: {fileFullPath}")
    else:
        
        fileFullPath = input(f"Provide the full path for the target photo: ")

    # Check if passed path is valid and photo type is supported
    if not os.path.isfile(fileFullPath):
        print(f"Provided path does not represent a valid file.")
        exit()

    providedFileType = imghdr.what(fileFullPath)
    if providedFileType not in supportedPhotoFormats:
        print(f"Provided file {fileFullPath} type ({providedFileType}) not supported by this script.")
        exit()

    # Extract EXIF data from file
    img_no_exif = extractEXIFData(fileFullPath)

    # Calculate available space for steganography into target photo
    maxMessageSize = calculateSteganographySpace(img_no_exif)

    # Get message to hide
    messageToHide = input(f"Insert message to hide: ")
    bitMessageArray = getMessageToHide(messageToHide, maxMessageSize)

    bitMessageArray = paddingMessageToHide(bitMessageArray,maxMessageSize)

    # Hide Message into target photo
    img_no_exif = writeMessageToPhoto(img_no_exif,bitMessageArray)

    # Save final image
    #img_no_exif.save(fileFullPath+".encoded")