from bokeh.plotting import figure, save, show

class Map:
    def __init__(self, ops, title):
        self.p = figure(title=title)
        self.ops = ops

    def plotnodes(self,):

        self.p.circle(x = self.ops['x'], y = self.ops['y'], size=10, color="red")

    def plotedges(self,):
        #loop ove rall points and plot incident lists
        for startingpoint in self.ops['ID']:
            #plot all edges in incidence list to points not covered yet
            #plot line to point if target> self index
            IL = self.ops['IL'][startingpoint]
            print("IL", IL)
            for target in IL:
                #if(target >startingpoint):
                #plot line
                xline = [ self.ops['x'][self.ops['ID'].index(startingpoint)], self.ops['x'][self.ops['ID'].index(target)] ]
                yline = [ self.ops['y'][self.ops['ID'].index(startingpoint)], self.ops['y'][self.ops['ID'].index(target)] ]
                self.p.line(xline, yline)
            #print("starting point idx", startingpoint, IL)

    def saveplot(self, name):
        save(obj=self.p, filename=name)

    def showmap(self):
        show(self.p)
