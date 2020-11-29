<p align="center">Abandoned for now but i'll make it working later. It semi-works but inaccurate</p>
  
  
<img src="https://i.imgur.com/CIgEu75.png" width="500" height="297">
</p>
osu!rtm is a program written in Python, that creates maps based on replay. (BETA)

I'll add releases soon, it isn't ready yet but still working. If you want to test it - launch the python code yourself.

Made by [Whereabout](https://osu.ppy.sh/users/15201580)

## Features:
1. If svm is less than 0.1 adds bpm mark to compensate speed
2. Works with mods
3. Has gray anchors support, but uses slow algorithm for calculation (i think i cant implement a better one)
4. Works on both fc and non-fc maps

## TODO:
1. Improve algorithm for gray anchors
2. Add mouse support
3. Add miss hitwindow support (check if object was clicked early enough for a miss)
4. Probably add compensation for ending frames 

## FAQ
* Why does it only work when object is clicked? Can't you just copy player's movements during slider time?

You can. But that would be inaccurate. Clicking an object means you've positioned cursor on top of it and (howbeit) it was your decision to click. You can click an object early or late (your brain needs time to coordinate), and your cursor position would be the most accurate and expected during the moment of click. Another thing is that sometimes there are no frame at object time, and you would have to approximate. But there are always frames of clicking!
  
* What's the difference between gray and red anchors used for a generated slider?

For this program solely, red imply curve passing through them, so they ressemble the exact path cursor took. Even though the curve may look ugly and excessive. Gray anchors are control points for bezier curve, curve is constructed according to bezier formula and it's not the accurate path.
The only accurate thing is points, resulting shape may be different.
* Use red points if you need accuracy and you have fast and long sliders on your map (Der wald, Deal with the devil etc.).
* Use gray points if you need visual appeal and accuracy for short sliders (Cycle hit, some insane diffs or sotarks)
Both work accurately for small/slow sliders.

## How it works
![HowItWorks](https://i.imgur.com/rLN5a7H.png)
