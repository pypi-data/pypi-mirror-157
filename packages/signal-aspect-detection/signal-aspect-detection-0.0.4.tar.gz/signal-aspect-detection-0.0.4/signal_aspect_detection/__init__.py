VERSION = (0, 0, 2, "f") # following PEP 386
DEV_N = None


def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        if DEV_N:
            version = "%s.dev%s" % (version, DEV_N)
    return version

__version__ = get_version()

import cv2

def create_binary(image,val):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    if val != -1:
        thresh = cv2.threshold(blurred, val, 255, cv2.THRESH_BINARY)[1]
    else:
        thresh = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    threshi = cv2.bitwise_not(thresh)
    return threshi

from .crop_image_line import crop_image_line , combine_ranges
from .image_accessor_class import HorizontalImageAccessor , VerticalImageAccessor

def crop_signal(image):

    #thresholds mindestbreit 50% 
    width , thickness = 0.5 , 0.8

    r1 = crop_image_line(VerticalImageAccessor(image),width , thickness)
    r2 = crop_image_line(HorizontalImageAccessor(image),width , thickness)
    
    boxes = combine_ranges(r1,r2)
    
    print("crop",r1,r2)
    print("boxes",boxes)
    
    max_box = (-1,-1,-1,-1)
    max_size = 0

    for box in boxes:
        sz = (box[1] - box[0]) *  (box[3] - box[2]) 
        if sz > max_size:
            max_box = box
            max_size = sz
    
    return max_box


from .find_ellipses import find_ellipses
from .color_detector import get_ellipse_color
from .light_class import SignalLight

def find_lights(image):
    ellipses = find_ellipses(image)

    signalLigths = []
    for ellipse in ellipses:
        (x , y) , (xax,yax) , angle = ellipse
        
        color_class = get_ellipse_color(image,x,y,xax,yax,angle)
        #print("color_class",color_class,x,y,xax,yax,angle)
        signalLight = SignalLight(ellipse,color_class)
        signalLigths.append(signalLight)

    return signalLigths


def filter_lights(signalLights,height , width):
    filteredSignalLights = []
    for signalLight in signalLights:
        
        #zu klein
        if signalLight.getCircleRadius() <= 2: #prevent devision by zero
            continue
       
        colors = signalLight.getColor()
        (x,y) = signalLight.getXY() 
        radius = round(signalLight.getExpansion() / 2)

        
        #zu groß
        
        #partly outside
        
        if x - radius < 0: continue
        if y - radius < 0: continue
        if x + radius > width: continue
        if y + radius > height: continue

        #only black
        if len(colors) == 1 and colors[0][0] == 'black': #no matching expected
            continue
        
        filteredSignalLights.append(signalLight)
    return filteredSignalLights


from .signal_matching import check_light
def find_matches(signalLigths,image_width,image_height,signal):
    lights = []
    matches = []
    for signalLigth in signalLigths:
        
        if signalLigth.getCircleRadius() <= 2: #prevent devision by zero
            lights.append([])
            continue

        colors = signalLigth.getColor()
        (x,y) = signalLigth.getXY() 
        radius = round(signalLigth.getExpansion() / 2)

        #find matches for signal
        matches = check_light(signal,x/image_width,y/image_height,radius/image_width,colors)

        #match = filter_matches(match,0.25,0.7,0.8)
        #print("match",x/image_width,y/image_width,radius/image_width,colors,match,signalLigth.getCircleRadius())

        #validate (maximal one match should be possible)
        #if len(match) > 1:
        #    raise Exception("Multiple matches "+str(match))

        #add the match
        lights.append(matches)

    return lights
    

def filter_matches(matches,xyl,rl,cl):
    filtered_matches = []
    for light_match in matches:
        match = []
        for m in light_match:
            _key,xyd,rd,cd = m
            if xyd < xyl and rd < rl and cd < cl:
                match.append(m)
        if len(match) > 1:
            raise Exception("Multiple matches "+str(match))
        if len(match) == 1:
            filtered_matches.append(match[0])
    return filtered_matches

def find_aspect(lights,signal):

    #convert matches to list
    lights_list = []
    for match in lights:
        lights_list.append(match[0])


    for key , definition in signal.get_aspects().items():

        # convert aspects to array, validate value "on"
        aspects_lights = []
        for light , state in definition.items():
            if state != "on": 
                raise Exception("state "+state+" is not implemented")
            aspects_lights.append(light)

        #test if match
        lights_list = list(set(lights_list))
        if sorted(aspects_lights)==sorted(lights_list):
            return key

    return None


from .draw import draw_signallights
from .draw import draw_signal_aspect

def detect_lights(original,signal_definition,crop_image = True):

    # resize image
    original_height , original_width , _ = original.shape
    width = 100 
    height = int(original_height * width / original_width)
    dim = (width, height)
  
    # resize image
    I = cv2.resize(original, dim, interpolation = cv2.INTER_AREA)
    
    bin_image = create_binary(I,-1)
    rows , cols , _ = I.shape


    if crop_image:
        (left,right,top,bottom) = crop_signal(bin_image)
        
        print("crop",(left,right,top,bottom))
        
        #fix crop if not found #deprecated
        if left == -1: left = 0
        if right == -1: right = cols
        if top == -1: top = 0
        if bottom == -1: bottom = rows
        
        crop_img = I[top:bottom, left:right]
    else:
        crop_img = I
    
    images = [I, bin_image,crop_img]

    #detect bulbs in cropped image
    signalLights = find_lights(crop_img)

    rows , cols , _ = crop_img.shape

    filteredSignalLights = filter_lights(signalLights,rows , cols)

    light_matches = find_matches(filteredSignalLights,cols,rows,signal_definition)

    eimg = draw_signallights(signalLights,rows , cols)
    images.append(eimg);
    
    e2img = draw_signallights(filteredSignalLights,rows , cols)
    images.append(e2img);
    
    i = draw_signal_aspect(cols,rows,signal_definition)
    images.append(i);
    
    return filteredSignalLights ,  light_matches , images
