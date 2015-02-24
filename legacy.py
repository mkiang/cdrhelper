##  IN VERSION 1.9+, networkx changed how it returned strongly and weakly
##  connected components. Thus, import the old version of these functions (1.7).
def _single_source_shortest_unipath_length(G,source,cutoff=None):
    """Compute the shortest path lengths from source to all reachable nodes.

    The direction of the edge between nodes is ignored.
    
    For directed graphs only.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    lengths : dictionary
        Dictionary of shortest path lengths keyed by target.
    """
    # namespace speedups
    Gsucc = G.succ
    Gpred = G.pred

    seen={}                  # level (number of hops) when seen in BFS
    level=0                  # the current level
    nextlevel = set([source]) # set of nodes to check at next level
    while nextlevel:
        thislevel=nextlevel  # advance to next level
        nextlevel = set()         # and start a new list (fringe)
        for v in thislevel:
            if v not in seen:
                seen[v]=level # set the level of vertex v
                nextlevel.update(Gsucc[v]) # add successors of v
                nextlevel.update(Gpred[v]) # add predecessors of v
        if (cutoff is not None and cutoff <= level):  break
        level=level+1
    return seen  # return all path lengths as dictionary

def strongly_connected_components_old(G):
    """Return nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An directed graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.
       The list is ordered from largest connected component to smallest.

    See Also       
    --------
    connected_components

    Notes
    -----
    Uses Tarjan's algorithm with Nuutila's modifications.
    Nonrecursive version of algorithm.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen 
       Information Processing Letters 49(1): 9-14, (1994)..
    """
    preorder={}
    lowlink={}    
    scc_found={}
    scc_queue = []
    scc_list=[]
    i=0     # Preorder counter
    for source in G:
        if source not in scc_found:
            queue=[source]
            while queue:
                v=queue[-1]
                if v not in preorder:
                    i=i+1
                    preorder[v]=i
                done=1
                v_nbrs=G[v]
                for w in v_nbrs:
                    if w not in preorder:
                        queue.append(w)
                        done=0
                        break
                if done==1:
                    lowlink[v]=preorder[v]
                    for w in v_nbrs:
                        if w not in scc_found:
                            if preorder[w]>preorder[v]:
                                lowlink[v]=min([lowlink[v],lowlink[w]])
                            else:
                                lowlink[v]=min([lowlink[v],preorder[w]])
                    queue.pop()
                    if lowlink[v]==preorder[v]:
                        scc_found[v]=True
                        scc=[v]
                        while scc_queue and preorder[scc_queue[-1]]>preorder[v]:
                            k=scc_queue.pop()
                            scc_found[k]=True
                            scc.append(k)
                        scc_list.append(scc)
                    else:
                        scc_queue.append(v)
    scc_list.sort(key=len,reverse=True)            
    return scc_list
	
def weakly_connected_components_old(G):
    """Return weakly connected components of G.
    """
    if not G.is_directed():
        raise nx.NetworkXError("""Not allowed for undirected graph G. 
              Use connected_components() """)
    seen={}
    components=[]
    for v in G:
        if v not in seen:
            c=_single_source_shortest_unipath_length(G,v)
            components.append(list(c.keys()))
            seen.update(c)
    components.sort(key=len,reverse=True)
    return components