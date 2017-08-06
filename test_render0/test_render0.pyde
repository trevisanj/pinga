import random
import glob

BANK_DIR = "../bank"

bank_keywords = ["eye", "nose", "mouth"]
yy = [100, 200, 300]


def load_bank():
    """Loads images in bank directory. Returns list of lists"""
    
    images = []
    for kw in bank_keywords:
        list_temp = []
        images.append(list_temp)
        for filename in glob.glob("{}/{}*".format(BANK_DIR, kw)):
            list_temp.append(loadImage(filename))
            
    return images    
            

def setup():
    global images
    images = load_bank()
    size(600, 600)
    noLoop()
    
def draw():
    # global images
    for y, organ_choices in zip(yy, images):
        organ = random.choice(organ_choices)
        image(organ, 0, y) 
        