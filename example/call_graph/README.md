## Introduction

This example demonstrates how interceptor can be used to generate call graph tree when ansible runs 
a playbook.

## Usage

    usage: generate.py [-h] [-l] [-t [TARGET]] [-i [IGNORE [IGNORE ...]]] -- <ansible-playbook options>
    
    The tool generates the call graph when a playbook is run after ansible classes
    are intercepted
    
    optional arguments:
      -h, --help            show this help message and exit
      -l, --long            File reference of method in call graph is absolute,
                            i.e. starts with ansible, otherwise just the basename if not __init__.py
      -t [TARGET], --target [TARGET]
                            Filepath to write call graph, defaults to
                            example/call_graph/call_graph.txt
      -i [IGNORE [IGNORE ...]], --ignore [IGNORE [IGNORE ...]]
                            Methods to ignore while generating call graph
                            
TODO: Expose option to allow restricting classes. 


## Sample Output

![Sample Call Graph](sample_call_graph.jpg?raw=true "Sample Call Graph")

However, please note this has been generated limiting intercepted classes and not using the flags.


## Call graph visualization

The call graph can be formatted into a tree structure using tool created 
[here](https://github.com/sans-sense/Utils)
