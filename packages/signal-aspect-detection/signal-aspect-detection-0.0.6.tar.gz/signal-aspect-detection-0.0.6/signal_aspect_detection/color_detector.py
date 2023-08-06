import skimage
import numpy as np
import math
import cv2

from sklearn.cluster import KMeans
# https://scikit-learn.org/stable/modules/clustering.html

def cluster(L,a,b,n_clusters):
    X = []
    for i in range(len(L)):
        X.append([L[i],a[i],b[i]])


    #X = np.array([[1, 2], [1, 4], [1, 0],[10, 2], [10, 4], [10, 0]])
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(np.array(X))
    #print(kmeans.cluster_centers_)
    #print(len(kmeans.labels_),len(X))

    Lc, ac, bc = map(list, zip(*kmeans.cluster_centers_))

    cl_size = []
    for cl in range(len(kmeans.cluster_centers_)):
        lst = np.where(kmeans.labels_ == cl)[0]
        cnt = len(lst)
        cl_size.append(cnt)
    return Lc, ac , bc , cl_size


def get_ellipse_color(img,x,y,xax,yax,angle):
    

    max = np.max([xax,yax])
    x1 = round(x - max/2)
    x2 = round(x + max/2)
    y1 = round(y - max/2)
    y2 = round(y + max/2)
    if x1 < 0: x1 = 0
    if y1 < 0: y1 = 0
    
    if xax < 1 or yax < 1:
        return [ (get_lab_color_class(0,0,0) , 1.0) ]#black

    clipped_image = img[y1:y2, x1:x2]
    clipped_ellipse = (x-x1,y-y1) , (xax,yax) , angle
    
    rows , columns, _ = clipped_image.shape

    # create a mask image of the same shape as input image, filled with 0s (black color)
    #mask = np.zeros_like(clipped_image)
    if rows == 0 or columns == 0:
        print("cannot create image with dimension", rows,columns,x,y,xax,yax)
        return [ (get_lab_color_class(0,0,0) , 1.0) ]#black

    mask = np.zeros([rows , columns,3],dtype=np.uint8)

    # create a white filled ellipse
    #print("clipped_ellipse",clipped_ellipse,"size",rows , columns)

    mask=cv2.ellipse(mask, clipped_ellipse, color=(255,255,255), thickness=-1)


    av = []
    bv = []
    Lv = []
    for i in range(rows):
        for j in range(columns):
            color_mask = mask[i,j]
            if (color_mask == (0,0,0)).all(): # black
                #ignore
                continue
            if (color_mask != (255,255,255)).any(): # white
                raise Exception("unknown mask color "+color_mask)

            pixel_color = clipped_image[i,j]
            red , green , blue = pixel_color[0] , pixel_color[1] , pixel_color[2]
            L , a , b = skimage.color.rgb2lab((red,green,blue))
            av.append(a)
            bv.append(b)
            Lv.append(L)
                
    if len(Lv) == 0: 
        return [ (get_lab_color_class(0,0,0) , 1.0) ]#black
    
    if len(Lv) == 1: 
        return [ (get_lab_color_class(Lv[0],av[0],bv[0]) , 1.0)]

    n_cluster = 5;

    if len(Lv) < n_cluster:
        n_cluster = len(Lv)

    Lc, ac , bc , cl_size = cluster(Lv,av,bv,n_cluster)



    data = {}
    for ix in range(len(Lc)):
        color_class = get_lab_color_class(Lc[ix],ac[ix],bc[ix])
        percent = cl_size[ix] / len(Lv)
        
        #print(ix,"size=",cl_size[ix],"p",percent,"Lab",Lc[ix], ac[ix],bc[ix],"color",color_class)

        v = 0.0
        if color_class in data:
            v = data[color_class]
        data[color_class] = percent + v
    
    result = list(data.items())

    result.sort(key=lambda tup: tup[1], reverse=True)

    return result


color_limit = 20
brightness_limit = 50
def get_lab_color_class(L,a,b):
    if np.abs(a) < color_limit and np.abs(b) < color_limit:
        if L < brightness_limit:
            return "black"
        return "white"

    if np.abs(b) > np.abs(a):
        if b <= -color_limit: 
            return "blue"
        if b >=  color_limit: 
            return "yellow"
    else:
        if a <= -color_limit: 
            return "green"
        if a >=  color_limit: 
            return "red"

    raise Exception("cannot classify color")

def get_pixel_color_class(pixel_color):

    print("pixel",pixel_color,type(pixel_color),type(pixel_color[0]))

    red , green , blue  = pixel_color[0] , pixel_color[1] , pixel_color[2]
    L , a , b = skimage.color.rgb2lab((red,green,blue))
    #print("rgb",red , green , blue,"Lab",L,a,b)
    return get_lab_color_class(L,a,b)

