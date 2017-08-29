# pinga

Interactive Genetic Algorithm in Processing (Python mode)


## Contents

```
 handson: sketchbook for hands-on session (see below)
    bank: image bank (see below)
   faces: hands-on solution
sketches: another "species" using the same interactive GA engine
```

Hands-on sketchbook, image bank, and presentation slides.

### Hands-on sketchbook

The directory `handson` is incomplete. It already contains a visual 
frontend and some of the genetic-algorithm related routines.

The following routines will be implemented during the hands-on session:

  - `random_individual()`, generates new individual from scratch
  - `draw_individual()`, aka produce the "phenotype"
  - `mutate()`, one of the genetic "operators"
  - `create_child()`, another genetic operator
  
If there is time left, we will also implement the following routines 
(otherwise we paste them from sketchbook in the `faces` directory`):

  - `new_population_random()`, generates new population of random individuals
  - `new_population_mutants()`, generates new population of mutants from existing population
  - `new_population_children()`, generates new population of children of selected individuals

### Image bank

The directory `bank` contains images of eyes, noses and mouths. New images can be downloaded from the web and simply saved into this folder to be made available for the program. However, all images must start either with the word "eye", "nose", or "mouth" in order to be found by the program.

