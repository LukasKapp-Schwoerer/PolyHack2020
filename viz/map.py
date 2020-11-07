from bokeh.plotting import figure, save

class Map:
    def __init__(self, ops, title):
        self.p = figure(title=title)
        self.ops = ops

    def plotnodes(self,):

        self.p.circle(x = self.ops['x'], y = self.ops['y'], size=10, color="red")

    def plotedges(self,):
        #loop ove rall points and plot incident lists
        for startingpoint in ops['ID']:
            #plot all edges in incidence list to points not covered yet
            #plot line to point if target> self index
            IL = self.ops['IL'][startingpoint]
            for target in IL:
                if(target >startingpoint):
                    #plot line
                    xline = [ self.ops['x'][startingpoint], self.ops['x'][target] ]
                    yline = [ self.ops['y'][startingpoint], self.ops['y'][target] ]
                    self.p.line(xline, yline)
            print("starting point idx", startingpoint, IL)

    def saveplot(self, name):
        save(obj=self.p, filename=name)

# Initialize the plot (p) and give it a title
p = figure(title="Operation Points")

# Create a list of x-coordinates
x_coords = [0,1,2,3,4]
y_coords = [5,4,1,2,0]
ID = [0,1,2,3,4]
IL = {0: [2,3], 1: [3,4,2], 2:[0,1], 3: [0,1] , 4:[1]}
ops = { 'ID': ID,
        'x': x_coords,
        'y': y_coords,
        'IL': IL }

map = Map(ops, "test")
map.plotnodes()
map.plotedges()
map.saveplot("test.html")
