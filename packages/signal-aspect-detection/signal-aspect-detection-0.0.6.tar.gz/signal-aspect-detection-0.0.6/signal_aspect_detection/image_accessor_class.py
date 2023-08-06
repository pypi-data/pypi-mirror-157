class ImageAccessor:
    """A image accessor class"""
    def __init__(self,image):
        self.image = image
        self.rows , self.columns = image.shape[0] , image.shape[1]

    def _extract_rgb(color):
        return (color[0] , color[1] , color[2])

    def _extract_bin(color):
        return color

    def get_rgb(self,line,pos):
        raise NotImplementedError

    def get_bin(self,line,pos):
        raise NotImplementedError

    def get_lines_cnt(self):
        raise NotImplementedError

    def get_line_length(self):
        raise NotImplementedError


class HorizontalImageAccessor(ImageAccessor):

    def get_lines_cnt(self):
        return self.rows

    def get_line_length(self):
        return self.columns

    def get_rgb(self,line,pos):
        return ImageAccessor._extract_rgb(self.image[line,pos])

    def get_bin(self,line,pos):
        return ImageAccessor._extract_bin(self.image[line,pos])


class VerticalImageAccessor(ImageAccessor):

    def get_lines_cnt(self):
        return self.columns

    def get_line_length(self):
        return self.rows

    def get_rgb(self,line,pos):
        return ImageAccessor._extract_rgb(self.image[pos,line])
    
    def get_bin(self,line,pos):
        return ImageAccessor._extract_bin(self.image[pos,line])