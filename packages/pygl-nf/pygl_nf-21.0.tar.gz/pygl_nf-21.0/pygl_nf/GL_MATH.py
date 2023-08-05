import math
import random
import pygame

def Mod(num):
    if num < 0:num = -num
    return num


class Math_:

    def __init__(self):
        pass

    def COS(self,ugl):
        return math.cos(ugl)

    def SIN(self,ugl):
        return math.sin(ugl) 

    def RAST(self,pos1=[],pos2=[]):
        if pos1[0]>pos2[0]:w = pos1[0]-pos2[0]
        else:              w = pos2[0]-pos1[0]
        if pos1[1]>pos2[1]:h = pos1[1]-pos2[1]
        else:              h = pos2[1]-pos1[1]
        dl = math.sqrt(w*w+h*h)
        return dl

    def ANGLE_TO(point1,point2):
        radians = math.atan2(point1[0]-point2[0],point1[1]-point2[1])
        angle = (360*radians)/(2*math.pi)
        if angle<0:
            angle=360+angle
        return angle

    def SRED(listing):
        sum = 0
        for num in listing: sum+=num
        return sum/len(listing)
        

class Vec2_:
    def __init__(self,points) -> None:
        self.vector = pygame.math.Vector2(points)
        
    def Rotate(self,angle):
        self.vector.rotate_ip(angle)

    def x(self):
        return self.vector.x

    def xx(self):
        return self.vector.xx

    def y(self):
        return self.vector.y

    def yy(self):
        return self.vector.yy

    def xy(self):
        return self.vector.xy

    def Normalize(self,New:bool=False):
        if New:
            return Vec2_( self.vector.normalize() )
        elif not New:
            self.vector = self.vector.normalize()

    def Rotate_rad(self,angle):
        self.vector.rotate_ip_rad(angle)

    def Angle_to(self,vector) -> float:
        ang = self.vector.angle_to(vector.vector)
        if ang-45<0: ang = 360+ang
        return ang - 45

    def Lenght(self) -> float:
        return self.vector.length()

    def Lenght_Squared(self) -> float:
        return self.vector.length_squared()

    def Is_normalised(self) -> bool:
        return self.vector.is_normalized()

    def Cross(self,vector):
        return self.vector.cross(vector.vector)

    def Scale(self,value):
        self.vector.scale_to_length(value)

    def Sum(self,vector):
        pos = [self.vector.x+vector.vector.x,self.vector.y+vector.vector.y]
        self.vector = pygame.math.Vector2(pos)




