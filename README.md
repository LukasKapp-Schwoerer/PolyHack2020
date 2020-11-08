# CoDe
CoDe is an interactive railway traffic data aggregation tool, enabling the user to combine information from different data sets. It visualizes contruction site induced bottlenecks while providing settings such as time of day, construction work time interval and traffic grid coarseness. After computing a congestion metric, the interactive geographic map provides additional data when exploring the resulting railway grid streamlining the planning of new construction work.

## Used data sets
 * construction-cite.csv
 * linie-mit-betriebspunkten.csv
 * zugzahlen.csv

## Functionality

* Provide a fine-grained or coarse-grained overview of critical bottlenecks of the railway grid
* Adjust time of day to account for type of construction work and typical rail traffic
* Adjust time interval
* Interactive GUI providing additional data

![Alt](/img/GUI.png "Screenshot of the GUI")

## data_extraction
Date Processing
* Selecting most insightful data
* Approximating missing GPS coordinates
* Rich data-structures combining multiple sources


Algorithm
* For construction sites: Employ graph-exploration to find affected track segments
* Distinction between night and day (passenger trains are day only, freight trains evenly split)
* Congestion metric considering
    - Time of day
    - Number & Type of trains passing
    - Capacity loss induced by the construction work


## Clustering
To provide a high-level overview of congestions in regions, operational points are grouped in clusters. Clustering is performed by a uniform grid. Additionaly, to preserve disconnections in the network, clusters are only formed from connected regions.

* Averaging points in a common neighborhood
* Clusters are selected by a grid
* Only connected points could belong to a single cluster

![Alt](/img/Cluster.jpeg "Visualization of Clustering")
