# CoDe
We show you the bottleneck

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


## Clustering
To provide a high-level overview of congestions in regions, operational points are grouped in clusters. Clustering is performed by a uniform grid. Additionaly,  to preserve disconnections in the network, clusters are only formed from connected regions.

* Averaging points in a common neighborhood
* Clusters are selected by a grid
* Only connected points could belong to a single cluster