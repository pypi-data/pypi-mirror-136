Alpha Version

install via pip install NetABM

run:
from NetABM import ABM

model = ABM(network_list)
model.run_model()

get attributes via
model.agents.items()

returns key and item from dictionary



______________________________________________________________________
network_list is a python list variable with networkx object as indices
other attributes can be added to the class. 
______________________________________________________________________
Visualization can be done through model.run_overlapping_histograms()
Get Network Analysis by model.get_stats()