import math
import numpy as np

class SignalLight:
    """A signal light class"""
    def __init__(self,ellipse,color_class):
        self.ellipse = ellipse
        self.color_class = color_class

    def getEllipse(self):
        return self.ellipse

    def getXY(self):
        (x,y) , _ , _ = self.ellipse
        return (x,y)

    def getColor(self):
        return self.color_class

    def getCircleRadius(self):
        _ , (xax,yax) , _ = self.ellipse
        return math.sqrt(xax * yax)

    def getExpansion(self): 
        _ , (xax,yax) , _ = self.ellipse
        return np.max([xax,yax])
    
    def getFlatness(self):
        _ , (xax,yax) , _ = self.ellipse
        return np.max([xax,yax]) / np.min([xax,yax])



