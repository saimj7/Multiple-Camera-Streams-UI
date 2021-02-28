# Multiple Camera Streams GUI
A simple user interface to stitch and display multiple camera streams with OpenCV and Kivy.

> Supports configuring several videos and ip cameras.

<div align="center">
<img src=mylib/misc/demo.gif?raw=true "demo" width=750 >
</div>

---

## Inference

- Install main libraries:
```
pip install opencv-python
pip install kivy
```
- To setup cameras via config, enter your video path or ip camera url in 'config>ui_config.json'.

> You can place your videos in mylib>videos or enter the url if its an ip camera. Example:

```
"camera_url": [
    "mylib/videos/1.mp4",
    "http://192.158.0.115:8050/video",
```
- To setup cameras via ui, click settings>enter details>apply after running the code:

<div align="center">
<img src=mylib/misc/settings.png?raw=true "settings" width=700 >
</div>

> You could also setup a database if you ever want to.

- To run: ``` python run.py ```



---

saimj7/ 28-02-2021 © <a href="http://saimj7.github.io" target="_blank">Sai_Mj</a>.
