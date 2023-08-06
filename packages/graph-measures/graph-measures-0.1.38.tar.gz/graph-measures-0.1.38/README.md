# Topological Graph Features

Topological feature calculators infrastructure.

## Calculating Features
This package helps one to calculate features for a given graph. All features are implemented in python codes, 
and some features have also an accelerated version written in C++. Among the accelerated features, one can find 
a code for calculating 3- and 4-motifs using VDMC, a distributed algorithm to calculate 3- and 4-motifs in a 
GPU-parallelized way.

## Versions
- Last version: 0.1.38
- Last stable version: 0.1.22

## What Features Can Be Calculated Here?
The set of all vertex features implemented in graph-measures is the following. 
The features that have an accelerated version are written in bold:
* Average neighbor degree
* General (i.e. degree if undirected, else or (in-degree, out-degree))
* Louvain (i.e. implement Louvain community detection method, then associate to each vertex the number of vertices 
in its community)
* Hierarchy energy
* **Motifs**
* **K core**
* **Attraction basin** 
* **Page Rank**
* Fiedler vector
* Closeness centrality
* Eccentricity
* Load centrality
* **BFS moments**
* **Flow** 
* Betweenness centrality
* Communicability betweenness centrality
* Eigenvector centrality
* Clustering coefficient
* Square clustering coefficient
* Generalized degree
* All pairs shortest path length
* All pairs shortest path

Aside from those, there are some other [edge features](src/graphMeasures/features_algorithms/edges).
Some more information regarding the features can be found in the files of [features_meta](src/graphMeasures/features_meta).

## Dependencies
```requirements.txt
setuptools
networkx
pandas
numpy
matplotlib
scipy
scikit-learn
python-louvain
bitstring
future
torch
```

## Installation Through pip
The full functionality of the package is currently available on a Linux machine, with a Conda environment.
- Linux + Conda<br>1. Go to base environment<br>2. If pip is not installed on your env, install it. Then, use pip to install the package
- Otherwise, pip must be installed.
```commandline
pip install graph-measures
```
**Note:** On Linux+Conda the installation might take longer (about 5-10 minuets) due to the compilation of the c++ files.
## How To Use?
Even though one has installed the package as `graph-measures`, The package should be imported from the code as `graphMesaures`. Hence, use:
```python
import graphMeasures
```
## Calculating Features

There are two main methods to calculate features:
1. Using [FeatureCalculator](src/graphMeasures/features_for_any_graph.py/FeatureCalculator) (**recommended**): \
A class for calculating any requested features on a given graph. \
The graph is input to this class as a text-like file of edges, with a comma delimiter, or a networkx _Graph_ object. 
For example, the graph [example_graph.txt](src/graphMeasures/measure_tests/example_graph.txt) is the following file: 
    ```
    0,1
    0,2
    1,3
    3,2
    ```
    Now, an implementation of feature calculations on this graph looks like this:
    ```python
   import os
   from graphMeasures import FeatureCalculator
   feats = ["motif3", "louvain"]  # Any set of features
   path = os.path.join("measure_tests", "example_graph.txt") 
   head = "" # The path in which one would like to keep the pickled features calculated in the process. 
   # More options are shown here. For infomation about them, refer to the file.
   ftr_calc = FeatureCalculator(path, head, feats, acc=True, directed=False, gpu=True, device=0, verbose=True)
   ftr_calc.calculate_features()
   mx = ftr_calc.feature_matrix
    ``` 
    More information can be found in [features_for_any_graph.py](src/graphMeasures/features_for_any_graph.py).\
    **Note:** If one set `acc=True` without using a Linux+Conda machine, an exception will be thrown.\
     **Note:** If one set `gpu=True` without using a Linux+Conda machine that has cuda available on it, an exception will be thrown.
2. By the calculations as below **(less recommended)**: \
The calculations require an input graph in NetworkX format, later referred as gnx, and a logger.
For this example, we build a gnx and define a logger:
    ```python
   import networkx as nx
   from graphMeasures.loggers import PrintLogger
    
   gnx = nx.DiGraph()  # should be a subclass of Graph
   gnx.add_edges_from([(0, 1), (0, 2), (1, 3), (3, 2)])
    
   logger = PrintLogger("MyLogger")
    ```
    On the gnx we have, we will want to calculate the topological features.
    There are two options to calculate topological features here, depending on the number of features we want to calculate: 
    * Calculate a specific feature:

    ```python
    import numpy as np
    # Import the feature. 
    # If simple, import it from vertices folder, otherwise from accelerated_graph_features: 
    from graphMeasures.features_algorithms.vertices.louvain import LouvainCalculator  
    
    feature = LouvainCalculator(gnx, logger=logger)  
    feature.build()  # The building happens here
    
    mx = feature.to_matrix(mtype=np.matrix)  # After building, one can request to get features the a matrix 
    ```

    * Calculate a set of features (one feature can as well be calculated as written here):

    ```python
   import numpy as np
   from graphMeasures.features_infra.graph_features import GraphFeatures
    
   from graphMeasures.features_algorithms.vertices.louvain import LouvainCalculator
   from graphMeasures.features_algorithms.vertices.betweenness_centrality import BetweennessCentralityCalculator
    
   features_meta = {
       "louvain": FeatureMeta(LouvainCalculator, {"lov"}),
      "betweenness_centrality": FeatureMeta(BetweennessCentralityCalculator, {"betweenness"}),
   }  # Hold the set of features as written here. 
    
   features = GraphFeatures(gnx, features_meta, logger=logger) 
   features.build()
    
   mx = features.to_matrix(mtype=np.matrix)
    ```
