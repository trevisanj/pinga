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
MUTATION_PROB = .2
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
        self.mark = 0
        self.chromosome = OrderedDict()

    def __len__(self):
        return len(self.chromosome)
    
    def __getitem__(self, feature_name):
        return self.chromosome[feature_name]
    
    def __setitem__(self, feature_name, value):
        self.chromosome[feature_name] = value

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
    """This function produces the "phenotype", i.e., the visual representation of the individual"""
    
    for feature_name, img_choices, y_rel in reversed(zip(individual, F_BANK, F_Y)):
        index = individual[feature_name]
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
    for i, feature_name in enumerate(individual):
        if random.random() < MUTATION_PROB:
            temp = individual[feature_name]
            individual[feature_name] = random.randint(0, len(F_BANK[i])-1)


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
# Number of individuals
POPULATION_SIZE = 40
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
WIDTH, HEIGHT = 1000, 700
# Scale for rendering the individuals (arbitrary unit)
# (tune this until drawing size is acceptable)
SCALE_K = 2. / 300
# spacing between figures (pixels)
SPACING = 10
#
# ### Other constants
#
# Fitness value for the individuals which the user *prefers* (marked green)
MARK_GREEN = 1
# Fitness value for the remaining individuals 
MARK_WHITE = 0
# White color
COLOR255 = color(255, 255, 255)
# Drawing state
ST_DRAWING = 2


#######################################
# ## Generic-algorithm related routines

def new_population_mutants(population):
    """Generates new population replacing non-green with their mutant versions"""
    
    green_ = _keep(population)
    other = _keep(population, MARK_WHITE)
    for individual in other:
        mutate(individual)
    return green_+other


def new_population_children(population):
    """Generates new population replacing non-green with children from green individuals"""
    ret = _keep_green(population)
    ret.extend([create_child(ret) for i in range(POPULATION_SIZE - len(ret))])
    return ret


def _keep(population, mark=MARK_GREEN):
    """Filters desired individuals"""
    return [x for x in population if x.mark == mark]


def new_population_random(population=None):
    """Generates new population replacing non-green with random individuals

    Args:
        population: list of Invididual

    Returns:
        list: new population
    """
    ret = _keep(population) if population is not None else []
    ret.extend([random_individual()
                for i in range(POPULATION_SIZE - len(ret))])
    return ret


#############
# ## Frontend

########################
# ### Auxiliary routines

def get_num_cols_rows(size_):
    """Calculates number of panel rows and columns based on population size"""
    num_rows = int(math.sqrt(size_))

    while num_rows >= 1:
        num_cols = float(size_) / num_rows
        if num_cols - int(num_cols) < 0.01:
            break
        num_rows -= 1
    return int(num_cols), num_rows


def mouse_to_k(x, y):
    """Converts mouse coordinates to index of individual in population"""
    k = -1
    x0 = (x - SPACING) % panel_step
    if x0 <= panel_width:
        y0 = (y - SPACING) % panel_step
        if y0 <= panel_width:
            k = (x - SPACING) / panel_step + (y - SPACING) / panel_step * nc
    return k


########################
# ### Calculated globals
#
# Number of panel rows and columns
nc, nr = get_num_cols_rows(POPULATION_SIZE)
print "{} columns X {} rows = {}".format(nc, nr, POPULATION_SIZE)
# Panel width (*and also height*) in pixels
panel_width = min(int((WIDTH - SPACING * (nc + 1)) / nc), int((HEIGHT - SPACING * (nr + 1)) / nr))
# Distance between the left corners of panels. Note that this is a float
panel_step = min((WIDTH - SPACING * (nc + 1)) / nc + SPACING, (HEIGHT - SPACING * (nr + 1)) / nr + SPACING)
# Actual scale value
scale_ = panel_width * SCALE_K
# Current machine state
state = ST_DRAWING


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
    fall back to ST_DRAWING.

        ST_DRAWING +---+--> KEY_CHILDREN ---+
          ^ ^ ^ ^  |   |                    |
          | | | +--+   +--> KEY_MUTANTS --+ |
          | | |        |                  | |
          | | |        +--> KEY_RANDOM -+ | |
          | | +-------------------------+ | |
          | +-----------------------------+ |
          +---------------------------------+
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

                elif individual.mark == MARK_GREEN:
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
    elif state  == KEY_CHILDREN:
        num_green = len([x for x in population if x.mark == MARK_GREEN])
        if num_green == 0:
            # cannot mutate or generate children, no green, **beep!**
            print("\a")
        else:
            population = new_population_children(population)
        state = ST_DRAWING
    elif state == KEY_MUTANTS:
        population = new_population_mutants(population)
        state = ST_DRAWING
    elif state == KEY_RANDOM:
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
        population[k].mark = MARK_GREEN
    elif mouseButton == 39:  # right mouse button
        population[k].mark = 0  # No longer green