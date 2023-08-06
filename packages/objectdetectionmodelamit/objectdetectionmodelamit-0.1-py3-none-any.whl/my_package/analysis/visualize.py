#Imports
import math
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import cv2
import numpy as np
def plot_visualization(imgs,segts,outputs,check): # Write the required arguments
  for i in range(len(imgs)):
    for j in segts[i][1][0:3]:
      imgs[i]=imgs[i]*((j<0.5).astype(int))
    
    imgs[i]=Image.fromarray((np.rollaxis(imgs[i],0,3)*255).astype(np.uint8))  #hw3 <--- 3hw 
    
    cnt=0
    outline_colr=["red","green","yellow"]
    for j in segts[i][0][0:3]:
      img1=ImageDraw.Draw(imgs[i])
      img1.rectangle(j,outline=outline_colr[cnt])
      cnt+=1
    
    imgs[i]=np.array(imgs[i])
    
    cnt=0
    text_colr=[(0, 0, 255),(231, 84, 128),(0,255, 0)]
    for j in range(0,min(3,len(segts[i][2]))):
      cal=segts[i][2][j]
      prob=segts[i][3][j]
      text=cal+'\n'+str("%.4f" % (prob))
      cv2.putText(img=imgs[i], text=text, org=tuple(map(int,segts[i][0][j][0])), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.4, color=text_colr[cnt],thickness=1)
      cnt+=1

    imgs[i]=Image.fromarray(imgs[i])
    if (check=='1'):
      imgs[i].save(outputs+'/'+str(i)+'.jpg')
    else:
      imgs[i].save(outputs+'/'+check+'.jpg')


    imgs[i].show()


      
    

      
  # The function should plot the predicted segmentation maps and the bounding boxes on the images and save them.
  # Tip: keep the dimensions of the output image less than 800 to avoid RAM crashes.
  
