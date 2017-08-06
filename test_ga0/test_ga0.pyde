"""
InGA - Interactive Genetic Algorithm framework - 2nd edition

TODO
  - the gene position must be kept where it is!!
  - mix the two concepts: incremental angle ("turn") and new starting angle, so now the gene will be a variable-size sub-drawing which always has the same orientation 
  - assign colors to parents so that chromosome pieces can be seen in children

"""
import math
import random
import copy


# Constants

# Two types of phenotype
FLAG_INCREMENTAL_ANGLE = True

# Keyboard control setup
# replace all non-green with random individuals
KEY_RANDOM = "R"
# replace all non-green with mutants
KEY_MUTANTS = "M"
# replace all non-green with children
KEY_CHILDREN = "C"

# Visual setup
# Canvas dimensions
WIDTH, HEIGHT = 700, 700
# Scale for rendering the individuals
SCALE_K = 1. / 300 if not FLAG_INCREMENTAL_ANGLE else 1./500
# spacing between figures
SPACING = 10

# Number of individuals
POPULATION_SIZE = 16

# Other constants
# Fitness value for the individuals which the user *likes*
GREEN = 1
# Fitness value for the individuals which the user *doesn't like* (no
# longer used)
RED = -1
# White color
COLOR255 = color(255, 255, 255)
# Drawing state
ST_DRAWING = 2


####################################################################################
# Case-specific implementation 

# Individual setup
# Number of genes (i.e., line segments) in each individual
NUM_GENES = 100
# Minimum length of line
MIN_STEP = 3
# Maximum length of line
MAX_STEP = 20
# Maximum "turn", i.e., angle change relative to direction of previous step
MAX_TURN = 90
# Child generation: maximum fraction of chromossome to be taken as a single part
# when generating a child (float between 0 and 1)
MAX_PART_SIZE_PROPORTION = 0.3
# number of genes to mutate
MUTATION_NUM = 50


class Individual(object):
    """Class to store chromosome and mark"""

    def __init__(self):
        self.mark = None
        self.chromosome = []

    def __len__(self):
        return len(self.chromosome)

def random_individual():
    """Creates new random individual

    Chromosome is encoded as: [(angle in degrees, step in pixels), ...]
    """
    ret = Individual()
    for i in range(NUM_GENES):
        angle = (random.randint(0, 360) if i == 0 else random.randint(-MAX_TURN, MAX_TURN)) if FLAG_INCREMENTAL_ANGLE else random.randint(0, 360)
        ret.chromosome.append([angle, random.randint(MIN_STEP, MAX_STEP)])
    return ret


def create_child(individuals, MAX_PART_SIZE_PROPORTION=0.3):
    """Creates single individual as a combination of parts of input individuals

    Args:
        individuals: list of individuals
        max_consecutive_proportion: maximum fraction of chromossome to be taken as a single part (float between 0 and 1)
    """

    def _split_chromosome(chromosome, max_part_size):
        """
        Splits chromossome in parts

        Args:
            individual:
            max_part_size: maximum number of consecutive genes to keep

        Returns a list of pieces of a chromossome
        """
        NUM_GENES = len(chromosome)
        i = 0
        ret = []
        while i < NUM_GENES:
            part_size = min(random.randint(1, max_part_size), NUM_GENES - i)
            ret.append(chromosome[i:i + part_size])
            i += part_size
        return ret

    max_part_size = int(MAX_PART_SIZE_PROPORTION * NUM_GENES)

    parts = sum([_split_chromosome(ind.chromosome, max_part_size)
                 for ind in individuals], [])
    random.shuffle(parts)

    ret = Individual()
    i, i_part = 0, 0
    while i < NUM_GENES:
        part = parts[i_part]
        if len(part) > NUM_GENES - i:
            part = part[0:NUM_GENES - i]
        ret.chromosome.extend(part)
        i += len(part)
        i_part += 1
    return ret


def mutate(individual):
    """
    Mutates individual *in place*

    If a gene will mutate, there is 50% chance that I will change the angle 
    and 50% chance that I will change the line size
    """
    for i in range(MUTATION_NUM):
        # takes a random gene from individual
        gene = random.choice(individual.chromosome)
        if random.random() < .5:
            # angle
            gene[0] += (random.random() - .5) * 10
        else:
            # line length
            gene[1] += (random.random() - .5) * 20


def draw_individual(individual):
    """Renders individual on screen"""

    # first pass to determine width & height
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
        x += step * cos(angle_rad)
        y += step * sin(angle_rad)
        points.append((x, y))
        xmin = min(x, xmin)
        xmax = max(x, xmax)
        ymin = min(y, ymin)
        ymax = max(y, ymax)

    w, h = xmax - xmin, ymax - ymin
    
    pushMatrix()
    # ---begin---
    translate(-w/2-xmin, -h/2-ymin)
    stroke(0)
    fill(0)
    ellipse(0, 0, 4, 4)  # Marks starting point
    noFill()
    beginShape()
    for point in points:
        vertex(*point)
    endShape()
    # ---end---
    popMatrix()




###################################################################################
# Generic GA framework

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


###################################################################################
# Frontend

def get_num_cols_rows(size_):
    """Calculates number of panel rows and columns based on population size"""
    num_rows = int(math.sqrt(POPULATION_SIZE))

    while num_rows >= 1:
        num_cols = size_ / num_rows
        if num_cols - int(num_cols) < 0.01:
            break
        num_rows -= 1
    return num_cols, num_rows


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
# Initial population
population = new_population_random()
# Current machine state
state = ST_DRAWING


# Processing events

def setup():
    size(WIDTH, HEIGHT)
    stroke(0)
    background(220)
    noSmooth()


def draw():
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


def mouse_to_k(x, y):
    k = -1
    x0 = (x - SPACING) % panel_step
    if x0 <= panel_width:
        y0 = (y - SPACING) % panel_step
        if y0 <= panel_width:
            k = (x - SPACING) / panel_step + (y - SPACING) / panel_step * nc
    return k


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


def keyPressed():
    global state
    if key.upper() in (KEY_CHILDREN, KEY_MUTANTS, KEY_RANDOM):
        state = key.upper()
        