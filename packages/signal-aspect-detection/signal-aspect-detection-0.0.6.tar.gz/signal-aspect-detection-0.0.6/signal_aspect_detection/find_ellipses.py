import cv2

def find_ellipses(image):
    threshold = 100
    canny_output = cv2.Canny(image, threshold, threshold * 2)
 
    contours, _ = cv2.findContours(canny_output, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE) #cv2.RETR_TREE
    ellipses = []
    for i, c in enumerate(contours):
        
        if c.shape[0] > 5:
            ellipse = cv2.fitEllipse(c)
            ellipses.append(ellipse)
            
    return ellipses
