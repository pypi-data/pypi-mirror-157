class Circle:
    def __init__(self, x, y, r, vx, vy, m, color):
        self.x = x
        self.y = y
        self.r = r
        self.vx = vx
        self.vy = vy
        self.m = m
        self.color = color
    def change_attr(self, x = None, y = None,  r = None, vx = None, vy = None, m = None, color = None):
        if x!=None: self.x = x
        if y!=None: self.y = y
        if r!=None: self.r = r
        if vx!=None: self.vx = vx
        if vy!=None: self.vy = vy
        if m!=None: self.m = m
        if color!=None: self.color = color

class FreeSpaceRect:
    def __init__(self, x, y, w, h, vx, vy, m, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy
        self.m = m
        self.color = color
    def change_attr(self, x = None, y = None, w = None, h = None, vx = None, vy = None, m = None, color = None):
        if x!=None: self.x = x
        if y!=None: self.y = y
        if w!=None: self.w = w
        if h!=None: self.h = h
        if vx!=None: self.vx = vx
        if vy!=None: self.vy = vy
        if m!=None: self.m = m
        if color!=None: self.color = color

class CellRect:
    def __init__(self, row, col, vrow, vcol, m, color):
        self.row = row
        self.col = col
        self.vrow = vrow
        self.vcol = vcol
        self.m = m
        self.color = color
    def change_attr(self, row = None, col = None, vrow = None, vcol = None, m = None, color = None):
        if row!=None: self.row = row
        if col!=None: self.col = col
        if vrow!=None: self.vrow = vrow
        if vcol!=None: self.vcol = vcol
        if m!=None: self.m = m
        if color!=None: self.color = color    
