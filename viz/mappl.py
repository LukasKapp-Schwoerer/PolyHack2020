import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colorbar
from matplotlib.widgets import Slider, Button, RadioButtons
import os
print(os.getcwd())
from viz import transform
from datetime import date
from matplotlib.axes._axes import _log as matplotlib_axes_logger

matplotlib_axes_logger.setLevel('ERROR')

class Map:
    """docstring for ."""
    def __init__(self, points, extractor, title):
        self.extractor = extractor
        self.width = 20
        self.height = 10
        self.fig, self.ax = plt.subplots(nrows = 1, ncols = 1, figsize=(self.width,self.height))

        self.points = points
        #extract locations and incidence lists
        x_coords = []
        y_coords = []
        ids = []
        incidence_list = {}
        for point in points.values():
            ids.append(point.id_index)
            x_coords.append(point.gps[0])
            y_coords.append(point.gps[1])
            incidence_list[point.id_index] = []

            for connection in point.connections_outbound:
                incidence_list[point.id_index].append(points[connection.to_op].id_index)

        self.ops = {'ID': ids,
              'x': x_coords,
              'y': y_coords,
              'IL': incidence_list}

        self.nodes = 0
        self.edges = []
        self.congestededges = []
        self.congestvertices = []
        self.timestamp = []
        self.iscbar = 0

        #axcolor = 'lightgoldenrodyellow'
        axcolor = 'w'
        self.ax_date = plt.axes([0.23, 0.03, 0.2, 0.03], facecolor=axcolor)
        self.sl_date = Slider(self.ax_date, 'Start', 2019, 2040, valinit=2019, valstep = 0.25)
        self.ax_wind = plt.axes([0.55, 0.03, 0.1, 0.03], facecolor=axcolor)
        self.sl_window = Slider(self.ax_wind, 'Length', 1, 5, valinit=1, valstep = 0.25)
        self.constructionduration = 2 #one year
        self.range_start = date(2019,1,1)
        self.range_end = date(2019+self.constructionduration, 1, 1)
        self.ax_daytime = plt.axes([0.01, 0.5, 0.06, 0.15], facecolor=axcolor)
        self.radio = RadioButtons(self.ax_daytime, ('day', 'night'), active=0)
        self.resetax = plt.axes([0.75, 0.03, 0.06, 0.03])
        self.button = Button(self.resetax, 'Compute', color=axcolor, hovercolor='0.975')

        self.ax.set_xlim([2450000,2850000])
        self.ax.set_ylim([1050000,1300000])
        self.im = plt.imread("viz/ch.jpg")

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

    def plotgraph(self,):
        ops = self.ops
        self.nodes = self.ax.scatter(self.ops['x'], ops['y'], s=2, c = 'k', alpha = 0.5)
        plt.show(block=False)

    def plotedges(self):
        ops = self.ops
        plotted_edges = []
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
                if(target>= startingpoint):
                    edgetup = [startingpoint, target]
                else:
                    edgetup = [target, startingpoint]
                if((xline[0] != 0 and xline[1] != 0) and (edgetup not in plotted_edges)):
                    self.edges.append(self.ax.plot(xline, yline, linewidth = 2, c = 'k', alpha = 0.3))
                    plotted_edges.append(edgetup)

            #print("starting point idx", startingpoint, IL)
        plt.show(block=False)

    def plotcongestions(self, ccgs):
        points = self.points

        #extract all congestion values for color map
        conj = []
        throughput = []
        for ccg in ccgs:
            conj.append(ccg.congestion.passenger_congestion)
            throughput.append(ccg.congestion.passenger_trains)

        minconj = np.min(conj)
        maxconj = np.max(conj)

        throughput = 0.2 + np.array(throughput)*5.0/np.max(throughput)
        #print("conj", conj)
        if(np.sum(conj)):
            #print("sum",np.sum(conj))
            colors = cm.autumn((maxconj-conj)*1.0/maxconj)
        else:
            colors = cm.autumn(np.array(conj)+1)
        #print((maxconj-conj)*1.0/maxconj)
        #print(colors)

        if(not self.iscbar):
            sc = self.ax.scatter([0,0], [0,0], c = [0, 1], cmap = cm.autumn)
            self.cbarax = self.fig.add_axes([0.9, .1, 0.02, 0.7])
            self.cbar = self.fig.colorbar(sc, self.cbarax, ticks = [1, 0])
            self.cbar.ax.set_yticklabels(['0', '1'])
            self.cbar.set_label("Congestion index (normalized)")
            self.iscbar = 1

        self.annotations = []

        idx = 0
        for ccg in ccgs:
            smaller_op = points[ccg.smaller_op].gps
            greater_op = points[ccg.greater_op].gps
            x = [smaller_op[0], greater_op[0]]
            y = [smaller_op[1], greater_op[1]]
            if(x[0] != 0 and x[1] != 0):
                self.congestededges.append(self.ax.plot(x,y, color = colors[idx], linewidth = 2+throughput[idx] ))
                congestion_frac = ccg.congestion.passenger_congestion / ccg.congestion.passenger_trains
                if congestion_frac > 0:
                    congestion_text = str(congestion_frac)
                else:
                    congestion_text = "unknown"
                annotation = self.ax.annotate(f"{ccg.smaller_op} <-> {ccg.greater_op}\n" + \
                                              f"reduction fraction: {congestion_text}\n" + \
                                              f"earliest: {ccg.congestion.start_date}, latest: {ccg.congestion.end_date}",
                                              (np.mean(x), np.mean(y)),
                                              xytext=(20,20),textcoords="offset points",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
                annotation.set_visible(False)
                self.annotations.append(annotation)

            idx+=1
        self.fig.canvas.draw()



        def hover(event):
            for i in range(len(self.annotations)):
                annotation = self.annotations[i]
                artist = self.congestededges[i][0]
                vis = annotation.get_visible()
                cont, ind = artist.contains(event)
                if cont:
                    annotation.set_visible(True)
                    #cont, ind = sc.contains(event)
                    self.fig.canvas.draw_idle()
                else:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.fig.canvas.draw_idle()

        self.fig.canvas.mpl_connect("motion_notify_event", hover)

    def plotvertexcongestions(self, vcgs):

        #extract all congestion values for color map
        conj = []
        throughput = []
        xvals = []
        yvals = []
        for vcg in vcgs:
            conj.append(vcg.congestion.passenger_congestion)
            throughput.append(vcg.congestion.passenger_trains)
            xvals.append(vcg.gps[0])
            yvals.append(vcg.gps[1])

        minconj = np.min(conj)
        maxconj = np.max(conj)

        throughput = 3 + np.array(throughput)*60.0/np.max(throughput)
        #print("thorughput",throughput)
        #print("conj", conj)
        if(np.sum(conj)):
            #print("sum",np.sum(conj))
            colors = cm.autumn((maxconj-conj)*1.0/maxconj)
        else:
            colors = cm.autumn(np.array(conj)+1)
        #print("conj", conj)
        #print("colors", colors)
        #print((maxconj-conj)*1.0/maxconj)
        #print(colors)

        if(not self.iscbar):
            sc = self.ax.scatter([0,0], [0,0], c = [0, 1], cmap = cm.autumn)
            self.cbarax = self.fig.add_axes([0.9, .1, 0.02, 0.7])
            self.cbar = self.fig.colorbar(sc, self.cbarax, ticks = [1, 0])
            self.cbar.ax.set_yticklabels(['0', '1'])
            self.cbar.set_label("Congestion index (normalized)")
            self.iscbar = 1

        self.vannotations = []

        idx = 0
        self.congestvertices = []
        #self.congestvertices.append(self.ax.scatter(xvals,yvals, s = 20 ,c = colors))
        for vcg in vcgs:
            #throughput[idx]
            if(vcg.gps[0]!=0):
                self.congestvertices.append(self.ax.scatter(vcg.gps[0], vcg.gps[1], s=throughput[idx], c = colors[idx]))
                congestion_frac = 0.5
                if(vcg.congestion.passenger_trains):
                    congestion_frac = vcg.congestion.passenger_congestion / vcg.congestion.passenger_trains
                if congestion_frac > 0:
                    congestion_text = str(congestion_frac)
                else:
                    congestion_text = "unknown"

                annotation = self.ax.annotate(f"OP {vcg.id_word}\n" + \
                                              f"reduction fraction: {congestion_text}\n" + \
                                              f"earliest: {vcg.congestion.start_date}, latest: {vcg.congestion.end_date}",
                                              (xvals[idx], yvals[idx]),
                                              xytext=(20,20),textcoords="offset points",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
                annotation.set_visible(False)
                self.vannotations.append(annotation)



            idx+=1

        self.fig.canvas.draw()

        def hoverv(event):
            for i in range(len(self.vannotations)):
                annotation = self.vannotations[i]
                artist = self.congestvertices[i]
                vis = annotation.get_visible()
                cont, ind = artist.contains(event)
                if cont:
                    annotation.set_visible(True)
                    #cont, ind = sc.contains(event)
                    self.fig.canvas.draw_idle()
                else:
                    if annotation.get_visible():
                        annotation.set_visible(False)
                        self.fig.canvas.draw_idle()

        self.fig.canvas.mpl_connect("motion_notify_event", hoverv)


    def activatebuttons(self):
        def dateupdate(sliderval):
            #print(self.timestamp)
            if len(self.timestamp):
                self.timestamp[-1].remove()
                self.timestamp = []
            year = np.int(sliderval)
            month = np.int(1+11.0*(sliderval-year))
            #print("y,m", year, month)
            #print("dtype", year.dtype, month.dtype)
            self.range_start = date(year, month, 1)
            year_end = np.int(sliderval+self.constructionduration)
            month_end = np.int(1+11.0*(sliderval+self.constructionduration-year_end))
            self.range_end = date(year_end, month_end,1)
            self.timestamp.append(self.ax.text(2480000, 1245000,"Congestion: " +str(year)+"/"+str(month)+"-"+str(year_end)+"/"+str(month_end)))

        def windowupdate(val):
            self.constructionduration = val

        def computecongestion(event):
            print("computing ccg")
            range_start = self.range_start
            range_end = self.range_end
            vcg, ccg = self.extractor.get_congestions_list(range_start, range_end)
            if(len(self.congestededges)):
                self.deletecongestionedges()
            if(len(self.congestvertices)):
                self.deletecongestionvertices()
            if(len(ccg)):
                self.plotcongestions(ccg)
            if(len(vcg)):
                self.plotvertexcongestions(vcg)
            else:
                print("no congestion detected")

        self.button.on_clicked(computecongestion)
        self.sl_date.on_changed(dateupdate)
        self.sl_window.on_changed(windowupdate)


    def deletegraph(self):
        print("deleting")
        self.nodes.remove()
        self.nodes = 0
        self.fig.canvas.draw()
        for idx in range(len(self.edges)):
            #print("rem edg")
            line = self.edges[idx]
            line[0].remove()
        self.edges = []
        self.fig.canvas.draw()

    def deletecongestionedges(self):
        print("deleting")
        for idx in range(len(self.congestededges)):
            #print("rem edg")
            line = self.congestededges[idx]
            line[0].remove()
        self.congestededges = []
        self.fig.canvas.draw()
        self.annotations = []
        #self.cbar.remove()
    def deletecongestionvertices(self):
        print("deleting vertices")
        for idx in range(len(self.congestvertices)):
            #print("rem edg")
            temp = self.congestvertices[idx]
            temp.remove()
        self.congestvertices = []
        self.fig.canvas.draw()
        self.vannotations = []
#precompute coarsness levels.
