import glob

BANK_DIR = "../bank"

bank_keywords = ["eye", "nose", "mouth"]

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
    noLoop()
    
def draw():
    print("whatever")    