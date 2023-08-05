#!/usr/bin/env python
#
# This module define the object Vector2
# This is a 2 dimension vector based on Euclid/Descarte geometry
#
#
# Loosely based on the work of Alex Holkner
# Original name: "euclid.py"
# Alex.Holkner@mail.google.com
#
# ---- Licence and money  ########
# Author : Simon Zozol, simon.zozol@gmail.com
# This work is under CC0 licence. This is mostly equivalent to public domain.
# The spirit is that you do whatever you want and I deny any responsibility if it somehow backfire.
# That said, I would appreciate if you would keep the result as open source.
# And I would even more appreciate if you could donate me a little something :
# Tipee : https://www.tipeee.com/holy-python
# Paypal : https://www.paypal.com/us/cgi-bin/webscr?cmd=_send-money&nav=1&email=simon.zozol@gmail.com

import math

# Usage:
#  @enforce_vector2(1,2)
#  def myFunction(lapse, position, speed):
#    suite
# The decorator will convert parameter 1 and 2 (position and speed) into Vector2 if needed
# So, myFunction(2,[1,1],(2,2))  will work properly. And myFunction can assume the input parameter to be Vector2 type
# This is very convenient, but has high execution time. Feel free to remove all the @enforce_vector2
# until I find a solution
# THIS SUPPORT ONLY POSITIONAL EXPLICIT ARGUMENTS
from functools import wraps
def enforce_vector2 (*arg_positions):

    def real_decorator(function):
        @wraps(function)   # for proper introspection
        def __enforce_vector2(*args, **kwargs):
            newargs = list(args)
            for argPos in arg_positions:
                newargs[argPos] = convert_as_vector2(newargs[argPos])
                if newargs[argPos] is None:  # if conversion failed
                    original_type = type(args[argPos]).__name__
                    raise TypeError("can not convert '"+original_type+"' as 'Vector2'")

            return function(*newargs, **kwargs)
        return __enforce_vector2
    return real_decorator


class Vector2:
    __slots__ = ['x', 'y']

    def __init__(self, x, y=None):
        """ Normal constructor has 2 parameters: x and y
            If only one parameter is given, Vector2(spam) tries to convert spam into a Vector2  """
        if y is None:
            temp = convert_as_Vector2(x)
            
            self.x = temp.x
            self.y = temp.y
        else:
            self.x = x
            self.y = y

    def __copy__(self):
        return self.__class__(self.x, self.y)
    copy = __copy__

    def __deepcopy__(self):
        try:
            x = self.x.__deepcopy__()
        except:
            # TODO This work for int and float, but it doesn't feel like canonical
            x = self.x

        try:
            y = self.y.__deepcopy__()
        except:
            y = self.y
            
        return self.__class__(x, y)
    deepcopy = __deepcopy__

    def __repr__(self):
        return 'Vector2({}, {})'.format(repr(self.x), repr(self.y))

    def __str__(self):
        return 'Vector2({}, {})'.format(str(self.x), str(self.y))

    @enforce_vector2(1)
    def __eq__(self, other):
            return self.x == other.x and self.y == other.y

    @enforce_vector2(1)
    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.x != 0 or self.y != 0

    def __len__(self):
        return 2

    __bool__ = __nonzero__

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    # thanks to this, you can write  x,y = myVector
    def __iter__(self):
        return iter((self.x, self.y))

    @enforce_vector2(1)
    def __add__(self, other):
            return Vector2(self.x + other.x,
                           self.y + other.y)

    __radd__ = __add__  # called when trying tuple + Vector2

    # operator +=
    # through pythonic magic, tuple+=Vector2 works (result is a Vector2)
    @enforce_vector2(1)
    def __iadd__(self, other):
            self.x += other.x
            self.y += other.y
            return self

    @enforce_vector2(1)
    def __sub__(self, other):
        """  Vector2 - something --> Vector2 """
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)

    @enforce_vector2(1)
    def __rsub__(self, other):
            """  "(1,1) - Vector2(2,2)" is equivalent to "__rsub__(Vector2(2,2),(1,1))"
              Before the "real" call, @enforce_vector2(1) will convert the tuple in a Vector2"""
            return Vector2(other.x - self.x,
                           other.y - self.y)
    
    def __mul__(self, other):
        return Vector2(other * self.x,
                       other * self.y)

    # __rmul__ is typically called for float * Vector2 
    __rmul__ = __mul__

    def __imul__(self, other):
        """ operator *=
           allow writing :
           spam=Vector2(3,4); foo=2; spam *= foo; foo *= spam"""
        self.x *= other
        self.y *= other
        return self

    def __floordiv__(self, other):
        assert type(other) in (int, float)
        return Vector2(operator.floordiv(self.x, other), operator.floordiv(self.y, other))

    def __truediv__(self, other):
        assert type(other) in (int, float)
        return Vector2(operator.truediv(self.x, other), operator.truediv(self.y, other))

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    __pos__ = __copy__
    
    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
        #   I return None to avoid ambiguity with normalized

    def normalized(self):
        d = self.magnitude()
        if d:
            return Vector2(self.x / d, 
                           self.y / d)
        return self.copy()

    @enforce_vector2(1)
    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self):
        return Vector2(self.y, -self.x)

    @enforce_vector2(1)
    def angle(self, other):
        """Return the angle to the vector other. result in the range [0, 2*pi]"""
        # return math.acos(self.dot(other) / (self.magnitude()*other.magnitude()))
        return math.atan2(self.x*other.y-other.x*self.y,
                          self.x*other.x+self.y*other.y)

    def angle_to_x_axis(self):
        """Return the angle to the vector (1,0)"""
        return math.atan2(self.y, self.x)

    @enforce_vector2(1)
    def reflect(self, normal):
        # assume normal is normalized  TODO: do not assume if it makes sense
        d = 2 * (self.x * normal.x + self.y * normal.y)
        return Vector2(self.x - d * normal.x,
                       self.y - d * normal.y)
    
    @enforce_vector2(1)
    def project(self, other):
        """Return one vector projected on the vector other"""
        n = other.normalized()
        return self.dot(n)*n


def check_vector_valid(vector):
    """vaguely check if vector.x and vector.y are number like (does x+y give numeric value?) """
    assert (type(vector.x+vector.y) in [int, float])
    

def convert_as_vector2(something):
    """    if something is not a vector2, this function try to convert it.
      It return an vector2d.Vector2 object if possible or None if not possible
      If "something" is a Vector2 function return the object, not its copy """
    if isinstance(something, Vector2):  # TODO: à tester
        return something
    try:
        result = Vector2(something[0], something[1])   
        check_vector_valid(result)
        return result
    except:
        try:
            result = Vector2(something.getX(), something.getY())
            check_vector_valid(result)
            return result
        except:
            try:
                # If this one fail too, None is return
                result = Vector2(something.x, something.y)
                check_vector_valid(result)
                return result
            except AttributeError:
                return None

if __name__ == "__main__":
    spam = Vector2(1,3)
    spam += (2,1)
    print(spam)

    #problem : the current decorator do not allow named arguments
    spam.__add__(other=(1,0))
