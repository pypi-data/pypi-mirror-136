from fastai.vision.all import *
from fastai.metrics import accuracy
import pandas as pd
import numpy as np
import os
import PIL.Image as Image
#import matplotlib.pyplot as plt

# Make sure our GPU is the default device to be used while training
defaults.device = torch.device('cuda:0')

# Dictionary to convert the class to the malware family name
lbldict = {1: 'Ramnit', 2:'Lollipop', 3:'Kelihos_ver3', 4:'Vundo', 5:'Simda', 6:'Tracur', 7:'Kelihos_ver1', 8:'Obfuscator.ACY', 9:'Gatak'}

Image.MAX_IMAGE_PIXELS = 933120000 # Change the max pixels to avoid warnings

path = '/run/media/bbdcmf/ITS490-Data/' # Path to the project folder
trainPath = path+'train/train_images_original/' # Path to the train images folder
exportPath = path+'bestmodel.pkl' # Path to our exported model/where we will export the model

def convertToImage(src, dst):
    files=os.listdir(src)
    print('Source:', src)
    print('Destination', dst)
    print('Converting...')
    for file in files:
        srcPath = src+file
        dstPath = dst+file+'.png'
        #if(file.endswith('.asm')):
        f = open(srcPath, 'rb')
        ln = os.path.getsize(srcPath)
        width = int(ln**0.5)
        a = bytearray(f.read())
        f.close()
        g = np.reshape(a[:width * width], (width, width))
        g = np.uint8(g)
        img = Image.fromarray(g)
        img.save(dstPath)
    print('Files converted successfully')

# csv = Path to train csv file, path = path to train images, validpct = percent of data for validation, label_col = column number for labels in csv, splitter = how the data should be splitted for train/validation, item_tfms = item transforms for data augmentation, device = what device should be used (cpu/gpu)
def loadData(csv, path, validpct=None, label_col=1, seed=None, splitter=None, item_tfms = None, device = None):
    df = pd.read_csv(csv, sep=',', header=0)
    dls = ImageDataLoaders.from_df(df, path, label_col=label_col, valid_pct=validpct, seed=seed, splitter = splitter, item_tfms = item_tfms, device=device)
    return dls

def trainModel(dls, arch, path, epoch_ct=1, metrics=error_rate):
    learn = cnn_learner(dls, arch, metrics=metrics)
    learn.fine_tune(epochs=epoch_ct)
    learn.dls.train = dls.train
    learn.dls.valid = dls.valid
    learn.export(path)

def isDir(directory):
    isDir = os.path.isdir(directory)
    if isDir == False:
        print("Error: Directory not found, please try again")
    return isDir
    
def showImages(testPath, item):
    # Show the images that are being predicted
    img = plt.imread(testPath+item)
    plt.imshow(img)
    plt.axis('off')
    plt.title(item)
    plt.show()

def predict(testPath, lbl_dict):
    files = os.listdir(testPath)
    for item in files:
        # Predict each file
        pred, pred_idx, probs = learn.predict(testPath+item)
        print(f"Item: {item} | Prediction: {lbl_dict[int(pred)]}; Probability: {probs[pred_idx]:.04f}")
        #showImges(testPath, item)

##################################***Training a new model***##################################
#
#dls = loadData('train.csv', trainPath, label_col=1, validpct=0.2, seed=42, splitter=RandomSplitter(), item_tfms = Resize(224), device = torch.device('cuda:0'))
#
#trainModel(dls, resnet34, path=exportPath, epoch_ct=2, metrics=[error_rate, accuracy])
#
##############################################################################################

###############################***Loading a PreTrained Model***###############################
#
# Import a trained model
learn = load_learner(exportPath, cpu=False)
#
##############################################################################################

answered = False
while answered == False:
    should_convert = input("Does your test set need to be converted to images?[y/n]")
    if should_convert.lower() == 'y':
        # If the files have not been converted to images yet
        srcPath = input("Enter the folder containing the files that will be converted:\n")
        isDir1 = isDir(srcPath)
        dstPath = input("Enter the folder you'd like the image(s) to be saved to:\n")
        isDir2 = isDir(dstPath)
        if(isDir1 and isDir2):
            convertToImage(srcPath, dstPath)
            answered = True
    elif should_convert.lower() == 'n':
        # If the files are already images
        dstPath = input("Enter the folder containing the images you'd like to predict:\n")
        answered = isDir(dstPath)
    else:
        print("Error, you must enter either y or n")
        
predict(dstPath, lbldict)
