import numpy as np

def count_pixel(v):
    result = []
    cnt = 0
    last = -1
    for i in range(len(v)):
        if v[i] != last:
            if cnt > 0:
                result.append((last,cnt))
            last = v[i]
            cnt = 0
        cnt += 1
                
    result.append((last,cnt))
    return result

def calculate_line(v):
    s = -1
    e = -1
    c = 0
    pos = 0
    w = 0
    for px , cnt in v:
        if px == 255:
            if s == -1:
                s = pos
            e = pos + cnt - 1
            c += cnt
        pos += cnt
        w += cnt
    return s , c , e ,w
    
def is_line_of_signal(v):
    min , cnt , max , w = calculate_line(v)
    border = w - min - max
    
    if cnt < border: return False
    if cnt < w/3: return False
    return True

   
def combine_ranges(r1,r2):
    boxes = []
    pos1 = 0
    for px1 , cnt1 in r1:
        if px1 == 255 and cnt1 > 5:
            s1 = pos1
            e1 = pos1 + cnt1 - 1
            pos2 = 0
            for px2 , cnt2 in r2:
                if px2 == 255 and cnt2 > 5:
                    s2 = pos2
                    e2 = pos2 + cnt2 - 1
                    boxes.append((s1,e1,s2,e2))
                pos2 += cnt2
        pos1 += cnt1
    return boxes

def crop_image_line(imageAccessor, thres_width , threas_thickness):   #sr - scan rows
    
    thickness = 0
    line_length = imageAccessor.get_line_length()
    lines_cnt = imageAccessor.get_lines_cnt()
    min_width = round(line_length * thres_width)
    min_thickness = round(lines_cnt * threas_thickness)
    max_hole_size = 11
    min_area_size = 13
    h = []
    for line in range(lines_cnt):
        v = []
        for x in range(line_length):
            b = imageAccessor.get_bin(line,x)  
            v.append(b)

        # test line 
        #print("v",v)
        r = count_pixel(v)
   
        pixel = 0        
        if is_line_of_signal(r): 
            pixel = 255
        h.append(pixel)
    
    return count_pixel(h)

