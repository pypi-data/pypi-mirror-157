import numpy as np
import cv2

def draw_text(image,x,y,text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontscale = 0.3
    textsize = cv2.getTextSize(text, font, fontscale, 1)[0]
    # get coords based on boundary
    textX = round(x - textsize[0]/2) 
    textY = round(y + textsize[1]/ 2)
    cv2.putText(image, text, (textX,textY), font, fontscale, (0, 0, 0), 1, cv2.LINE_AA)


def draw_signal_aspect(width,height, signal_definition):
    
    colors = {
        "red" : (255, 0, 0, 255),
        "blue" : ( 0, 0 , 255 , 255),
        "green" : (0, 255, 0, 255),
        "yellow" : (255, 255, 0, 255),
        "white" : ( 255 , 255 , 255 , 255),
        "grey" : (50, 50, 50, 255),
        "black" :  ( 0, 0 , 0 , 255),
    }
    image = np.zeros([height,width,3],np.int32) 
    
    
    #background
    for background in signal_definition.get_background():
        p = [] 
        for x,y in background:
            p.append([round(x * width),round(y * height)])
            
        bg_color = (200,200,200,255)
        pts = np.array(p , np.int32)
        cv2.fillPoly(image,[pts],bg_color)
    
    
    #lights
    for id, geo in signal_definition.get_lights().items():
        #position
        xoff = round(width * geo['x'])
        yoff = round(height * geo['y'])
        center_coordinates = (xoff,yoff)
        radius = round(width * geo['radius'])
        signal_color = colors[geo['color']]
        cv2.circle(image, center_coordinates, radius, signal_color, -1)
        draw_text(image,xoff,yoff,id)
        
        
        
    return image

def draw_signallights(signalLights,rows , cols):
    COLORS = {}
    COLORS["red"] = (255,0,0)
    COLORS["yellow"] = (255,255,0)
    COLORS["green"] = (0,255,0)
    COLORS["white"] = (255,255,255)
    COLORS["black"] = (0,0,0)
    COLORS["blue"] = (0,255,255)

    eimg = np.zeros([rows , cols,3],dtype=np.uint8)
    eimg.fill(200) # or img[:] = 255
  
    for i in range(len(signalLights)):
        signalLight = signalLights[i]
        color_class = "black"
        for cc , _ in signalLight.getColor():
            if cc == "black": continue;
            color_class = cc
            break
        color = COLORS[color_class]
        cv2.ellipse(eimg, signalLight.getEllipse(), color , 1)
        
        
        #paint number of ellipse
        (x,y) , _, _ = signalLight.getEllipse()
        text = "{0}".format(i)
        draw_text(eimg,x,y,text)
    return eimg
