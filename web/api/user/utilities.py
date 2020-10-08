import os
from PIL import Image
from .artpiece import Artpiece
import random

#function to pull image off of database
def pull_picture(id):
    # handle invalid id
    artpiece = Artpiece.get_by_id(id)
    image = Image.frombytes("RGBX", (616, 414), artpiece.raw_image)
    image.show()
    return image

"""
Return a list of images in the 'gallery' folder and their descriptions
Output is list of tuples (image_location, image_description)
    output list is in random order for random display order every time
"""
def get_gallery_images():
    internal_gallery_path = './web/static/img/gallery/'
    public_gallery_path = '/static/img/gallery/'

    imagename_list = [internal_gallery_path + filename for filename in os.listdir(internal_gallery_path)]

    desc_list = list()
    for img_name in imagename_list:
        with Image.open(img_name) as image:
            desc_list.append(image.getexif().get(270)) #Exif ID 270 = ImageDescription
            #now check aspect ratio and normalize
    imagename_list = [public_gallery_path + filename for filename in os.listdir(internal_gallery_path)]
    
    img_list = list(zip(imagename_list,desc_list))
    random.shuffle(img_list)

    return img_list