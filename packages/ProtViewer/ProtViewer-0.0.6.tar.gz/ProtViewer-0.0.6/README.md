# ProtViewer

A tool to view activity pattern in protein structures. Protein structure visualization is only one application of this 
tool. One can visualize arbitrary graphs with some activity patterns with this tool.

## Website

You can use the tool very easily to visualize activities of certain nodes in graphs. The 
[online-viewer](old-shatterhand.github.io/ProtViewer) can be used to visualize activity of nodes in a graph.
One example is the binding prediction of some model for protein-ligand interactions. The model can output
scores defining how much influence a certain node had on the prediction if or if not a certain protein binds to a 
target or not.

## Generating Activity Files

You can easily generate the input files for the online viewer yourself be following the structure described in the "Activity File Structure" section below.

### Package Installation

Otherwise, you can install the python package to generate the files using pip
``````shell
pip install protviewer
``````
and also updating is very easy. Just type
``````shell
pip install --upgrade protviewer
``````

### Package Usage

To use the package and generate the activities for a certain protein, just call
``````python
from viewer import view

view(pdb_file, output_dir, activities, distances)
``````
This will generate the json-file inside the `output_dir` as `[pdb_file].json`. You can then directly upload this
output file to the [web service](old-shatterhand.github.io/ProtViewer) and investigate what your model guided to the 
decision if a model binds or not.

## Activity File Structure
The json-file you input to the [online-viewer](old-shatterhand.github.io/ProtViewer) has to have the following structure
``````json
{
  "nodes": [
    "AA_1": {
      "x": ...,
      "y": ...,
      "z": ...,
      "activity": ...,
      "distance": ...,
    }, ...
  ],
  "edges": {
    "start": [
      0, 2, 1, 5, 3, ...
    ],
    "end": [
      2, 1, 5, 3, 6, ...
    ]
  }
}
``````