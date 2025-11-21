#!/usr/bin/env python3


import kivy
kivy.require('2.3.1') # replace with your current kivy version !

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser # file loading
from kivy.uix.screenmanager import ScreenManager, Screen # loading and plotting screens
from kivy.graphics import Line, Color, Ellipse
from kivy.uix.popup import Popup

# https://www.techwithtim.net/tutorials/kivy-tutorial/multiple-screens
# https://kivy.org/doc/stable/api-kivy.uix.filechooser.html#kivy.uix.filechooser.FileChooser
# https://www.geeksforgeeks.org/data-visualization/visualizing-bar-plot-and-line-plot-with-kivy
# https://stackoverflow.com/questions/42505450/kivy-change-filechooser-defaul-location

class InteractiveLineChart(Widget):
    def __init__(self, **kwargs):
        super(InteractiveLineChart, self).__init__(**kwargs)
        self.data = [10, 20, 15, 30, 250, 35, 20]
        self.points = []
        self.draw_line()

    def draw_line(self):
        with self.canvas:
            Color(0.8, 0.3, 0.3, 1)  # Line color
            self.line = Line(points=self.get_line_points(), width=2)
            # Color(0, 0, 0, 1)  # Point color
            # for point in self.points:
            #     Ellipse(pos=point, size=(10, 10))

    def get_line_points(self):
        width, height = self.size
        padding = 50
        max_value = max(self.data)
        points = []
        self.points = []
        for index, value in enumerate(self.data):
            x = padding + index * ((width - 2 * padding) / (len(self.data) - 1))
            y = padding + (value / max_value) * (height - 2 * padding)
            points.extend([x, y])
            self.points.append((x - 5, y - 5))
        print(points)
        print(self.points)
        return points

    def on_touch_down(self, touch):
        for index, point in enumerate(self.points):
            x, y = point
            if x <= touch.x <= x + 10 and y <= touch.y <= y + 10:
                self.show_popup(index)
                return True
        return super(InteractiveLineChart, self).on_touch_down(touch)

    def show_popup(self, index):
        popup = Popup(title=f'Data Point {index + 1}',
                      content=Label(text=f'Value: {self.data[index]}'),
                      size_hint=(None, None), size=(200, 200))
        popup.open()

    def on_size(self, *args):
        self.canvas.clear()
        self.draw_line()

class LoadingScreen(Screen):
    pass

    def load(self, *args, **kwargs):
        print(args, kwargs)


class PlottingScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass



class LoggerReaderApp(App):
    def build(self):
        return(Builder.load_file("LoggerReader.kv"))

    def close_application(self):
        # closing application
        App.get_running_app().stop()
        # removing window
        Window.close()

if __name__ == '__main__':
    LoggerReaderApp().run()
