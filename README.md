# VT SailBOT 2020 Sensor Evaluation Repository
Welcome! This repository stores the VT SailBOT 2020 team's code for evaluating our
sensor systems, which includes tasks like sorting images into classes for testing
(`BUOY_PRESENT` or `BUOY_NOT_PRESENT`) and then identifying where in the `BUOY_PRESENT`
images the buoy actually is. 

## Assumptions
These tools are mainly used for processing image datasets used for testing the sensors. 
Each tool assumes that testing images are stored in the following directory structure: 

```
TEST_DATASET/ (the top level directory)
    [various directories where raw images are stored after being captured]
    BUOY_PRESENT/       (where images that _have_ a buoy are stored)
    BUOY_NOT_PRESENT/   (where images that _don't have_ a buoy are stored)
    BUOY_MASK_IMAGES/   (where mask images for images from BUOY_PRESENT are stored)
```

### Workflow: 
_You don't need to place any of the explicitly listed 
subdirectories in `TEST_DATASET/` yourself - the scripts in this repo will 
make them for you._


1. **Take images.** Place them into the main `TEST_DATASET/` directory under whatever
subdirectory names you want (_except the ones explicitly listed above). The 
`single_camera_image_capture.py` script from the `sailbot-20` repo will default to
storing these images in folders based on the date they were taken, such as 
`2019-11-14_10-40/`. 

2. **Sort/Classify images.** Use `run_sorting.py` to classify each image, placing them
into the `BUOY_PRESENT` or `BUOY_NOT_PRESENT` directories. These directories will be 
automatically created if they don't exist. 

3. **Identify buoy regions ("truth" the images).** Use `run_truthing.py` to identify
where the buoy is in each image from `BUOY_PRESENT/`. The script will create masks
according to your selections and place them into `BUOY_MASK_IMAGES/`, which is 
automatically created if it doesn't exist. 

## Details: `run_sorting.py`
### Instructions
The `run_sorting.py` tool helps users quickly classify images as either (1) containing
or (2) not containing a buoy. It displays images one after another on the screen, waiting
for the user to: 
* Press 'y', indicating the image **does** have a buoy,
* Press 'n', indicating the image **does not** have a buoy, or
* Press 'q', quitting the program. 

The tool will sort the images into `BUOY_PRESENT/` or `BUOY_NOT_PRESENT/` depending
on your choice.

Use the following command line arguments. 

> `python3 run_sorting.py <path_to_test_dataset_directory>`


## Details: `run_truthing.py`
### Instructions
The `run_truthing.py` tool should be run after `run_sorting.py`, and helps users quickly
identify which part of an image contains a buoy. It displays images from `BUOY_PRESENT/`
one after another, waiting for the user to: 

* (1) Click and then (2) drag a circle to represent where the buoy is, displayed as a 
red circle on the screen,
* Use the `h`/`j`/`k`/`l` keys to move the created circle `left`/`down`/`up`/`right`
respectively (VIM bindings, if you're familiar with them), 
* Use the `n`/`m` keys to `decrease`/`increase` the size of the circle, respectively, 
* Use the `space` key to confirm a selection and have the program save your selection
as an image mask, moving on to the next image, or
* Use the `q` key to save progress and quit. 

### Description
The tool itself has two windows: 
1. A _main_ window to view the entire image, and
2. A _closeup_ window to view the small area around the cursor in more detail (which
is extremely useful when selecting small regions). 

The size of the _closeup_ window is based on the `closeup_radius` command-line argument,
which is measured in pixels (_recommended value:_ `20`)

Mask files are stored as images with one layer of depth (`0..255`) in which every pixel
is black (`0`) except those in the user-defined selection, which are white (`255`). 

Each mask file is stored at `BUOY_MASK_IMAGES/mask.[name_and_ext_of_original_img]`.

Use the following command line arguments. 
> `python3 run_truthing.py <path_to_test_dataset_directory> <closeup_radius>`
