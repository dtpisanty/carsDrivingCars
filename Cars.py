'''
A simple class that generates SVG drawings of cars based
on the distance, speed, stall time and duration of a trip.
Distance controls the width of a car's central element
Trip duration controls the car's overall height
Speed controls the polygon's skew angle
Stall time (% of time spent at 0 km/h) determines colour.

Writen by Diego Trujillo Pisanty, August 2023
diego@trujillodiego.com
trujillodiego.com
'''
import drawsvg as dw
import numpy as np

class Car:
    idx=0
    def __init__(self,distance,speed,stalled,time,size=800,maxDist=100,maxSpeed=200,maxTime=80):
        self.dist=maxDist
        self.margin=size*0.35
        self.dims=size-self.margin
        if distance<self.dist: 
            self.dist=distance
        self.maxSpeed=maxSpeed
        self.speed=maxSpeed   
        if speed<self.speed:
            self.speed=speed
        self.time=maxTime
        if time<self.time:
            self.time=time

        distFactor=(0.8*self.dims)/maxDist
        self.box_w=distFactor*self.dist
        timeFactor=(size-185)/maxTime
        self.box_h=timeFactor*self.time
        # self.box_h=400
        self.wheels=[[self.margin+60,self.dims+self.margin-30,24],[self.dims+self.margin-60,self.dims+self.margin-30,24]]
        self.support=[self.margin,self.margin+self.dims-60-10,self.dims,5]
        baseY=self.margin+self.dims-60-15
        rTriBase=(self.dims-self.box_w)/3
        fTriBase=2*rTriBase
        rads=-((0.5*np.pi/self.maxSpeed)*self.speed)-(0.5*np.pi)
        self.rearTri=[self.margin,baseY,
                      (self.margin)+rTriBase-2.5,baseY,
                      self.margin+rTriBase-2.5-(self.box_h/np.tan(rads)),baseY-self.box_h]
        self.box=[self.margin+rTriBase+2.5-(self.box_h/np.tan(rads)),baseY-self.box_h,
             self.margin+rTriBase+self.box_w-2.5-(self.box_h/np.tan(rads)),baseY-self.box_h,
             self.margin+rTriBase+self.box_w-2.5,baseY,
             self.margin+rTriBase+2.5,baseY]
        self.frontQuad=[self.margin+rTriBase+self.box_w+2.5-((0.9*self.box_h)/np.tan(rads)),baseY-(0.90*self.box_h),
                        self.margin+rTriBase+self.box_w+2.5+(0.3*fTriBase)-((0.9*self.box_h)/np.tan(rads)),baseY-(0.90*self.box_h),
                        self.margin+self.dims,baseY,
                        self.margin+rTriBase+self.box_w+2.5,baseY]
        
        self.drawing=dw.Drawing(size,size,id_prefix='car_'+str(self.idx))
        green=255-min(255,255*stalled//(time/2))
        green=hex(int(green))[-2:]
        self.color="#ff"+green+"00"
        if 'x' in self.color:
            self.color=self.color.replace('x','0')

    def render(self,filename='car_'+str(idx)+'.svg'):
        self.drawing.append(dw.Circle(*self.wheels[0],fill='none',stroke='black',stroke_width=10))
        self.drawing.append(dw.Circle(*self.wheels[1],fill='none',stroke='black',stroke_width=10))
        self.drawing.append(dw.Rectangle(*self.support,fill='black',stroke='none'))
        self.drawing.append(dw.Lines(*self.rearTri,fill=self.color,stroke='black',close=True,stroke_width=2))
        self.drawing.append(dw.Lines(*self.box,fill=self.color,stroke='black',close=True,stroke_width=2))
        self.drawing.append(dw.Lines(*self.frontQuad,fill=self.color,stroke='black',close=True,stroke_width=2))
        self.drawing.save_svg(filename)