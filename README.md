# cueplayer

This is a simple and quite useless project I made on a whim because of a youtube video I saw ([this one](https://www.youtube.com/watch?v=PLP9c0Z4Q3Y)).
It uses cuesdk to play a video on your keyboard (or whatever device that supports cue, hopefully).  
It's only been tested on a K95 keyboard, [video here](https://www.youtube.com/watch?v=gzcWriqcSz4), so I don't know how well it will run on other devices.

### Requirements

This program requires python>=3.7 (It was tested on 3.8.6).  
The modules required are:
* [cuesdk](https://pypi.org/project/cuesdk/)
* [numpy](https://pypi.org/project/numpy/)
* [Pillow](https://pypi.org/project/Pillow/)
* [opencv-python](https://pypi.org/project/opencv-python/)

These will be installed through the requirement.txt file.

### Install

Clone repo and install modules.
```
git clone https://github.com/Maharaghi/cueplayer.git
cd cueplayer
python -m pip install -r requirements.txt
```
Place the video file you want to play in the same directory as `main.py`.  
The video file **MUST** be called `video.mp4` because I'm lazy and haven't added any way to input another name.  

Run the program with  
```
python main.py
```
