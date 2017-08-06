import random
import math
import glob
from collections import OrderedDict

BANK_DIR = "../bank"
AREA_MULT = 500.
Y_MULT = 7.
X0, Y0 = 300, 300 # Origin

# feature names (will be used to search for filenames)
f_names = ["eye", "nose", "mouth"]
# feature relative areas
f_areas = [10, 5, 7]
# feature relative y
f_y = [-5, 0, 5]
# will store all PImage objects
f_bank = []


def load_bank():
    """Loads images in bank directory. 
    
    Files in bank directory must begin with the name of a feature, i.e., "eye", "nose", etc.
    
    Returns:
        list of lists of PImage: [[PImage00, PImage01, ...], [PImage10, ...], ...]
    """
    
    global f_bank
    
    for name, area in zip(f_names, f_areas):
        list_temp = []
        f_bank.append(list_temp)
        for filename in glob.glob("{}/{}*".format(BANK_DIR, name)):
            img = loadImage(filename)
            img.format = ARGB

            # Turns white pixels transparent
            # Source: https://forum.processing.org/one/topic/turn-white-pixels-transparent.html
            color_test, color_replace = color(255, 255, 255), color(255, 0, 255, 255)
            print img.width, img.height
            if True:
                img.loadPixels()
                for y in range(img.height):
                    i0 = y*img.width
                    for x in range(img.width):
                        i = i0+x
                        if img.pixels[i] == color_test:
                            img.pixels[i] = img.pixels[i] & 0x00FFFFFF
                img.updatePixels()
                                            
            # Resizes image
            area_original = img.width*img.height
            area_wanted = float(area*AREA_MULT)
            factor = math.sqrt(area_wanted/area_original)
            img.resize(int(img.width*factor), int(img.height*factor))
            
            list_temp.append(img)
            

class Individual(object):
    """Class to store chromosome and mark"""

    def __init__(self):
        self.mark = None
        self.chromosome = []

    def __len__(self):
        return len(self.chromosome)


def random_individual():
    """Creates new random individual

    Chromosome is encoded as: [index, index, ...] (integers)
    """
    # global f_bank
    ret = OrderedDict()
    print f_names
    print f_bank
    for name, img_choices in zip(f_names, f_bank):
        ret[name] = random.randint(0, len(img_choices)-1) 
    return ret
                                   
def draw_individual(individual):
    pushMatrix()
    translate(X0, Y0)
    
    for index, img_choices, y_rel in reversed(zip(individual.values(), f_bank, f_y)):
        img = img_choices[index]
        y = y_rel*Y_MULT-img.height/2
        x = -img.width/2
        print x, y
        image(img, x, y)
        
    popMatrix()
                                                

def setup():
    load_bank()
    size(600, 600)
    background(255)
    noLoop()
    
def draw():
    # global f_bank
    ind = random_individual()
    draw_individual(ind)
