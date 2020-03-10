#Data preprocessing
#import libraries
import numpy as np
import cv2
import sys
import os
from cv2_rolling_ball import subtract_background_rolling_ball
#from google.colab.patches import cv2_imshow
import pickle
#import keras
import threading
import time
import _thread
#main_dir = os.path.dirname(os.path.realpath(__file__)) 
main_dir=os.getcwd()
print(main_dir)
img_dir = os.path.join(main_dir, 'images')
print(img_dir)
fg_bg_dir = os.path.join(main_dir, 'fg_bg')
if not os.path.isdir(fg_bg_dir):
  os.mkdir(fg_bg_dir)
  
  
def get_bg_fg(img):
    softmask, background = subtract_background_rolling_ball(img,20, light_background=False,use_paraboloid=False, do_presmooth=True)
    mask = cv2.threshold(softmask,127, 255,cv2.THRESH_BINARY_INV| cv2.THRESH_OTSU)[1]
    background = cv2.bitwise_and(img, img, mask = mask)
    foreground = cv2.bitwise_and(img, img, mask = cv2.bitwise_not(mask))
    return background, foreground
def get_freq_spec(img):
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    return magnitude_spectrum

def process_photographer(photographer, img_write):
    #print('processing: ', photographer)
    #f_b = list()
    processed_images=0
    photographer_dir = os.path.join(img_dir, photographer)
    photographer_list = os.listdir(photographer_dir)
    #img_paths = list("{}{}{}".format(photographer_dir,'/', i) for i in os.listdir(photographer_dir))
    fg_dir = os.path.join(fg_bg_dir, photographer, 'foreground')
    bg_dir = os.path.join(fg_bg_dir, photographer, 'background')
    
    if not os.path.isdir(fg_dir):
        os.makedirs(fg_dir)
    else:
        processed_images=len(os.listdir(fg_dir))
        print(processed_images,photographer,len(photographer_list)-processed_images)
        time.sleep(1)
    
    if not os.path.isdir(bg_dir):
        os.makedirs(bg_dir)
    
    img_paths = list("{}{}{}".format(photographer_dir,'/', i) for i in photographer_list[processed_images:])
    
    for j,img_path in enumerate(img_paths):
        j=processed_images+j
        print('Precessing img: %d out of: %d in %s' %(j+1,len(img_paths),photographer))
        #print(img_path)
        img = cv2.resize(cv2.imread(img_path),(128,128))
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        background, foreground = get_bg_fg(gray_img)
        #mag_spectrum = get_freq_spec(gray_img)
        if img_write:
            cv2.imwrite(bg_dir + '/' + str(j+1) + '.jpg', background)
            cv2.imwrite(fg_dir + '/' +str(j+1) + '.jpg', foreground)
        #f_b.append([foreground, background, mag_spectrum, photographer])
    
    
    
  
  
def preprocess(img_dir, img_write = True):
    photographers = sorted(os.listdir(img_dir))
    thread_list = [0]*len(photographers)
    for i, photographer in enumerate(photographers):
       print(i)
       try:
           _thread.start_new_thread( process_photographer,  (photographer, img_write, ) )
       except:
           print ("Error: unable to start thread")
       time.sleep(1)
        #result.append(process_photographer(photographer, img_write))
       #print('finished processing:', photographer)
def save_pickle(file, filepath):
    pickle_out = open(filepath, 'wb')  
    pickle.dump(file, pickle_out)   
    pickle_out.close()  
    
def count(fg_bg_dir):
    total_processed = 0
    for root, dirs, files in os.walk(fg_bg_dir, topdown=False):
        for i in files:
            total_processed += len(i)
    file = open(main_dir+'/count.txt', 'w+') 
    file.write(str(total_processed))
    file.close()
    #time.sleep(10)


#count(fg_bg_dir)     
preprocess(img_dir)
try:
    _thread.start_new_thread( count, (fg_bg_dir, ))
           
except:
    print ("Error: unable to start thread")
#print(result)
#save_pickle(result, main_dir + '/total_data.pkl')
       
while 1:
    pass
