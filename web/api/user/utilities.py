from PIL import Image
from .artpiece import Artpiece

#function to pull image off of database
def pull_picture(id):
    # handle invalid id
    artpiece = Artpiece.get_by_id(id)
    image = Image.frombytes("RGBX", (616, 414), artpiece.raw_image)
    image.show()
    return image