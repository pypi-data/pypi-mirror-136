# app-graphs

[Original repository](https://github.com/skorjanc/app-graphs) (github).

**app-graphs** uses [ogdf-python](https://pypi.org/project/ogdf-python/) which in turn uses [OGDF](https://ogdf.uos.de/).
app-graphs draws a graph from data given in .xlsx format. Nodes are generated from given aplications and components as well as from edges, where node lies on edge, spliting it in two. Edges are generated between aplication and its components and from directed edges provided.

## Installation

First we need to install [**OGDF**](https://ogdf.uos.de/2020/02/09/catalpa/). This is done by downloading OGDF, unziping it and calling following commands in bash:
```bash
foo@bar:~ogdf$ mkdir ogdf-debug ogdf-release
foo@bar:~ogdf$ cd ogdf-debug
foo@bar:~ogdf/ogdf-debug$ cmake ..
foo@bar:~ogdf/ogdf-debug$ ccmake ..
```
Configure BUILD_SHARED_LIB=ON and CMAKE_BUILD_TYPE=Debug when calling last line.
```bash
foo@bar:~ogdf/ogdf-debug$ make
```
Repeat above for release (debug <-> release). And as a last step add ogdf to path.
```bash
foo@bar:~ogdf$ export OGDF_BUILD_DIR=~/ogdf/ogdf-debug
```
As a last step install app-graphs.
```python
pip install app-graphs
```

## Usage

```python
from app-graphs import graph

# Define graph instance
my_graph = graph()

# Read data from filename_aplikacije and vmesniki_sheet_name
my_graph.read(filename_aplikacije = r'example.xlsx',
            aplikacije_sheet_name = 'Aplication list',
            filename_vmesniki = r'example.xlsx',
            vmesniki_sheet_name = 'Integration list',
            aplikacije = 'Aplications',
            komponente = 'Components',
            vmesnik_izvor = 'Source',
            vmesnik_ponor = 'Target',
            vmesnik_smer = 'Direction',
            tehnologija = 'Technology',
            barve = 'Colors'
            )

# Uses ogdf-python to generate graph
my_graph.draw()

# Saves genereted graph in desired format
my_graph.save_svg('test-graph')
my_graph.save('test-graph', 'DOT')
my_graph.save('test-graph', 'GML')
```
![example](https://i.imgur.com/0VCrbTh.png)
