from random import *
from PIL import Image, ImageDraw, ImageOps
from util import *
from graphics import *
from scrappy_plotter import *

def sortlines(lines):
    print("optimizing stroke sequence...")
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x,s,r = None,1000000,False
        for l in clines:
            d = distsum(l[0],slines[-1][-1])
            dr = distsum(l[-1],slines[-1][-1])
            if d < s:
                x,s,r = l[:],d,False
            if dr < s:
                x,s,r = l[:],s,True

        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines

def visualize_turtle(lines):
    import turtle
    wn = turtle.Screen()
    t = turtle.Turtle()
    t.speed(0)
    t.pencolor('white')
    t.pd()
    for i in range(0,len(lines)):
        for p in lines[i]:
            t.goto(p[0]*640/1024-320,-(p[1]*640/1024-320))
            t.pencolor('black')
        t.pencolor('white')
    turtle.mainloop()

def visualize_graphics(lines):
    s = 3.3
    w,h = 210*s,297*s
    win = GraphWin('pic', w, h)
    # win.setCoords(0,0,w,h) # flip picture?
    for l in lines:
        prev = Point(l[0][0]*s, l[0][1]*s)
        for p in l:
            new_point = Point(p[0]*s, p[1]*s)
            e = Line(prev, new_point) 
            e.setWidth(1)
            e.draw(win)
            prev = new_point

    message = Text(Point(win.getWidth()/2, 20), 'Click anywhere to quit.')
    message.draw(win)
    win.getMouse()
    win.close()

def scale_points(lines):
    max_x, min_x, max_y, min_y = 0, 0, 0, 0 
    w, h = 210, 297 # A4 size
    # page size, scale of pic in the page, and the margins
    p_of_page = 0.85     # % of the A4 page
    offset = (1-p_of_page)/2 # margins
    w, h = w*p_of_page, h*p_of_page
    w_offset, h_offset = w*offset, h*offset
    # figure out the max points provided
    for l in lines:
        for p in l:
            if p[0] < min_x: min_x = p[0]
            if p[0] > max_x: max_x = p[0]
            if p[1] < min_y: min_y = p[1]
            if p[1] > max_y: max_y = p[1]
    # scale all the points
    w_scale, h_scale = w/max_x, h/max_y
    scale = min(w_scale,h_scale)
    scaled_lines = []
    for l in lines:
        new_line = [(int(p[0]*scale + w_offset), int(p[1]*scale + h_offset)) for p in l]
        scaled_lines.append(new_line)
    return scaled_lines

def scrappy_plotter_plot_points(lines):
    n_lines = len(lines)
    n = n_lines
    for l in lines:
        # go to first coordinate with the pen 'up'
        pen_down = False
        for p in l:
            line_to(p[0], p[1], pen_down)
            pen_down = True
        print('{} of {} lines left'.format(n, n_lines))
        n -= 1
    
def main_plot():
    linedraw.resolution = 1024 # smaller resolution creates faster compute time
    linedraw.draw_hatch = False # criss-cross shading yes/no
    linedraw.hatch_size = 8 # shading patch size (8, 16, 32, ..)
    linedraw.show_bitmap = True
    linedraw.contour_simplify = 1 # 
    
    lines = linedraw.sketch("./images/bros.jpg")
    lines = sortlines(lines)
    scaled_lines = scale_points(lines)
    visualize_graphics(scaled_lines)
    # scrappy_plotter_plot_points(scaled_lines) # make the plotter draw the picture!
    
if __name__=="__main__":
    import linedraw
    # import plotter. TODO: Make it a class
    try:
        # plotter_startup()
        main_plot()
        # plotter_finishup()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        # plotter_finishup()
        pass