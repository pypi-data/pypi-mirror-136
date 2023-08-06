from asyncio.windows_events import NULL
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import os

def plot_visualization(imageDictionary,wantToSave=True,check=0,filename="newImage.jpg"): 
    image=NULL
    if check==0:
        image=imageDictionary["image"]
        image= image*255
    else :
        image=imageDictionary["transformedImage"]
    pilImage=Image.fromarray(np.uint8(image)).convert('RGB')
    CurrentFilepath = os.path.realpath(__file__)
    location = CurrentFilepath.replace(
            'my_package\\analysis\\visualize.py', 'Outputs\\')
    location = location.replace('\\', '/')  
    # print("Size of BBoxes: ",imageDictionary['bboxes'])

    for j in imageDictionary['bboxes']: # for one bbox
        x_min, y_min, x_max, y_max = j['bbox']
        shape = [(x_min, y_min), (x_max, y_max)]
        drawer = ImageDraw.Draw(pilImage)
        drawer.rectangle(shape, outline ="red", width=3) # draws rectangle on the image
        my_font = ImageFont.truetype('arial.ttf', 20) # for bigger font
        drawer.text((x_min,y_min), j['category'], font=my_font, fill = (255, 255, 0))
        # print("Hello")


    if wantToSave:
        pilImage.save(location + filename)
        # pilImage.show()

    return pilImage
  
  # Write the required arguments

#       TotalBoxPredicted=len(imageDictionary["gt_bboxes"])

#       for eachBox in imageDictionary["bboxes"]:
#         x_min, y_min, x_max, y_max = eachBox[1],eachBox[2],eachBox[3],eachBox[4]
#         shape = [(x_min, y_min), (x_max, y_max)]
#         draweImage = ImageDraw.Draw(imageDictionary["image"])
#         draweImage.rectangle(shape, outline ="red", width=5) # draw rectangle on the image
#         fontToBeUsed = ImageFont.truetype('arial.ttf', 20) 
#         draweImage.text((x_min,y_min), eachBox[0], font=fontToBeUsed, fill = (255, 255, 0))


#       if wantToSave:
#             imageDictionary["image"].save(location + imageDictionary['img_fn'].split('/')[-1])

#       return imageDictionary["image"]

  
    # The function should plot the predicted segmentation maps and the bounding boxes on the images and save them.
    # Tip: keep the dimensions of the output image less than 800 to avoid RAM crashes
    