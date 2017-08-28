"""
PInGA - Processing Intactive Genetic Algorithm

"Species": sketch
"""


import math
import random
import copy
import glob
from collections import OrderedDict


####################################################################################################
# # Specific implementation
#
# This part of the code contains the implementation of the "species" in case:
#   
# - "chromosome" representation ("genotype") 
# - genetic operators    
# - drawing individual ("phenotype")

# ## Globals
#
# ### General setup
#
# Mutation probability for each gene
MUTATION_PROB = .2
# Number of genes in chromosome, which is equivalent to number of drawing steps
NUM_GENES = 50
# Minimum length of line
MIN_STEP = 3
# Maximum length of line
MAX_STEP = 20
# Maximum "turn", i.e., angle change relative to direction of previous step
MAX_TURN = 90
# Maximum number of genes mutated in a mutation operation
MAX_MUTATIONS = 50
# Maximum number of "genes" to be kept together at child generation
MAX_GENES_TOGETHER = 20
# There are two types of phenotype
# - False: angle in chromosome is relative to arrow pointing right
# - True: angle in chromosome is relative to previous angle
FLAG_INCREMENTAL_ANGLE = False



class Individual(object):
    """Store chromosome and mark/fitness"""

    def __init__(self):
        self.mark = 0
        # [[angle0, step0], [angle1, step1], ...]
        self.chromosome = []

    def __len__(self):
        return len(self.chromosome)

    def __getitem__(self, feature_name):
        return self.chromosome[feature_name]

    def __setitem__(self, feature_name, value):
        self.chromosome[feature_name] = value

    def __iter__(self):
        return self.chromosome.__iter__()


def draw_individual(individual):
    """
    Renders individual on screen

    Args:
        individual: sequence with pair number of elements.
            [(angle_in_degrees, step_in_pixels), ...]
    """

    # first pass to determine width & height, collect points
    xmin, ymin, xmax, ymax = 99999, 99999, -99999, -99999
    x, y = 0, 0
    points = [(x, y)]
    angle_rad = 0
    for i in range(0, NUM_GENES):
        gene = individual.chromosome[i]
        if FLAG_INCREMENTAL_ANGLE:
            angle_rad += gene[0] * math.pi / 180
        else:
            angle_rad = gene[0] * math.pi / 180
        step = gene[1]
        x += step * scale_ * math.cos(angle_rad)
        y += step * scale_ * math.sin(angle_rad)
        points.append((x, y))
        xmin = min(x, xmin)
        xmax = max(x, xmax)
        ymin = min(y, ymin)
        ymax = max(y, ymax)
    w, h = xmax - xmin, ymax - ymin

    pushMatrix()

    # translate(-(panel_width - w) / 2 - xmin,
    #           -(panel_width - h) / 2 - ymin)
    translate(-w/2-xmin, -h/2-ymin)
    stroke(0)
    fill(0)
    ellipse(0, 0, 4, 4)  # Marks starting point
    noFill()
    beginShape()
    for point in points:
        vertex(*point)
    endShape()

    popMatrix()


def random_individual():
    """Generates a new random individual

    Returns:
        new Individual object
    """

    ret = Individual()
    for i in range(NUM_GENES):
        angle = (random.randint(0, 360) if i == 0 else random.randint(-MAX_TURN, MAX_TURN)) \
            if FLAG_INCREMENTAL_ANGLE else random.randint(0, 360)
        step = random.randint(MIN_STEP, MAX_STEP)
        ret.chromosome.append([angle, step])
    return ret



def mutate(individual):
    """
    Mutates individual *in place*
    
    Mutation changes the index of a feature.

    Returns:
        None
    """

    for i in range(MAX_MUTATIONS):
        if random.random() <= MUTATION_PROB:
            # mutates either the angle or the step
            if random.random() < .5:
                individual.chromosome[i][0] += (random.random() - .5) * 10
            else:
                individual.chromosome[i][1] += (random.random() - .5) * 20


def create_child(parents):
    """Creates single individual as a combination of genes taken randomly from parents.
    
    Note that individual may have arbitrary number of parents.
    
    Returns:
        new Individual object
    """

    ret = Individual()
    qtd = 0
    for i in range(len(parents[0])):
        if qtd == 0:
            parent_now = random.choice(parents)
            qtd = random.randint(1, MAX_GENES_TOGETHER)
        if qtd > 0:
            ret.chromosome.append(copy.copy(parent_now.chromosome[i]))
            qtd -= 1
    return ret






####################################################################################################
# # Generic engine 
#
# The code henceforth can be used with different "species". It roughly does the following:
#
# - draws entire population
# - handles mouse and keyboard input
# - implements the GA generation logic
#
# ## How to play
#
# Select/de-select individuals with the mouse according with your own subjective criterion, 
# then generate a new population using one of three options on the keyboard ("R"/"M"/"C").
#
# Selected (GREEN) individuals are always kept intact for the next generation. 
# 
# ### Controls
# 
# - Left mouse button: select individuals (turns tile background GREEN)
# - Right mouse button: de-selects individuals (turns tile background WHITE)
# - "R" key: new generation of random individuals. Generates a new population of random individuals
# - "M" key: new generation of mutants. Mutates non-GREEN individuals
# - "C" key: new generation of children. Generates a new population of children of the GREEN 
#            individuals
#

# ## Constants
#
# Number of individuals
POPULATION_SIZE = 16
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
SCALE_K = 1.5 / 300
# spacing between figures (pixels)
SPACING = 10
#
# ### Other constants
#
# Fitness value for the selected individuals
MARK_GREEN = 1
# Fitness value for the non-selected individuals 
MARK_WHITE = 0
# White color
COLOR255 = color(255, 255, 255)
# Drawing state
ST_DRAWING = 2


#######################################
# ## Generic-algorithm related routines

def new_population_mutants(population):
    """Generates new population replacing non-green with their mutant versions"""
    
    green_ = [x for x in population if x.mark == MARK_GREEN]
    other = [x for x in population if x.mark == MARK_WHITE]
    for individual in other:
        mutate(individual)
    return green_+other


def new_population_children(population):
    """Generates new population replacing non-green with children from green individuals"""
    ret = [x for x in population if x.mark == MARK_GREEN]
    ret.extend([create_child(ret) for i in range(POPULATION_SIZE - len(ret))])
    return ret


def new_population_random(population=None):
    """Generates new population replacing non-green with random individuals

    Args:
        population: list of Invididual

    Returns:
        list: new population
    """
    ret = [x for x in population if x.mark == MARK_GREEN] if population is not None else []
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
    smooth()
    frameRate(10)
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