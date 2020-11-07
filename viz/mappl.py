import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import os
print(os.getcwd())
import transform


class Map:
    """docstring for ."""

    def __init__(self, ops, title):
        self.width = 20
        self.height = 10
        self.fig, self.ax = plt.subplots(nrows = 1, ncols = 1, figsize=(self.width,self.height))

        self.nodes = []
        self.edges = []
        self.timestamp = []
        self.conv = transform.GPSConverter()

        axcolor = 'lightgoldenrodyellow'
        self.ax_date = plt.axes([0.1, 0.05, 0.75, 0.03], facecolor=axcolor)
        self.sl_date = Slider(self.ax_date, 'Days', 0, 100, valinit=0, valstep = 1)
        self.ax_daytime = plt.axes([0.01, 0.5, 0.06, 0.15], facecolor=axcolor)
        self.radio = RadioButtons(self.ax_daytime, ('day', 'night'), active=0)
        self.ax.set_xlim([2450000,2850000])
        self.ax.set_ylim([1050000,1300000])
        self.im = plt.imread("ch.jpg")

        ratio = 1582.0/974.0
        scale = 0.926
        width = scale*400000
        height = width/ratio
        shiftx = 2470000
        shifty = 1074500
        imext = [shiftx, shiftx+width, shifty, shifty+height]
        print(imext)
        #imext_y = [1050000,1300000]
        self.ax.imshow(self.im, extent = imext)

    def plotgraph(self, ops):
        x, y = self.conv.WGSlist2CH(ops['y'], ops['x'])
        self.nodes.append(self.ax.scatter(ops['x'], ops['y'], s=10, c = 'r'))
        plt.show(block=False)

    def plotedges(self, ops):
        #loop ove rall points and plot incident lists
        for startingpoint in ops['ID']:
            #plot all edges in incidence list to points not covered yet
            #plot line to point if target> self index
            IL = ops['IL'][startingpoint]
            #print("IL", IL)
            for target in IL:
                #if(target >startingpoint):
                #plot line
                xline = [ ops['x'][ops['ID'].index(startingpoint)], ops['x'][ops['ID'].index(target)] ]
                yline = [ ops['y'][ops['ID'].index(startingpoint)], ops['y'][ops['ID'].index(target)] ]
                #x, y = self.conv.WGSlist2CH(yline, xline)

                if(xline[0] != 0 and xline[1] != 0):
                    self.edges.append(self.ax.plot(xline, yline, linewidth = 1, c = 'k'))

            #print("starting point idx", startingpoint, IL)
        plt.show(block=False)

    def activatebuttons(self):
        def dateupdate(date):
            if len(self.timestamp):
                self.timestamp[0].remove()
            print("called")
            print("date", date)
            self.timestamp.append(self.ax.text(47, 8.25,str(date)))
        self.sl_date.on_changed(dateupdate)
#precompute coarsness levels.
