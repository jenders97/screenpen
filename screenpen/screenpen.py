#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Author:       Robert Susik, Joseph Enders
# Email:        robert.susik@gmail.com
# ----------------------------------------------------------------------------
# Modified by Joseph Enders to better suit my uses. 
# Removed PyQt5, Matplotlib

import subprocess
import sys
import os
import configparser
import platform

from xml.dom import minidom
from collections.abc import Iterable
from typing import Callable, override
from datetime import datetime
from itertools import groupby

# Setting up Qt resources

from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QPoint, QRect, Qt, QSize
from PyQt6.QtGui import (
    QGuiApplication, QIcon, QPalette, QColor, QCursor, QPainter,
    QPixmap, QKeySequence, QAction, QShortcut, QImage, QScreen,
    QMouseEvent, QKeyEvent, QPaintEvent, QPainterPath
)

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout, 
    QPlainTextEdit, QListWidget, QListWidgetItem, QHBoxLayout, QGridLayout, QToolBar, 
    QDialog, QToolButton, QMenu, QColorDialog, QGraphicsDropShadowEffect
)

type Color = QColor | Qt.GlobalColor | int


PALETTE_PROPS = {
    'window': 'window',
    'windowText': 'windowText',
    'base': 'base',
    'alternateBase': 'alternateBase',
    'toolTipBase': 'toolTipBase',
    'toolTipText': 'toolTipText',
    'text': 'text',
    'button': 'button',
    'buttonText': 'buttonText',
    'brightText': 'brightText',
    'link': 'link',
    'highlight': 'highlight',
    'highlightedText': 'highlightedText',
}


def _get_color_from_RGB(r: int, g: int, b: int)-> QColor:
    return QColor(r, g, b)


def _set_palette_color(palette: QPalette , property: str, value: Color):
    getattr(palette, property)().setColor(value)

# _set_palette_color(_create_palette(), PALETTE_PROPS['window'], _get_color_from_RGB(53, 53, 53))

ALIGNMENT = {
    'center': Qt.AlignmentFlag.AlignCenter,
    'left': Qt.AlignmentFlag.AlignLeft,
    'right': Qt.AlignmentFlag.AlignRight,
}

COLORS: dict[str, Color] = {
    'black': QtGui.QColorConstants.Black,
    'white': QtGui.QColorConstants.White,
    'red': QtGui.QColorConstants.Red,
    'green': QtGui.QColorConstants.Green,
    'blue': QtGui.QColorConstants.Blue,
    'cyan': QtGui.QColorConstants.Cyan,
    'magenta': QtGui.QColorConstants.Magenta,
    'yellow': QtGui.QColorConstants.Yellow,
    'gray': QtGui.QColorConstants.Gray,
    'darkGray': QtGui.QColorConstants.DarkGray,
    'lightGray': QtGui.QColorConstants.LightGray,
    'transparent': QtGui.QColorConstants.Transparent,
    'darkRed': QtGui.QColorConstants.DarkRed,
    'darkGreen': QtGui.QColorConstants.DarkGreen,
    'darkBlue': QtGui.QColorConstants.DarkBlue,
    'darkCyan': QtGui.QColorConstants.DarkCyan,
    'darkMagenta': QtGui.QColorConstants.DarkMagenta,
    'darkYellow': QtGui.QColorConstants.DarkYellow,
}

def _execute_dialog(dlg):
    return dlg.exec()

WINDOW_ATTRS = {
    'translucentBackground': Qt.WidgetAttribute.WA_TranslucentBackground,
}

IMAGE_FORMATS = {
    'ARGB32': QImage.Format.Format_ARGB32,
}

PEN_STYLES= {
    'solidLine': Qt.PenStyle.SolidLine,
    'dashLine': Qt.PenStyle.DashLine,
    'dotLine': Qt.PenStyle.DotLine,
    'dashDotLine': Qt.PenStyle.DashDotLine,
}

PEN_CAP_STYLES = {
    'roundCap': Qt.PenCapStyle.RoundCap,
    'squareCap': Qt.PenCapStyle.SquareCap,
    'flatCap': Qt.PenCapStyle.FlatCap,
}

PEN_JOIN_STYLES = {
    'roundJoin': Qt.PenJoinStyle.RoundJoin,
}

TOOLBAR_AREAS = {
    'leftToolBarArea': Qt.ToolBarArea.LeftToolBarArea,
    'rightToolBarArea': Qt.ToolBarArea.RightToolBarArea,
    'topToolBarArea': Qt.ToolBarArea.TopToolBarArea,
    'bottomToolBarArea': Qt.ToolBarArea.BottomToolBarArea,
}

TOOL_BUTTON_STYLE = {
    'toolButtonIconOnly': Qt.ToolButtonStyle.ToolButtonIconOnly,
}

POPUP_MODE = {
    'instantPopup': QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
}

COMPOSITION_MODE = {
    'source': QPainter.CompositionMode.CompositionMode_Source,
    'source_over': QPainter.CompositionMode.CompositionMode_SourceOver,
}

BUTTONS = {
    'left': Qt.MouseButton.LeftButton,
    'right': Qt.MouseButton.RightButton,
    'middle': Qt.MouseButton.MiddleButton,
}

BRUSHES = {
    'no_brush': Qt.BrushStyle.NoBrush,
}

CURSORS = {
    'arrow_cursor': Qt.CursorShape.ArrowCursor,
}

KEYS = {
    'escape': Qt.Key.Key_Escape,
    'enter': Qt.Key.Key_Enter,
    'return': Qt.Key.Key_Return,
    'shift': Qt.Key.Key_Shift,
}

def _path_move_to(path, point):
    path.moveTo(point.x(), point.y())

def _path_cubic_to(path, point1, point2, point3):
    return path.cubicTo(
        point1.x(), point1.y(), 
        point2.x(), point2.y(), 
        point3.x(), point3.y(), 
    )

DIALOG_BUTTONS = {
    'ok': QDialogButtonBox.StandardButton.Ok,
    'cancel': QDialogButtonBox.StandardButton.Cancel,
}
        

# import numpy as np

# import importlib

#from matplotlib.backends.qt_compat import QtCore,#QtCore, QtWidgets
#if QtCore.qVersion() >= "5.":
#    from matplotlib.backends.backend_qtagg import (
#        FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)
#else:
#    from matplotlib.backends.backend_qt4agg import (
#        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
#from matplotlib.figure import Figure

__version__ = "0.3.3"

# dir_path = os.path.dirname(os.path.realpath(__file__))
# syntax_py_path = f'{dir_path}/utils/syntax.py'
# spec = importlib.util.spec_from_file_location('syntax', syntax_py_path)
# syntax = importlib.util.module_from_spec(spec)
# sys.modules['syntax'] = syntax
# spec.loader.exec_module(syntax)

class ScreenPenWindow(QMainWindow):
    def __init__(self, screen: QScreen, screen_geom: QRect, pixmap: QtGui.QPixmap | None = None, transparent_background: bool = True,
                    config_file: str | None = None): # app: QApplication
        super().__init__()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        # PATHS
        try:
            prefix: str = sys._MEIPASS
            resources_xml_path = os.path.join(prefix, 'utils', 'resources.xml')
        except:
            prefix = ''
            resources_xml_path = os.path.join(dir_path, 'utils', 'resources.xml')

        self.resources_xml: str = resources_xml_path

        self.config: Configuration = Configuration(config_file)
        

        
        #self.setScreen(screen)# self.screen = screen
        if pixmap is not None:
            self.screen_pixmap: QPixmap = pixmap
        else:
            raise Exception("Error setting initial pixmap")

        self.screen_geom: QRect = screen_geom
        self.transparent_background: bool = transparent_background
        self.hidden_menus: bool = bool(self.config["hidden_menus"])
        self.icon_size: int = int(self.config["icon_size"])
        self.penbar_area: Qt.ToolBarArea = TOOLBAR_AREAS[str(self.config["penbar_area"])]
        self.boardbar_area: Qt.ToolBarArea = TOOLBAR_AREAS[str(self.config["boardbar_area"])]
        self.actionbar_area: Qt.ToolBarArea = TOOLBAR_AREAS[str(self.config["actionbar_area"])]

        if self.transparent_background:
            self.setAttribute(WINDOW_ATTRS['translucentBackground'])
        # self.move(screen_geom.topLeft())
        self.setGeometry(screen_geom)
        self.activateWindow()
        self.showFullScreen()
        self._createCanvas()
        self._clearCanvas()
        
        
        self.history: DrawingHistory = DrawingHistory(int(self.config["drawing_history"]))
        self.history.append(self.screen_pixmap)

        self.begin: QPoint = QPoint()
        self.end: QPoint = QPoint()
        self.lastPoint: QPoint = QPoint()

        self.drawing: bool = False
        self.curr_method: str = 'drawPath'
        self.curr_color: Color = COLORS['red']
        self.curr_style: Qt.PenStyle = PEN_STYLES['solidLine']
        self.curr_capstyle: Qt.PenCapStyle = PEN_CAP_STYLES['roundCap']
        self.curr_joinstyle: Qt.PenJoinStyle = PEN_JOIN_STYLES['roundJoin']
        self.curr_width: int = int(self.config["default_pen_size"])
        self.curr_br: QtGui.QBrush = QtGui.QBrush(self.curr_color)
        self.curr_pen: QtGui.QPen = QtGui.QPen()

        self.curr_args: list[QRect | QPoint | int | QPainterPath | None] = []
        self.path: QPainterPath | None = None

        self.highlighting: bool = False
        self.highlight_alpha: int = 128
        self._setupTools()
        self._setupIcons()
        self._createToolBars()
        if self.hidden_menus:
            self.hide_menus()

        self.sc_undo: QShortcut = QShortcut(QKeySequence(str(self.config["undo_key"])), self)
        _ = self.sc_undo.activated.connect(self.undo)
        self.sc_redo: QShortcut = QShortcut(QKeySequence(str(self.config["redo_key"])), self)
        _ = self.sc_redo.activated.connect(self.redo)
        self.sc_toggle_menus: QShortcut = QShortcut(QKeySequence(str(self.config["toggle_menus_key"])), self)
        _ = self.sc_toggle_menus.activated.connect(self.toggle_menus)
        self.sc_quit_program: QShortcut = QShortcut(QKeySequence(str(self.config["exit_shortcut_key"])), self)
        _ = self.sc_quit_program.activated.connect(self.quit_program)
        self.sc_clear_drawings: QShortcut = QShortcut(QKeySequence(str(self.config["clear_key"])), self)
        _ = self.sc_clear_drawings.activated.connect(self.removeDrawing())
        self.sc_save_drawing: QShortcut = QShortcut(QKeySequence(str(self.config["save_key"])), self)
        _ = self.sc_save_drawing.activated.connect(self.saveDrawing())
        self.sc_decrease_width: QShortcut = QShortcut(QKeySequence(str(self.config["decrease_width"])), self)
        _ = self.sc_decrease_width.activated.connect(self.decreaseWidth())
        self.sc_increase_width: QShortcut = QShortcut(QKeySequence(str("]")), self) #self.config["increase_width"])), self)
        _ = self.sc_increase_width.activated.connect(self.increaseWidth())
        self.sc_highlight: QShortcut = QShortcut(QKeySequence(str(self.config["highlight_key"])), self)
        _ = self.sc_highlight.activated.connect(self.setHighlight())


    def _setCursor(self, cursor: str | Qt.CursorShape | QPixmap, hotx: int | None = None, hoty: int | None = None):
        if hotx is None:
            hotx = 2
        if hoty is None:
            hoty = 2
        if type(cursor) == str:
            temp = self._applySvgConfig(self._icons[cursor], None)
            pixm = QPixmap.fromImage(QtGui.QImage.fromData(bytes(temp, encoding='utf-8')))
            pixm = pixm.scaled(QSize(32, 32))
            self.setCursor(QCursor(pixm, int(hotx), int(hoty)))
        elif type(cursor) == Qt.CursorShape:
            self.setCursor(QCursor(cursor))
        elif type(cursor) == QPixmap:
            self.setCursor(QCursor(cursor, int(hotx), int(hoty)))


    # @override
    # def keyPressEvent(self, a0: QKeyEvent | None):
    #     if a0 is not None:
    #         event = a0
    #     else:
    #         raise Exception("Invalid key event")
            
    #     if event.isAutoRepeat():
    #         return
    #     k = event.key()
    #     if (k==KEYS['shift']):
    #         self._setCursor('arrow2')


    # @override
    # def keyReleaseEvent(self, a0: QKeyEvent | None):
    #     if a0 is not None:
    #         event = a0
    #     else:
    #         raise Exception("Invalid key event")
            
    #     if event.isAutoRepeat():
    #         return
    #     k = event.key()
    #     if (k==KEYS['shift']):
    #         self._setCursor(cursor=Qt.CursorShape.ArrowCursor)


    def _setupIcons(self):
        self._icons: dict[str, str] = {}

        try:
            DOMTree = minidom.parse(self.resources_xml)
            icons = DOMTree.getElementsByTagName('icon')

            if len(icons) < 1:
                raise Exception('ERROR: there are no icons in resources.xml file')

            for icon in icons:
                if icon.getAttribute('name')=='':
                    raise Exception('ERROR: resources.xml: icon doesnt contain "name" attribute')

                self._icons[icon.getAttribute('name')] = icon.getElementsByTagName('svg')[0].toxml().replace('\n', '')

        except FileNotFoundError as ex:
            print('ERROR: There is no resources.xml file')
            raise ex

    def _applySvgConfig(self, svg_str: str, custom_colors_dict: dict[str, str] | None = None):
        colors_dict = {
            'STROKE': 'white',
            'FILL': 'silver'
        }
        if custom_colors_dict is not None:
            colors_dict = {**colors_dict, **custom_colors_dict}

        parsed = svg_str
        for el in colors_dict:                
            parsed = parsed.replace(f'{{{el}}}', colors_dict[el])

        return parsed


    def _getIcon(self, name: str, custom_colors_dict: dict[str, str] | None = None):
        return QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(bytes(self._applySvgConfig(self._icons[name], custom_colors_dict), encoding='utf-8'))))


    def _createCanvas(self):
        self.background: QImage = QtGui.QImage(self.size(), IMAGE_FORMATS['ARGB32'])
        self.imageDraw: QImage = QtGui.QImage(self.size(), IMAGE_FORMATS['ARGB32'])
        self.imageDraw_bck: QImage = QtGui.QImage(self.size(), IMAGE_FORMATS['ARGB32'])
        self._clearBackground()
    

    def _clearBackground(self): # make background transparent
        if self.transparent_background:
            self.background.fill(COLORS['transparent'])
        else:
            qp2 = QtGui.QPainter(self.background)
            qp2.drawPixmap(self.background.rect(), self.screen_pixmap, self.screen_pixmap.rect())
            _ = qp2.end()
        self.update()


    def _clearCanvas(self):
        self.imageDraw.fill(COLORS['transparent'])
        self.imageDraw_bck.fill(COLORS['transparent'])
        self.update()


    def _setupTools(self):
        self.curr_br.setColor(self.curr_color)
        self.curr_pen.setStyle(self.curr_style)
        self.curr_pen.setCapStyle(self.curr_capstyle)
        self.curr_pen.setJoinStyle(self.curr_joinstyle)
        self.curr_pen.setBrush(self.curr_br)
        self.curr_pen.setWidth(self.curr_width)


    def setColor(self, color: Color):
        def _setColor():
            self.curr_color = color
            if self.highlighting:
                try:
                    self.curr_color.setAlpha(self.highlight_alpha)
                    self.highlighting = True
                    
                except:
                    pass

            self._setupTools()
        return _setColor


    def setHighlight(self):
        def _setHighlight():
            if not self.highlighting:
                try:
                    self.curr_color.setAlpha(self.highlight_alpha)
                    self.highlighting = True

                except:
                    pass
                
            else:
                try:
                    self.curr_color.setAlpha(255)
                    self.highlighting = False

                except:
                    pass
                
            self._setAction2('drawPath')
        return _setHighlight
    

    def _getEraserPen(self, color: Color = COLORS['transparent'], size: int = 30):
        pen = QtGui.QPen()
        pen.setBrush(QtGui.QBrush(color))
        pen.setStyle(PEN_STYLES['solidLine'])
        pen.setCapStyle(PEN_CAP_STYLES['roundCap']) 
        pen.setJoinStyle(PEN_JOIN_STYLES['roundJoin'])
        pen.setWidth(size)
        return pen


    def setEraser(self):
        def _setEraser():
            pix = QPixmap()
            img = QtGui.QImage(QSize(32, 32), IMAGE_FORMATS['ARGB32'])
            img.fill(COLORS['transparent'])

            qp = QtGui.QPainter(img)
            qp.setPen(self._getEraserPen(QColor('#7acfe6'), 30))
            path = QtGui.QPainterPath()

            _path_move_to(path, QPoint(16, 16))
            _path_cubic_to(path, QPoint(16, 17), QPoint(16, 16), QPoint(16, 16))

            qp.drawPath(path)
            qp.setPen(self._getEraserPen(QColor('#eccdec'), 26))

            path = QtGui.QPainterPath()

            _path_move_to(path, QPoint(16, 16))
            _path_cubic_to(path, QPoint(16, 17), QPoint(16, 16), QPoint(16, 16))

            qp.drawPath(path)
            _ = qp.end()

            pix = pix.fromImage(img)
            self.setAction('drawEraser')()
            self._setCursor(pix, 16, 16)
            self._setupTools()
        return _setEraser


    def setPenStyle(self, style: Qt.PenStyle):
        def _setStyle():
            self.curr_style = style
            self._setupTools()

        return _setStyle


    def setWidth(self, width: int):
        def _setWidth():
            self.curr_width = width
            self._setupTools()
        return _setWidth
    

    def increaseWidth(self):
        def _increaseWidth():
            self.curr_width += 2
            self._setupTools()
        return _increaseWidth
    

    def decreaseWidth(self):
        def _decreaseWidth():
            self.curr_width -= 2
            self._setupTools()
        return _decreaseWidth


    def setAction(self, action: str, cursor: str | Qt.CursorShape | QPixmap | None = None):
        def _setAction():
            self.curr_method = action
            if cursor is None:
                self._setCursor(CURSORS['arrow_cursor'])
        return _setAction


    def _setAction2(self, action: str, cursor: str | Qt.CursorShape | QPixmap | None = None):
        self.curr_method = action
        if cursor is None:
            self._setCursor(CURSORS['arrow_cursor'])


#     class ChartDialog(QDialog):
#         def ok_success(self, *args):
#             sourcecode = '\n'.join(list(map(lambda x: f'    {x}', self.code.toPlainText().replace('\t', '').replace(' ', '').splitlines())))
#             self.code = f'''
# def drawChart(qp:QtGui.QPainter, p1:QtCore.QPoint):
# {sourcecode}
#     canvas = FigureCanvas(fig)
#     canvas.draw()
#     canvas.setStyleSheet("background-color:transparent;")

#     renderer = canvas.get_renderer()
#     fwidth, fheight = fig.get_size_inches()
#     fig_bbox = fig.get_window_extent(renderer)
#     self.drawMatplotlib(qp, canvas, p1)
# setattr(self, 'drawChart', drawChart)
# '''
#             exec(self.code, {'self': self.parent, **globals()})
#             self.accept()

#         def __init__(self, parent):
#             super().__init__(parent=parent)
#             self.parent = parent
#             self.setWindowTitle("Chart")



#             QBtn = DIALOG_BUTTONS['ok'] | DIALOG_BUTTONS['cancel']

#             self.buttonBox = QDialogButtonBox(QBtn)
#             self.buttonBox.accepted.connect(self.ok_success)
#             self.buttonBox.rejected.connect(self.reject)
            
#             self.resize(800, 600)
#             self.code    = QPlainTextEdit()
#             highlight = syntax.PythonHighlighter(self.code.document())
#             self.code.zoomIn(4)
#             self.code.setPlainText('')

#             l = QListWidget()
#             for c in self.parent._codes:
#                 ech = QListWidgetItem(c.label)
#                 ech.code = c.code
#                 ech.name = c.name
#                 l.addItem(ech)
#             def code_clicked(c):
#                 self.code.setPlainText(c.code)
#             l.itemClicked.connect(code_clicked)
#             self.layout = QVBoxLayout()
            
#             buttons = QHBoxLayout()
#             buttons.addWidget(self.buttonBox, 1)

#             codelay = QHBoxLayout()
#             codelay.addWidget(l)
#             codelay.addWidget(self.code, 1)

#             self.layout.addLayout(codelay)
#             self.layout.addLayout(buttons)

#             self.setLayout(self.layout)

#     def showChart(self):
#         def _showChart():
#             self._setCursor(CURSORS['arrow_cursor'])
#             dlg = self.ChartDialog(self)
#             if _execute_dialog(dlg):
#                 self.curr_method = 'drawChart'
#             else:
#                 pass
        
#         return _showChart

    def removeDrawing(self):
        def _removeDrawing():
            self._clearCanvas()
        return _removeDrawing


    def captureScreen(self):
        for tb in self.toolBars:
            tb.hide()

        img = self.imageDraw.copy()
        qp = QtGui.QPainter(img)
        qp.drawPixmap(img.rect(), self.screen_pixmap, self.screen_pixmap.rect())
        qp.drawImage(img.rect(), self.background, self.background.rect())
        qp.drawImage(img.rect(), self.imageDraw, self.imageDraw.rect())
        _ = qp.end()

        for tb in self.toolBars:
            tb.show()

        return img

    # TODO use pyscreenshot https://github.com/ponty/pyscreenshot to save drawing.
    def saveDrawing(self):
        def _saveDrawing(_: int = 0):
            filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            print(f'Saving {filename}')
            _ = self.captureScreen().save(f'{filename}')
        return _saveDrawing


    def colorPicker(self) -> Callable[[], None]:
        def _colorPicker():
            color = QColorDialog.getColor()

            if color.isValid():
                self.curr_color = color
                if self.highlighting:
                    self.curr_color.setAlpha(self.highlight_alpha)
        return _colorPicker


    def addNewAction(self, name: str, icon: QIcon, fun: Callable[[], None]):
        action = QAction(icon, name, self)
        _ = action.triggered.connect(fun)
        return action


    def _createToolBars(self):
        penToolBar = QToolBar("Color", self)
        penToolBar.setIconSize(QSize(self.icon_size, self.icon_size))
        boardToolBar = QToolBar("Color", self)
        boardToolBar.setIconSize(QSize(self.icon_size, self.icon_size))
        actionBar = QToolBar("Action", self)
        actionBar.setIconSize(QSize(self.icon_size, self.icon_size))
        self.toolBars: list[QToolBar] = [actionBar, penToolBar, boardToolBar]
        self.addToolBar(self.actionbar_area, actionBar)
        self.addToolBar(self.penbar_area, penToolBar)
        self.addToolBar(self.boardbar_area, boardToolBar)

        
        avail_colors = {
            'red': COLORS['red'],
            'green': COLORS['green'],
            'blue': COLORS['blue'],
            'cyan': COLORS['cyan'],
            'magenta': COLORS['magenta'],
            'yellow': COLORS['yellow'],
            'black': COLORS['black'],
            'white': COLORS['white'],

            'darkRed': COLORS['darkRed'],
            'darkGreen': COLORS['darkGreen'],
            'darkBlue': COLORS['darkBlue'],
            'darkCyan': COLORS['darkCyan'],
            'darkMagenta': COLORS['darkMagenta'],

            'orange': _get_color_from_RGB(255, 165, 0),
            'gray': _get_color_from_RGB(128, 128, 128),
        }

        for acol in avail_colors:
            penToolBar.addAction(
                self.addNewAction(f'{acol}', self._getIcon('rect_filled', {'FILL': acol, 'STROKE': 'none'}), self.setColor(avail_colors[acol]))
            )
        
        penToolBar.addAction(self.addNewAction(f'Color Picker', self._getIcon('color_picker'), self.colorPicker()))
        penToolBar.addAction(self.addNewAction(f'Eraser', self._getIcon('eraser'), self.setEraser()))

        actionBar.addAction(self.addNewAction("Path", self._getIcon('path'), self.setAction('drawPath')))
        actionBar.addAction(self.addNewAction("Highlight", self._getIcon('highlighter'), self.setHighlight()))
        actionBar.addAction(self.addNewAction("Rect", self._getIcon('rect'), self.setAction('drawRect')))
        actionBar.addAction(self.addNewAction("Line", self._getIcon('line'), self.setAction('drawLine')))
        actionBar.addAction(self.addNewAction("Point", self._getIcon('dot'), self.setAction('drawDot')))
        # actionBar.addAction(self.addAction("Matplotlib chart", self._getIcon('mpl'), self.showChart()))
        
        

        lineTypeMenu = QMenu()
        lineTypeMenu.addAction(self.addNewAction('Solid', self._getIcon('line'), self.setPenStyle(PEN_STYLES['solidLine'])))
        lineTypeMenu.addAction(self.addNewAction('Dashed', self._getIcon('line_dashed'), self.setPenStyle(PEN_STYLES['dashLine'])))
        lineTypeButton = QToolButton(self)
        lineTypeButton.setToolButtonStyle(TOOL_BUTTON_STYLE['toolButtonIconOnly'])
        lineTypeButton.setIcon(self._getIcon('line_type'))
        lineTypeButton.setPopupMode(POPUP_MODE['instantPopup']) # MenuButtonPopup
        lineTypeButton.setMenu(lineTypeMenu)
        lineTypeButton.setToolTip('Line type')
        _ = actionBar.addWidget(lineTypeButton)

        lineWidthMenu = QMenu()
        lineWidthMenu.addAction(self.addNewAction('Thin', self._getIcon('line_thin'), self.setWidth(width=3)))
        lineWidthMenu.addAction(self.addNewAction('Medium', self._getIcon('line_medium'), self.setWidth(width=15)))
        lineWidthMenu.addAction(self.addNewAction('Thick', self._getIcon('line_thick'), self.setWidth(width=25)))
        lineWidthButton = QToolButton(self)
        lineWidthButton.setToolButtonStyle(TOOL_BUTTON_STYLE['toolButtonIconOnly'])
        lineWidthButton.setIcon(self._getIcon('line_width'))
        lineWidthButton.setPopupMode(POPUP_MODE['instantPopup'])
        lineWidthButton.setMenu(lineWidthMenu)
        lineWidthButton.setToolTip('Line width')
        _ = actionBar.addWidget(lineWidthButton)

        boardToolBar.addAction(self.addNewAction("Whiteboard", self._getIcon('board', custom_colors_dict={'FILL': 'white'}), self.setupBoard(COLORS['white'])))
        boardToolBar.addAction(self.addNewAction("Blackboard", self._getIcon('board', custom_colors_dict={'FILL': 'black'}), self.setupBoard(COLORS['black'])))
        boardToolBar.addAction(self.addNewAction("Transparent", self._getIcon('board_transparent', custom_colors_dict={'FILL': 'black'}), self._clearBackground))
        boardToolBar.addAction(self.addNewAction("Remove drawings", self._getIcon('remove'), self.removeDrawing()))
        
        actionBar.addAction(self.addNewAction("Save image", self._getIcon('save'), self.saveDrawing())) # self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton)

        
    def scaleCoords(self, coords: QPoint):
        canvas_size = self.imageDraw.size()
        window_size = self.size()
        x_scale = canvas_size.width() / window_size.width()
        y_scale = canvas_size.height() / window_size.height()
        return QtCore.QPoint(int(coords.x()*x_scale), int(coords.y()*y_scale))

    @override
    def paintEvent(self, a0: QPaintEvent | None):
        if a0 is not None:
            event = a0
        else:
            raise Exception("Invalid painting event")

        self._setupTools()

        qp = QtGui.QPainter(self.imageDraw)
        canvasPainter = QtGui.QPainter(self)



        qp.setCompositionMode(COMPOSITION_MODE['source'])
        canvasPainter.setCompositionMode(COMPOSITION_MODE['source_over'])

        if BUTTONS['left'] and self.drawing:
            qp.setPen(self.curr_pen)
            qp.setBrush(self.curr_br)
            if self.curr_method in ['drawRect']:
                qp.setBrush(BRUSHES['no_brush'])
                self.curr_args = [QRect(self.begin, self.end)]
                qp.drawImage(self.imageDraw.rect(), self.imageDraw_bck, self.imageDraw_bck.rect())
                #
                
                getattr(qp, self.curr_method)(*self.curr_args)
                qp.setBrush(self.curr_br)
            elif self.curr_method in ['drawDot']:
                self.curr_args = [self.end, 10, 10]
                qp.drawImage(self.imageDraw.rect(), self.imageDraw_bck, self.imageDraw_bck.rect())
                
                getattr(qp, 'drawEllipse')(*self.curr_args)

            elif self.curr_method in ['drawLine']:
                qp.setBrush(BRUSHES['no_brush'])
                self.curr_args = [self.begin, self.end]
                qp.drawImage(self.imageDraw.rect(), self.imageDraw_bck, self.imageDraw_bck.rect())
                
                getattr(qp, self.curr_method)(*self.curr_args)
                qp.setBrush(self.curr_br)

            elif self.curr_method in ['drawPath']:
                if self.lastPoint != self.end:
                    qp.setBrush(BRUSHES['no_brush'])
                    qp.setPen(self.curr_pen)
                    _path_cubic_to(self.path, self.end, self.end, self.end)
                    self.curr_args = [self.path]
                    getattr(qp, self.curr_method)(*self.curr_args)
                    self.lastPoint = self.end
                    self.update()
                    qp.setBrush(self.curr_br)

            elif self.curr_method in ['drawEraser']:
                if self.lastPoint != self.end:
                    qp.setBrush(BRUSHES['no_brush'])
                    qp.setPen(self._getEraserPen(COLORS['transparent']))
                    _path_cubic_to(self.path, self.end, self.end, self.end)
                    self.curr_args = [self.path]
                    getattr(qp, 'drawPath')(*self.curr_args)
                    self.lastPoint = self.end
                    self.update()
                    qp.setBrush(self.curr_br)

        qp.setCompositionMode(COMPOSITION_MODE['source_over'])
        _ = qp.end()
        
        canvasPainter.drawImage(self.rect(), self.background, self.background.rect())
        canvasPainter.drawImage(self.rect(), self.imageDraw, self.imageDraw.rect())
        canvasPainter.setCompositionMode(COMPOSITION_MODE['source_over'])
        _ = canvasPainter.end()

    
    @override
    def mousePressEvent(self, a0: QMouseEvent | None):
        if a0 is not None:
            event = a0
        else:
            raise Exception("Invalid mouse event")
        
        # TODO make the buttons use config values
        if event.button() == BUTTONS['right']:
            sys.exit(0)

        if event.button() == BUTTONS['middle']:
            self.toggle_menus()
            
        if event.button() == BUTTONS['left'] and self.childAt(event.pos()) is None:
            self.drawing = True

        if self.curr_method in ['drawRect', 'drawChart', 'drawLine', 'drawDot']:
            qp = QtGui.QPainter(self.imageDraw_bck)
            qp.drawImage(self.imageDraw_bck.rect(), self.imageDraw, self.imageDraw.rect())
            _ = qp.end()
            self.begin = self.scaleCoords(event.pos())
            self.end = self.scaleCoords(event.pos())
            
        elif self.curr_method in ['drawPath', 'drawEraser']:
            self.path = QPainterPath()
            self.begin = self.scaleCoords(event.pos())
            self.end = self.scaleCoords(event.pos())
            _path_move_to(self.path, self.begin)
            self.lastPoint = self.scaleCoords(event.pos())
        self.update()

    @override
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if a0 is not None:
            event = a0
        else:
            raise Exception("Invalid mouse event")
            
        self.end = self.scaleCoords(event.pos())
        self.update()

    def drawPixmap(self, p: QPixmap):
        qp =  QPainter(self.imageDraw)
        qp.setCompositionMode(COMPOSITION_MODE['source'])
        qp.drawPixmap(self.imageDraw.rect(), p, p.rect())
        _ = qp.end()

        qp2 = QtGui.QPainter(self.imageDraw_bck)
        qp2.setCompositionMode (COMPOSITION_MODE['source'])
        qp2.drawPixmap(self.imageDraw_bck.rect(), p, p.rect())
        _ = qp2.end()

    def undo(self):
        p = self.history.undo()
        self.drawPixmap(p)
        self.update()

    def redo(self):
        p = self.history.redo()
        self.drawPixmap(p)
        self.update()

    def hide_menus(self):
        for toolbar in self.toolBars:
            toolbar.hide()

    def show_menus(self):
        for toolbar in self.toolBars:
            toolbar.show()

    def toggle_menus(self):
        if self.hidden_menus:
            self.show_menus()
        else:
            self.hide_menus()
        self.hidden_menus = not self.hidden_menus

    def quit_program(self):
        sys.exit(0)

    @override
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        if a0 is not None:
            event = a0
        else:
            raise Exception("Invalid mouse event")

        if event.button() == BUTTONS['left'] and self.drawing == True:
            self.drawing = False
            self.path = None

            self.begin = self.scaleCoords(event.pos())
            self.end = self.scaleCoords(event.pos())

            self.update()
            p = QPixmap()
            _ = p.convertFromImage(self.imageDraw)
            self.history.append(el=p)


    def setupBoard(self, color: Color):
        def _setupBoard():
            self.background.fill(color)
            self.update()
        return _setupBoard

class ScreenshotError(Exception):
    pass

def _get_screenshots_grim(screens: list[QScreen]) -> list[tuple[QScreen, QRect, QPixmap]]:
    screenshots: list[tuple[QScreen, QRect, QPixmap]] = []
    for idx, screen in enumerate(screens):
        screen_geom = QGuiApplication.screens()[idx].geometry()
        x = screen_geom.x()
        y = screen_geom.y()
        w = screen_geom.width()
        h = screen_geom.height()
        
        path = f'./~screen{idx}.png'

        try:
            _ = subprocess.run(
                f'grim -g "{x},{y} {w}x{h}" \'{path}\'', 
                check=True,
                shell=True,
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            )
            
            pixmap = QPixmap(f'{path}')
            screenshots.append((
                screen,
                screen_geom,
                pixmap
            ))

        except subprocess.CalledProcessError as err:
            raise ScreenshotError(f'Err: Grim is not available {err}')
            
#    for idx in range(len(screens)): # might not be needed.
        try:
            os.remove(f'{path}')
            
        except FileNotFoundError:
            temp = os.path.abspath(f'{path}')
            print(f"Could not delete file: {temp}.")

    return screenshots


def _grab_screen(screen_idx: int, screen: QScreen):
    screen_geom: QRect = QGuiApplication.screens()[screen_idx].geometry()

    # temp = screen.grabWindow(
    #         0, 
    #         screen_geom.x(), 
    #         screen_geom.y(), 
    #         screen.size().width(), 
    #         screen.size().height()

    return (
        screen_geom, 
        screen.grabWindow(
            0, 
            screen_geom.x(), 
            screen_geom.y(), 
            screen.size().width(), 
            screen.size().height()
        )
    )
    

def _get_screenshots_pyqt(screens: list[QScreen]) -> list[tuple[QScreen, QRect, QPixmap]]:
    screenshots: list[tuple[QScreen, QRect, QPixmap]] = []
    for screen_idx, screen in enumerate(screens):
        screen_geom, screen_pixmap = _grab_screen(screen_idx, screen)
        screenshots.append((screen, screen_geom, screen_pixmap))
    return screenshots


def _get_screenshots_pillow(screens: list[QScreen]) -> list[tuple[QScreen, QRect, QPixmap]]:
    from PIL import ImageGrab, Image, UnidentifiedImageError
    #from time import sleep
    screenshots: list[tuple[QScreen, QRect, QPixmap]] = []
    for idx, screen in enumerate(screens):
        screen_geom = QGuiApplication.screens()[idx].geometry()

        try:
            img = ImageGrab.grab(
                bbox=(
                    screen_geom.x(), screen_geom.y(), 
                    screen_geom.x()+screen.size().width(), screen_geom.y()+screen.size().height()
                ), 
                xdisplay=""
            )
        
        except UnidentifiedImageError as err:
            raise ScreenshotError(f'Pillow problem: {err}')
            #sleep(1)
            #try:
            #    img = [el for el in e.args[0].split("'") if el.endswith('.png')]#[0]
            #    img = Image.open(img)
            #    img = img.crop((screen_geom.x(), screen_geom.y(), screen_geom.x() + screen.size().width(), screen_geom.y() + screen.size().height()))
            #    
            #except Exception as e:
            #    raise ScreenshotError('Pillow problem')

        except Exception as err:
            raise ScreenshotError(f'Pillow problem: {err}')
        
        img = img.convert('RGB')
        data = img.tobytes('raw', 'RGB')
        qim = QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGBA64_Premultiplied)
        screen_pixmap = QPixmap.fromImage(qim)
        screenshots.append((screen, screen_geom, screen_pixmap))
    
    return screenshots


def _is_grim_installed():
    try:
        _ = subprocess.run('grim -h2', shell=True, 
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            check=True)
        return True
    except:
        return False
    

def _is_pillow_installed():
    try:
        import PIL
        return True
    except:
        return False


def _get_screens(app: QApplication) -> list[tuple[QScreen, QRect, QPixmap]]:
    screens = app.screens()
    if len(screens) < 1:
        raise ScreenshotError('No screens found')
    
    try:
        if _is_pillow_installed():
            return _get_screenshots_pillow(screens)
        else:
            raise ScreenshotError('Pillow problem: Pillow not installed.')
    except ScreenshotError as err:
        print(err)

    try:
        if _is_grim_installed():
            return _get_screenshots_grim(screens)
        else:
            raise ScreenshotError('Grim problem: Grim not installed.')
    except ScreenshotError as err:
        print(err)

    try:
        screenshots = _get_screenshots_pyqt(app.screens())
        imgs: list[QImage] = [screenshot[-1].toImage() for screenshot in screenshots]
        pxls = [img.pixel(i, j) for img in imgs for i in range(img.width()) for j in range(img.height())]
        if [next(g, f := next(g, g)) == f for g in [groupby(pxls)]][0]:
            print('Warning: All screens seems to be blank (e.g. black). It means your system configuration may not be supported.')
        return screenshots
    except:
        raise Exception('Warning: Unable to take screenshots of your screens. Your system configuration may not be supported.')


def _is_transparency_supported():
    warn = 'INFO: Your system may support transparency but we cannot detect it. You may try to use -t parameter to force it.'
    try:
        if platform.system() == 'Linux':
            return '_NET_WM_WINDOW_OPACITY' in subprocess.run("xprop -root", shell=True, stdout=subprocess.PIPE).stdout.decode()
        else:
            print(warn)
            return False
    except:
        print(warn)
        return False

def _setPalette(app: QApplication):
    palette = QPalette()
    _set_palette_color(palette, PALETTE_PROPS['window'], _get_color_from_RGB(53, 53, 53))
    _set_palette_color(palette, PALETTE_PROPS['windowText'], COLORS['white'])
    _set_palette_color(palette, PALETTE_PROPS['base'], _get_color_from_RGB(25, 25, 25))
    _set_palette_color(palette, PALETTE_PROPS['alternateBase'], _get_color_from_RGB(53, 53, 53))
    _set_palette_color(palette, PALETTE_PROPS['toolTipBase'], COLORS['black'])
    _set_palette_color(palette, PALETTE_PROPS['toolTipText'], COLORS['white'])
    _set_palette_color(palette, PALETTE_PROPS['text'], COLORS['white'])
    _set_palette_color(palette, PALETTE_PROPS['button'], _get_color_from_RGB(53, 53, 53))
    _set_palette_color(palette, PALETTE_PROPS['buttonText'], COLORS['white'])
    _set_palette_color(palette, PALETTE_PROPS['brightText'], COLORS['red'])
    _set_palette_color(palette, PALETTE_PROPS['link'], _get_color_from_RGB(42, 130, 218))
    _set_palette_color(palette, PALETTE_PROPS['highlight'], _get_color_from_RGB(42, 130, 218))
    _set_palette_color(palette, PALETTE_PROPS['highlightedText'], COLORS['black'])
    
    app.setPalette(palette)
    _ = app.setStyle("Fusion")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-v', '--version', dest='version', action='version', version=f'Version: {__version__}')
    parser.add_argument('-1', nargs='?', type=int, dest='screen', const='0')
    parser.add_argument('-2', nargs='?', type=int, dest='screen', const='1')
    parser.add_argument('-3', nargs='?', type=int, dest='screen', const='2')
    parser.add_argument('-t', '--transparent', dest='transparent', help='Force transparent background. If you are sure your WM support it.', action='store_true')
    parser.add_argument('-c', '--config', type=str, dest='config', help='Path to config file', default='')

    args = parser.parse_args()

    app = QApplication(sys.argv)
    _setPalette(app)

    screens_data = _get_screens(app)

    if args.screen is None:
        screen_choice: int = 0
    else:
        screen_choice = args.screen
        
    if screen_choice >= len(screens_data):
        raise Exception(f'Error: You don\'t have so many screens ({screen_choice + 1}). Try lower number.')

    if args.config != '':
        config_path: str | None = args.config
    else:
        config_path: str | None = None
    
    screen: QScreen
    screen_geom: QRect
    pixmap: QPixmap
    screen, screen_geom, pixmap = screens_data[screen_choice]
    
    use_transparency = args.transparent or _is_transparency_supported()

    _ = ScreenPenWindow(screen=screen, screen_geom=screen_geom, pixmap=pixmap,
                             transparent_background=use_transparency, config_file=config_path)
    sys.exit(_execute_dialog(app))
    #sys.exit(app.exec())


class DrawingHistory():
        def __init__(self, limit: int = 4):
            self.history: list[QPixmap] = []
            self.limit: int = limit
            self.current: int = -1
        
        def append(self, el: QPixmap):
            if self.current < len(self.history):
                del self.history[self.current + 1:]
                
            if len(self.history) >= self.limit:
                del self.history[0]
                self.current = self.limit - 2

            self.history.append(el)
            self.current += 1
            
        def extend(self, l: Iterable[QPixmap]):
            self.history.extend(l)
            
        def undo(self) -> QPixmap:
            if self.current > 0:
                self.current -= 1
            return self.history[self.current]
        
        def redo(self):
            if self.current + 1 < len(self.history):
                self.current += 1
            return self.history[self.current]

        def len(self) -> int:
            return len(self.history)

        def __getitem__(self, key: int) -> QPixmap:
            try:
                return self.history[-key]

            except KeyError:
                print(f"Error: Invalid key in history ({key})")
                sys.exit(-2)


class Configuration():
    config_keys: dict[str, str] = {
        "penbar_area": "str",
        "boardbar_area": "str",
        "actionbar_area": "str",
        "hidden_menus": "bool",
        "icon_size": "int",
        "drawing_history": "int",
        "default_pen_size": "int",
        "undo_key": "str",
        "redo_key": "str",
        "toggle_menus_key": "str",
        "exit_shortcut_key": "str",
        "save_key": "str",
        "clear_key": "str",
        "decrease_width": "str",
        "increase_width": "str",
        "highlight_key": "str",
        "exit_mouse": "str",
        "toggle_menus_mouse": "str",
        "drawing_mouse": "str"
    }

    __default_config: dict[str, str | bool | int] = {
        "penbar_area": "topToolBarArea",
        "boardbar_area": "topToolBarArea",
        "actionbar_area": "leftToolBarArea",
        "hidden_menus": False,
        "icon_size": 25,
        "drawing_history": 50,
        "default_pen_size": 3,
        "undo_key": "Ctrl+z",
        "redo_key": "Ctrl+y",
        "toggle_menus_key": "Ctrl+m",
        "exit_shortcut_key": "Escape",
        "save_key": "Ctrl+s",
        "clear_key": "Ctrl+x",
        "decrease_width": "[",
        "increase_width": "]",
        "highlight_key": "Ctrl+h",
        "exit_mouse": "right",
        "toggle_menus_mouse": "middle",
        "drawing_mouse": "left"
    }

    def __init__(self, config_path: str | None = None) -> None:
        self.config: dict[str, str | bool | int] = {}

        default_config_path = os.path.join(os.environ["XDG_CONFIG_HOME"], "screenpenrc")
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if config_path is not None:
            config_ini_path = config_path

        elif os.path.exists(default_config_path):
            config_ini_path = default_config_path
        
        else:
            from shutil import copyfile
            from shutil import SameFileError, SpecialFileError
            packaged_conf_path = os.path.join(dir_path, "utils", "screenpenrc")
            try:
                _ = copyfile(packaged_conf_path, default_config_path, follow_symlinks=False)
                print(f"Added default config file to {default_config_path}.")
                config_ini_path = default_config_path
            
            except (SameFileError, SpecialFileError, FileNotFoundError):
                print("Using default configuration.")
                config_ini_path = "**default**"

        self.config_path: str = config_ini_path

        self.build_config()
        
    
    def build_config(self):
        if self.config_path == "**default**":
            self.config = self.__default_config
            return

        config = configparser.ConfigParser()
        _ = config.read(self.config_path)

        for key, item in self.config_keys.items():
            match item:
                case "bool":
                    temp = config['screenpen'].getboolean(key)
                    if temp is None:
                        temp = self.__default_config[key]
                    self.config[key] = temp
                
                case "int":
                    temp = config['screenpen'].getint(key)
                    if temp is None:
                        temp = self.__default_config[key]
                    self.config[key] = temp

                case "str":
                    temp = config['screenpen'].get(key)
                    if temp is None:
                        temp = self.__default_config[key]
                    self.config[key] = temp
                
                case _:
                    raise Exception("Error in parsing config. Nonexistant key type.")
        
        return

    
    def __getitem__(self, key: str) -> str | bool | int:
        try:
            return self.config[key]
        except KeyError:
            print(f"Error: Invalid key in configuration ({key})")
            sys.exit(-2)

if __name__ == '__main__':
    main()
