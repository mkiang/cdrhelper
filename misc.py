""" 
Miscellaneous tools I use to analyze the European CDR data.
"""
import os

def folderCheck(folder):
    """Check if a folder exists -- if not, create it."""
    if not os.path.isdir(folder):
        os.makedirs(folder)

##  Subsetting nodes by gender and age
def selectNodes(G, age = 99, male = 0):
    """Returns a list comprised of a subset of nodes specified by age
        and sex. 99 for age or male returns all categories. 
        
        NOTE: Right now, I have very bad missing data handling. 
        Ignores missingness for 99s."""
    if (age is 99) and (male is not 99):
        subl = [n for n in G if (G.node[n]['male'] == male)]
    elif (male is 99) and (age is not 99):
        subl = [n for n in G if (G.node[n]['agecat'] == age)]
    elif (age is not 99) and (male is not 99):
        subl = [n for n in G if (G.node[n]['agecat'] == age) and 
                                (G.node[n]['male'] == male)]
    elif (age is 99) and (male is 99):
        subl = G.nodes()
    else: 
        raise NameError("Invalid subset specification.")
    return(subl)

def agexsexsubset(G):
    """Creates a list of lists of nodes by age and sex.
    
    Resulting order is ages first then gender. Thus:
        agexsexnodes[0]  = everyone in age 0 
        agexsexnodes[1]  = everyone in age 20
        agexsexnodes[2]  = everyone in age 30
        agexsexnodes[3]  = everyone in age 40
        agexsexnodes[4]  = everyone in age 50
        agexsexnodes[5]  = everyone in age 60+
        agexsexnodes[6]  = everyone in all ages
        agexsexnodes[7]  = males in age 0
            etc etc
        agexsexnodes[13] = all males
        agexsexnodes[14] = females in age 0
            etc etc
        agexsexnodes[20] = all females
    """
    agelist = [0, 20, 30, 40, 50, 60, 99]
    agexsexnodes = [selectNodes(G, age = x, male = y) for y in [99, 1, 0] \
                    for x in agelist]
    return(agexsexnodes)

def aggregateCalls(df_call):
    """Returns an aggregated version of importCalls() dataframe.
    
    Parameters:
    df_call : a pandas dataframe created by the importCalls() function.
    """
    df_sum = df_call.groupby(['A_num', 'B_num']).sum().add_prefix('s')
    df_sum = df_sum.reset_index()
    df_sum.drop('sdate', axis = 1, inplace = True)
    ##  NOTE!
    ##  Eventually, we want to make this generalized so that you can specify 
    ##  the number of days you want to collapse over and then it will redo all
    ##  these next steps for each date range.

    ##  Sum up the edges with weights (and obviously direction).
    ##  To be clear: .groupby will group the edges (still dircted). Then .sum
    ##  aggregates them by summing. And .add_prefix just changes column
    ##  names so it is explicit we are summing. Finally, .reset_index just 
    ##  renumbers the rows into an array more compatible with networkx.
    return(df_sum)

