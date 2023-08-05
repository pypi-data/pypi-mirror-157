import cv2
import numpy as np
import json

signal_colors = {
    "red" : (255, 0, 0, 255),
    "green" : (0, 255, 0, 255),
    "yellow" : (255, 255, 0, 255),
    "white" : ( 255 , 255 , 255 , 255),
    "grey" : (50, 50, 50, 255),
    "black" : (0,0,0,255)
}

class Signal:
    """A signal  class"""
    def __init__(self,model):
        self.model = model

    def get_aspects(self):
        return self.model['aspects']

    def get_background(self):
        return self.model['construct']['background']

    def get_lights(self):
        return self.model['construct']['lights']

    def draw_signal_aspect(self,image,start_point, size ,aspect):
    
        x1,y1 = start_point
        construct = self.model['construct']
        
        #background
        for background in construct['background']:
            p = [] 
            for x,y in background:
                p.append([round(x1 + x * size),round(y1 + y * size)])
                
            bg_color = signal_colors['black']
            pts = np.array(p , np.int32)
            cv2.fillPoly(image,[pts],bg_color)
        
        #lights
        aspect = self.model['aspects'][aspect]
        for id, geo in construct['lights'].items():
            #position
            xoff = round(size * geo['x'])
            yoff = round(size * geo['y'])
            center_coordinates = (x1 + xoff, y1 + yoff)
            radius = round(size * geo['radius'])
            signal_color = signal_colors['grey']
            if id in aspect and aspect[id] == "on":
                signal_color = signal_colors[geo['color']]

            cv2.circle(image, center_coordinates, radius, signal_color, -1)


def load_signal(filename):
    with open(filename) as json_file:
        model = json.load(json_file)
        return Signal(model)