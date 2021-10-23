class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def mag(self):
        return((self.x**2+self.y**2)**0.5)
    def print(self, n=3):
        print('({}, {})'.format(round(self.x,n), round(self.y,n)))
        return self
    def format(self, n=3):
        return '('+str(round(self.x,n))+','+str(round(self.y,n))+')'
    def add(self, v):
        self.x += v.x
        self.y += v.y
        return self
    def sub(self, v):
        self.x -= v.x
        self.y -= v.y
        return self
    def mult(self, s):
        self.x *= s
        self.y *= s
        return self
    def div(self, s):
        self.x /= s
        self.y /= s
        return self
    def dup(self):
        return Vector(self.x, self.y)
    def copy(self, v):
        self.x = v.x
        self.y = v.y
        return self
    def equal(self, v):
        return (self.x==v.x and self.y==v.y)
    def normalize(self):
        m = self.mag()
        if m==0: 
            return self
        self.x, self.y = self.x/m, self.y/m
        return self
# limit value to min and max
def limit(v, min_v, max_v):
    v = min_v if v<min_v else v
    v = max_v if v>max_v else v
    return v

# creates array of midpoints between v1 and v2, with 'segment_length' between them
def get_midpoints(v1, v2, segment_length):
    line_length = abs(v2.dup().sub(v1).mag())
    number_of_segments = round(line_length / segment_length)
    if number_of_segments == 0: 
        return []
    k = 1/number_of_segments
    ''' # DEBUG PRINTS
    v1.print()
    v2.print()
    print('line length = ',line_length)
    print('segment length = ', segment_length)
    print('number of segments = ', number_of_segments)
    print('k = ',k)
    '''
    # create midpoints array
    midpoints = []
    for i in range (number_of_segments):
        curr_k = k*i
        midpoints.append(Vector(v1.x + curr_k*(v2.x-v1.x), v1.y + curr_k*(v2.y-v1.y)))
    # end of the array should always be the second vector
    if(not midpoints[len(midpoints)-1].equal(v2)):
        midpoints.append(v2.dup())
    return midpoints

def print_midpoints(midpoints):
    for m in midpoints:
        m.print()
        
def sign(a):
    return 1 if a>0 else -1 if a<0 else 0