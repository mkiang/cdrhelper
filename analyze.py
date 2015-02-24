"""
Tools to help analyze fake CDR data as well as networks in general.

"""
from legacy import *
import networkx as nx
import pandas as pd
import numpy as np

def overlap(G, edge):
    """Calculate edge overlap between any two nodes.
    
    Taken directly from JP's notes. Returns the overlap value or None.
    
    Parameters:
    -----------
    G : NetworkX graph to be analyzed (undirected)
    edge : A tuple of edge (u, v)
    
    Notes:
    ------
    JP Onnela
    """
    node_i = edge[0]
    node_j = edge[1]
    degree_i = G.degree(node_i)
    degree_j = G.degree(node_j)
    nei_i = set(G.neighbors(node_i))
    nei_j = set(G.neighbors(node_j))
    nei_ij = nei_i & nei_j
    num_cn = len(nei_ij)
    if degree_i > 1 or degree_j > 1:
        return num_cn / float(degree_i + degree_j - num_cn - 2)
    else:
        return None

def overlapDistribution(G, nodelist = None, sort = True):
    """Returns a (sorted) vector of overlap values for any given set of nodes.
    
    Cycles through the entire nodelist and calculates all edges for all nodes
    in that list. Then returns a sorted list of the overlap values.
    """
    if nodelist is None:
        nodelist = G.nodes()
    olap = [overlap(G, edge) for node in nodelist for edge in G.edges(node)]
    if sort == True:
        return sorted(olap)
    else:
        return olap

def relativeLSCCsize(D):
    """Calculates the relative size of largest strongly connected component
    
    Note:
    -----
    DEPENDS ON OLD VERSION of strongly_connected_components. See legacy.py.
    """
    LCCsize = len(strongly_connected_components_old(D)[0])
    return(LCCsize / float(D.number_of_nodes()))

def relativeLWCCsize(D):
    """Calculates the relative size of largest weakly connected component
    
    Note:
    -----
    DEPENDS ON OLD VERSION of weakly_connected_components. See legacy.py.
    """
    LCCsize = len(weakly_connected_components_old(D)[0])
    return(LCCsize / float(D.number_of_nodes()))

def summaryStats(df):
    """Produces a very crude summary table from an attribute dataframe.
    
    This is a very 'R' way of producing a quick and dirty summary table. Use 
    it knowing there is a Python guru out there who is greatly disappointed
    right now.
    
    Parameters:
    -----------
    df : pandas dataframe you want analyzed. It makes the most sense for 
    the attribute dataframe, but is generalized enough for any df.
    """
    summary_stats = ['min', 'max', 'mean', 'median', 'var', 'std', 'nunique', 
                    'count', 'p25', 'p75']
    holder = pd.DataFrame(index = summary_stats)
    for col in df.columns.values:
        if df[col].dtype != np.object:
            stat_vector = np.zeros(10)
            i = 0
            for stat in summary_stats[:8]:
                attr = df[col].__getattribute__(stat)
                stat_vector[i] = attr()
                i += 1
            stat_vector[8] = df[col].quantile(.25)
            stat_vector[9] = df[col].quantile(.75)
            holder[col] = stat_vector
    return(holder)

def DNetworkSummary(D, qtr, filename = None):
    """Just outputs and prints a quick table of DIRECTED network statistics."""
    ##  Calculate all the network summary stats
    n = D.number_of_nodes()
    e = D.size()
    e_c = D.size(weight = 'calls')
    e_min = D.size(weight = 'min')
    e_sms = D.size(weight = 'sms')
    e_mms = D.size(weight = 'mms')
    n_scc = nx.number_strongly_connected_components(D)
    r_scc = relativeLSCCsize(D)
    n_wcc = nx.number_weakly_connected_components(D)
    r_wcc = relativeLWCCsize(D)
    
    ##  Description vector for printout and output file
    ts  = "    "  # just so the output file is a little more readable
    a1  = "Directed Network Statistics -- Quarter "
    a2  = ts + "Number of nodes: "
    a3  = ts + "Number of edges (unweighted): "
    a4  = ts + ts + "Number of edges (weighted by calls): "
    a5  = ts + ts + "Number of edges (weighted by minutes): "
    a6  = ts + ts + "Number of edges (weighted by SMS): "
    a7  = ts + ts + "Number of edges (weighted by MMS): "
    a8  = ts + "Number of Strongly Connected Components (SCC): "
    a9  = ts + ts + "Relative size of largest SCC: "
    a10 = ts + "Number of Weakly Connected Components (WCC): "
    a11 = ts + ts + "Relative size of largest WCC: "
    name = [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11]
    result = [qtr, n, e, e_c, e_min, e_sms, e_mms, n_scc, r_scc, n_wcc, r_wcc]
    outputresults = pd.DataFrame(data = {'Description': name, 'Result': result})
    if (filename is not None):
        outputresults.to_csv(filename, index = False)
    print outputresults

def GNetworkSummary(G, qtr, filename = None):
    """Just outputs and prints a quick table of clustering statistics."""
    ##  Calculate all the network summary stats
    n = G.number_of_nodes()
    e = G.size()
    e_c = G.size(weight = 'calls')
    e_min = G.size(weight = 'min')
    e_sms = G.size(weight = 'sms')
    e_mms = G.size(weight = 'mms')
    avgC = nx.average_clustering(G)
    avgC_c = nx.average_clustering(G, weight = 'calls')
    avgC_min = nx.average_clustering(G, weight = 'min')
    avgC_sms = nx.average_clustering(G, weight = 'sms')
    avgC_mms = nx.average_clustering(G, weight = 'mms')
    
    ##  Description vector for printout and output file
    ts  = "    "  # just so the output file is a little more readable
    a1  = "Undirected Network Statistics -- Quarter "
    a2  = ts + "Number of nodes: "
    a3  = ts + "Number of edges (unweighted, undirected): "
    a4  = ts + ts + "Number of edges (weighted by calls): "
    a5  = ts + ts + "Number of edges (weighted by minutes): "
    a6  = ts + ts + "Number of edges (weighted by SMS): "
    a7  = ts + ts + "Number of edges (weighted by MMS): "
    a12 = ts + "Average Clustering (undirected, unweighted): "
    a13 = ts + ts + "Avgerage Clustering (weighted by calls): "
    a14 = ts + ts + "Avgerage Clustering (weighted by minutes): "
    a15 = ts + ts + "Avgerage Clustering (weighted by SMS): "
    a16 = ts + ts + "Avgerage Clustering (weighted by MMS): "
    name = [a1, a2, a3, a4, a5, a6, a7, a12, a13, a14, a15, a16]
    result = [qtr, n, e, e_c, e_min, e_sms, e_mms,
              avgC, avgC_c, avgC_min, avgC_sms, avgC_mms]
    outputresults = pd.DataFrame(data = {'Description': name, 'Result': result})
    if (filename is not None):
        outputresults.to_csv(filename, index = False)
    print outputresults
