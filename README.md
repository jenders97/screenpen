## Screenpen 2 or something IDK

## Description

This is a fork of Robert Susik's [Screenpen](https://github.com/rsusik/screenpen) that I modified to match what I wanted more.

Screen annotation software which allows drawing directly on the screen. 
It is an open source and multiplatform 
(all systems that support Python) 
alternative to tools such as Epic Pen. 
Supported shapes:
* line,
* rectangle,
* chart (using matplotlib).

The behavior of the program depends on the Window System you use:
* if the system supports "live transparency then a transparent background is used (you can see a video playing in the background),
* if not then the screenshot is taken, and the user draws on the captured image (you see a static image of the screen),
* sometimes your WM may be detected as not supporting "live transparency". In that case try running with `-t` parameter to force it._

*Note: The app is created ad-hoc only for my use case. It may contain bugs...*

## Usage

### Installation and execution

### Controls
* Left mouse button - drawing.
* Right mouse button - quit.
* Keyboard shortcuts:
    * `Ctrl+Z` - undo,
    * `Ctrl+Y` - redo,
    * hold `Shift` - change mouse cursor icon to arrrow.
    * and much, much, more


### Configuration
There are a few configuration options that can be set using config file:
* `icon_size` - size of the icons (default: 50)
* `hidden_menus` - to hide menus on start (default: False)

The config should look like below:
```ini
[screenpen]
; Possible values for areas: topToolBarArea, bottomToolBarArea, leftToolBarArea, rightToolBarArea
penbar_area = topToolBarArea
boardbar_area = topToolBarArea
actionbar_area = leftToolBarArea
hidden_menus = False
icon_size = 50
sc_undo = Ctrl+Z
sc_redo = Ctrl+Y
sc_toggle_menus = Ctrl+1
exit_mouse_button = right
exit_shortcut = Escape
drawing_history = 500
```
(more options will be added in the future...)

### TODO

- [ ] Better Matplotlib charts support.
- [ ] Better wayland support.
- [ ] Add "paste image" feature.
- [ ] Add ellipse shape.
- [ ] Keyboard shortcuts for changing colors.

### Wayland support

Screenpen works in some Wayland compositors, but it is not perfect.
There are issues with windows positioning and transparency.
In case the window opens on wrong monitor (which I noticed on Sway WM) you can move it using `Win+Shift+Arrows` (or `Alt+Shift+Arrows`) shortcuts to a desired monitor.
Please let me know if you run into any issues. I have good luck with it on KDE wayland