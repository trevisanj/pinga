"""
Incomplete program for a genetic algorithm tutorial.

The task is to implement the following methods:
    - random_individual()
    - draw_individual()
    - mutate()
    - create_child() 
    
See ../README.md for more detailed information.
"""
import math
import random
import copy
import glob
from collections import OrderedDict


# # Globals
#
# ## General setup
#
# Mutation probability for each gene
MUTATION_PROB = .1
# Scaling factor affecting the sizes of the images drawn
AREA_MULT = 500.
# Scaling factor affecting the distances between images
DIST_MULT = 7.
#
# ## F_* variables: "feature" data
#
# These variables may be seen as columns in a table.
#
# feature names (will be used to search for filenames)
F_NAMES = ["eye", "nose", "mouth"]
# feature relative areas
F_AREAS = [10, 5, 7]
# feature relative y
F_Y = [-5, 0, 5]
# list of lists, will store all PImage objects
F_BANK = []


def load_bank():
    """Loads images from bank directory
    
    Files in bank directory must begin with the name of a feature, i.e., "eye", "nose", etc.
    
    Returns:
        list of lists of PImage: [[PImage00, PImage01, ...], [PImage10, ...], ...]
    """
    
    global F_BANK
    for name, area in zip(F_NAMES, F_AREAS):
        list_temp = []
        F_BANK.append(list_temp)
        for filename in glob.glob("{}/{}*".format("../bank", name)):
            img = loadImage(filename)
            img.format = ARGB

            # Turns white pixels transparent
            # Source: https://forum.processing.org/one/topic/turn-white-pixels-transparent.html
            color_test = color(255, 255, 255)
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
    """Store chromosome and mark/fitness"""

    def __init__(self):
        self.mark = None
        self.chromosome = OrderedDict()

    def __len__(self):
        return len(self.chromosome)
    
    def __getitem__(self, x):
        return self.chromosome[x]
    
    def __setitem__(self, x, value):
        self.chromosome[x] = value

    def __iter__(self):
        return self.chromosome.__iter__()


def random_individual():
    """Generates a new random individual

    Returns:
        new Individual object
    """

    ret = Individual()
    for name, img_choices in zip(F_NAMES, F_BANK):
        ret[name] = random.randint(0, len(img_choices)-1) 
    return ret


def draw_individual(individual):
    
    for index, img_choices, y_rel in reversed(zip(individual.chromosome.values(), F_BANK, F_Y)):
        img = img_choices[index]
        y = y_rel*DIST_MULT-img.height/2
        x = -img.width/2
        image(img, x, y)


def mutate(individual):
    """
    Mutates individual *in place*
    
    Mutation changes the index of a feature.

    Returns:
        None
    """
    for key_, value in individual.chromosome.iteritems():
        if random.random() < MUTATION_PROB:
            individual[key] = random.randint(0, len(F_BANK[key])-1)


def create_child(parents):
    """Creates single individual as a combination of genes taken randomly from parents.
    
    Note that individual may have arbitrary number of parents.
    
    Returns:
        new Individual object
    """

    ret = Individual()
    for key in parents[0]:
        ret[key] = random.choice(parents)[key] 
    return ret


####################################################################################################
# # Generic 
#
# The code henceforth can be used in different problems

# ## Constants
#
# ### Keyboard control setup
#
# replace all non-green with random individuals
KEY_RANDOM = "R"
# replace all non-green with mutants
KEY_MUTANTS = "M"
# replace all non-green with children
KEY_CHILDREN = "C"
#
# ### Visual setup
#
# Canvas dimensions (pixels)
WIDTH, HEIGHT = 700, 700
# Scale for rendering the individuals (arbitrary unit)
# (tune this until drawing size is acceptable)
SCALE_K = 2. / 300
# spacing between figures (pixels)
SPACING = 10
#
# Number of individuals
POPULATION_SIZE = 36
#
# ### Other constants
#
# Fitness value for the individuals which the user *likes*
GREEN = 1
# White color
COLOR255 = color(255, 255, 255)
# Drawing state
ST_DRAWING = 2


#######################################
# ## Generic-algorithm related routines

def new_population_mutants(population):
    """Generates new population replacing non-green with their mutant versions"""
    ret = _keep_green(population)
    num_green = len(ret)
    for i in range(POPULATION_SIZE - num_green):
        new = copy.deepcopy(ret[i % num_green])
        new.mark = 0
        mutate(new)
        ret.append(new)
    return ret


def new_population_children(population):
    """Generates new population replacing non-green with children from green individuals"""
    ret = _keep_green(population)
    ret.extend([create_child(ret) for i in range(POPULATION_SIZE - len(ret))])
    return ret


def _keep_green(population):
    """Filters out non-green individuals"""
    return [x for x in population if x.mark == GREEN]


def new_population_random(population=None):
    """Generates new population replacing non-green with random individuals

    Args:
        population: list of Invididual

    Returns:
        list: new population
    """
    ret = _keep_green(population) if population is not None else []
    ret.extend([random_individual()
                for i in range(POPULATION_SIZE - len(ret))])
    return ret


#############
# ## Frontend

# Calculated variables
#
# Number of panel rows and columns
nc, nr = get_num_cols_rows(POPULATION_SIZE)
# Panel width (*and also height*) in pixels
panel_width = int((WIDTH - SPACING * (nc + 1)) / nc)
# Distance between the left corners of panels. Note that this is a float
panel_step = (WIDTH - SPACING * (nc + 1)) / nc + SPACING
# Actual scale value
scale_ = panel_width * SCALE_K
# Current machine state
state = ST_DRAWING


########################
# ### Auxiliary routines

def get_num_cols_rows(size_):
    """Calculates number of panel rows and columns based on population size"""
    num_rows = int(math.sqrt(POPULATION_SIZE))

    while num_rows >= 1:
        num_cols = size_ / num_rows
        if num_cols - int(num_cols) < 0.01:
            break
        num_rows -= 1
    return num_cols, num_rows


def mouse_to_k(x, y):
    """Converts mouse coordinates to index of individual in population"""
    k = -1
    x0 = (x - SPACING) % panel_step
    if x0 <= panel_width:
        y0 = (y - SPACING) % panel_step
        if y0 <= panel_width:
            k = (x - SPACING) / panel_step + (y - SPACING) / panel_step * nc
    return k


############################
# ### Events from processing

def setup():
    global population
    size(WIDTH, HEIGHT)
    stroke(0)
    background(220)
    noSmooth()
    frameRate(10)
    load_bank()
    population = new_population_random()


def draw():
    """
    Drawing loop

    This is implemented as a state machine. The main state is ST_DRAWING. If 
    one of the KEY_* keys is pressed, a new population will be generated, then
    fall back to ST_DRAWING
    """
    global state, population
    if state == ST_DRAWING:
        yborder = SPACING
        k = 0
        for j in range(nr):
            xborder = SPACING
            for i in range(nc):
                individual = population[k]

                fill_ = COLOR255
                if xborder <= mouseX <= xborder + panel_width and yborder <= mouseY <= yborder + panel_width:
                    fill_ = lerpColor(color(255, 255, 0), fill_, .5)

                elif individual.mark == GREEN:
                    # green, like it
                    fill_ = lerpColor(
                        lerpColor(color(0, 255, 0), COLOR255, .5), fill_, .5)

                fill(fill_)
                rect(xborder, yborder, panel_width, panel_width)
                clip(xborder, yborder, panel_width, panel_width)

                pushMatrix()
                translate(xborder + panel_width / 2,
                          yborder + panel_width / 2)
                scale(scale_)
                draw_individual(individual)
                popMatrix()

                noClip()
                xborder += panel_step
                k += 1
            yborder += panel_step
    else:
        if state in (KEY_CHILDREN, KEY_MUTANTS):
            num_green = len([x for x in population if x.mark == GREEN])
            if num_green == 0:
                # cannot mutate or generate children, no green, **beep!**
                print("\a")
            elif state == KEY_CHILDREN:
                population = new_population_children(population)
            else:
                population = new_population_mutants(population)
        else:
            population = new_population_random(population)
        state = ST_DRAWING


def keyPressed():
    global state
    if isinstance(key, int):
        return
    if key.upper() in (KEY_CHILDREN, KEY_MUTANTS, KEY_RANDOM):
        state = key.upper()


def mouseClicked():
    global population
    k = mouse_to_k(mouseX, mouseY)
    print("k = {}; mouseButton = {}".format(k, mouseButton))
    if k == -1:
        return
    if mouseButton == 37:  # left mouse button
        population[k].mark = GREEN
    elif mouseButton == 39:  # right mouse button
        population[k].mark = 0  # No longer green
