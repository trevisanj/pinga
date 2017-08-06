import random
import math
import glob
from collections import namedtuple

BANK_DIR = "../bank"
AREA_MULT = 500.

Feature = namedtuple("Feature", ["name", "y", "area"])
features = [Feature("eye", 0, 10),
            Feature("nose", 0, 5),
            Feature("mouth", 0, 7),
            ]
            

bank_keywords = ["eye", "nose", "mouth"]
yy = [100, 200, 300]


def load_bank():
    """Loads images in bank directory. Returns list of lists"""
    
    images = []
    for feature in features:
        list_temp = []
        images.append(list_temp)
        for filename in glob.glob("{}/{}*".format(BANK_DIR, feature.name)):
            img = loadImage(filename)
            area_original = img.width*img.height
            area_wanted = feature.area*AREA_MULT
            if area_original != area_wanted:
                factor = math.sqrt(float(area_wanted)/area_original)
                img.resize(int(img.width*factor), int(img.height*factor))
            list_temp.append(img)
            
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
        