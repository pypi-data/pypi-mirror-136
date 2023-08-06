# -*- coding: utf-8 -*-
"""
@author: Christoph Krüger
Part of the PROBLEMSHIFTING PROJECT
@email: christoph.kruger@yahoo.com

"""


from scipy.stats import poisson
class ABM():
    """
    An Agent based model, which takes a list of networks as input.
    The list of networks allows adding of nodes specific to each timestep.
    The agents will shift weight around in the network, 
    creating more weighted nodes in the center of the network.
    Edges are disconnected stochastically according to the poisson distribution. 
    The Mu value can be set with the attributed mu.
    A membership dict can be added, give more initial weight to the nodes.
    The keys of the dictonary must match the network node names.
    """
    def __init__(self, network_list, membership_dict = {}, mu = 0.1):
        """
        Initialize the class with a list of networks.
        Potentially add a mu weight for the stochastic poisson deteriation of the network.
        """
        self.network = network_list[0]
        self.time_steps = len(network_list)
        self.flow_rate = 30
        self.membership_dict = membership_dict
        self.mu = mu
        #add changing network
        self.network_edge_changes = [0]
        self.network_node_changes = [0]
        for step in range(1,len(network_list)):
            difference_edges = network_list[step].edges - network_list[step - 1].edges
            difference_nodes = network_list[step].nodes - network_list[step - 1].nodes
            self.network_edge_changes.append(difference_edges)
            self.network_node_changes.append(difference_edges)
            
        #create dict with "agents" (nodes with value of weight)
        self.agents = {}
        for agent in self.network.nodes:
            self.agents[agent] = 100.
        
    
    def run_model(self):
        """
        Run the model. The timesteps are according to the length of the network list.
        """
        for i in range(self.time_steps):
            if i != 0: #in the first iteration, no new edges or nodes are added
                #add nodes
                for node_added in self.network_node_changes[i]:
                    self.network.add_node(node_added)
                    self.agents[node_added] = 100.

                #add edges
                for edge_added in self.network_edge_changes[i]:
                    self.network.add_edge(*edge_added)
                
            #shift weights in network
            for agent in self.agents.keys():
                neighbors = list(self.network.neighbors(agent))
                num_neigh = len(neighbors)
                if num_neigh == 0: #skip if empty
                    continue
                for neighbor in neighbors:
                    #check if membership dict is there and then use it, otherwise use defined flow rate
                    if self.membership_dict:
                        #check if treaty is in list, otherwise use default flow rate
                        if agent in self.membership_dict:                        
                            flow_rate = self.membership_dict[agent]
                        else:
                            flow_rate = self.flow_rate
                        if flow_rate < self.agents[agent]:
                            #transfer weight
                            self.agents[neighbor] += flow_rate / num_neigh
                            self.agents[agent] -= flow_rate / num_neigh
                    #otherwise use default flow rate
                    else:
                        if self.flow_rate < self.agents[agent]:
                            #transfer weight
                            self.agents[neighbor] += self.flow_rate / num_neigh
                            self.agents[agent] -= self.flow_rate / num_neigh
                
            #delte edges according to poisson
            edge_delete_list = [] #needed, as otherwise the dictionary will be changed during iteration
            for edge in self.network.edges:
                if poisson.rvs(mu = self.mu) > 0:
                    edge_delete_list.append(edge)
            
            for edge in edge_delete_list:
                self.network.remove_edge(*edge)
          
            