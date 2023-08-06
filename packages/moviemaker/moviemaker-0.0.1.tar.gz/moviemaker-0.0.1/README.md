[![Build Python application](https://github.com/abulgher/moviemaker/actions/workflows/python-app.yml/badge.svg)](https://github.com/abulgher/moviemaker/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/abulgher/moviemaker/actions/workflows/python-publish.yml/badge.svg)](https://github.com/abulgher/moviemaker/actions/workflows/python-publish.yml)

# Moviemaker
An ultra simple image to movie converter

## Description
Yet another tool to put together images to make a video you can play in the web-browser.
The piece of software has been developed inside the microscopy group with the main goal of realizing short video clip using FIB/SEM images in order to show, for example, the production steps of lamellas, micro-pillars and other interesting preparation.
Being *ad-hoc* for this purpose, it has very little capabilities and it doesn't offer the wide range of possibilities other common video-editing tools normally have.

## What **Moviemaker** does
**Moviemaker** does three things:
1. **Convert all images contained in a folder** and respecting a given filtering string in a more convient format for video rendering. Normally SEM pictures are saved in **TIFF** format (8 or 24bit grey levels), while for the video making purpose is either **PNG** or **JPEG** color a much better choice. The user can select the output format from a list and choose the output folder.
2. **Generate a video from a sequence of images**. The user can select a folder and a filter to be applied to the image list. Moreover the FPS (*frame per second*) parameter can also be selected. FPS=1 means that each image will last exactly 1 second in the video. FPS=4 means that each image will last only 0.25 s. The output format is mp4 and cannot be changed.
3. **Concatenate videos**. The user can select two input video clip to generate a third one in which the second is directly appended to the first one. No clipping, no transitions possible. Sorry.

**Moviemaker** has a GUI structured with three tabs, one for each of the tasks described above. In each tab, the user can provide the required information and then click the start button to initiate the task. Each task is executed in a parallel thread so that the GUI will remain responsive the whole time and information messages will be displayed in the text area along with a progress bar. Even if technically possible, there is no stop or cancel button implemented for the moment.

## Possible improvements
It is plenty of possible new features to be added, but they will probably never added because we don't need to reinvent another video-editing package. Moviemaker does its job and that's more or less it.

# Installation
Just use pip
```bat
pip install moviemaker
```

# Usage
Moviemaker has a very intuitive GUI with no command line options.
Just type from your enviroment prompt:
```bat
python -m moviemaker
```
