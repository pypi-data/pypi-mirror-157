import math
import numpy as np

def diff_radius(a,b):
    return np.abs(math.log10(math.pow(a,2) / math.pow(b,2)))

def diff_xy(a,b):
    x1,y1 = a
    x2,y2 = b
    xd = x2 - x1
    yd = y2 - y1
    return math.sqrt( xd * xd + yd * yd)

def diff_color(definition_color,colors):
    cd = 0.0
    for color_class , percent in colors:
        if color_class != definition_color: 
            cd += percent
    return cd

def check_light(signal,x,y,radius,colors):
    matches = []

    #print("check_light",x,y,radius,colors)

    for key , definition in signal.get_lights().items():

        xyd = diff_xy((definition['x'],definition['y']),(x,y))
        rd = diff_radius(definition['radius'],radius)
        cd = diff_color(definition['color'],colors)
        if cd < 0.9999999: #have to match with color
            #("check lamp",key,"xyd",xyd,"rd",rd,"cd",cd,"match",xyd < 0.25,rd < 0.5,cd < 0.7)
        #if xyd < 0.25 and rd < 0.5 and cd < 0.70:
        #print("check lamp",key,"xyd",xyd,"rd",rd,"cd",cd,"match",xyd < 0.25,rd < 0.7 ,cd < 0.8)
        #if xyd < 0.25 and rd < 0.7 and cd < 0.80:
            matches.append((key,xyd,rd,cd))
    return matches


