"""
Simulate fake call detail records.

"""

import networkx as nx
import random
import numpy as np
import pandas as pd
from scipy.stats import fisk  # Log-logistic distribution for call duration

def generatePostcode(sourcefile = None, header = 'Postal Code',
                     randombegin = 1000, randomend = 5000):
    """Returns a vector of postcodes or location identifier.

    If source does not exist, generates it.
    
    Reads in a CSV file of postcodes for the data generation process below. If
    no file exists, it will generate postcodes randomly. This is to try to get
    as close to the real data as possible. 
    
    NOTES:
    ------
    Just needs a csv with header 'Postal Code' and a postcode on each line.
    See: https://www.aggdata.com for free files in the correct format.
    """
    if (sourcefile is None):
        x = pd.DataFrame(data = range(randombegin, randomend),
                         columns = [header])
    else:
        x = pd.read_csv(sourcefile)
    return x

def generatePopulation(sourcefile = None, agemax = 106):
    """Returns a vector of weights for each age group.

    Reads in a CSV file of typical population structure (i.e., columns: age,
    both, male, female) and figures out the weight for each age above 18 to
    use for a weighted random draw later. If no source file is found,
    just creates a uniform probability vector.
    """
    if (sourcefile is None):
        agexsex = pd.DataFrame(range(0, agemax), columns = ["age"])
        agexsex["both"] = 100
    else:
        agexsex = pd.read_csv(sourcefile,
                              names = ["age", "both", "male", "female"],
                              header = 0)
    totalpop = sum(agexsex.iloc[18: ]['both'])
    ageweight = agexsex.iloc[18: ]['both'].values / float(totalpop)
    return ageweight

"""
DATA GENERATION:
    Works in three steps: 
    (1) Generates a network and then randomly picks edges and assigns them to a
            date.
    (2) For each randomly picked edge in (1), generate call and text data.
    (3) For some subset of calls in each day, reciprocate the call.
    
"""


def generateDateCallers(G, days = 90, callsperday = 20, 
                        startdate = '20130101', seed = None):
    """Returns a dataframe with dates, caller, and recipient.
    
    This outputs a pandas dataframe filled with repeating dates and calls 
    between u and v. Each line will represent a single observation (edge) 
    for that day based on an underlying graph, G.
    
    Parameters
    ----------
    days : Number of days under observation (default = 90)
    startdate : When the daterange should start. (default = '20130101')
    callsperday : The number of observations (callers) per day. Drawn from a
        Poisson distribution. (default = 20)
    G : NetworkX graph to select edges from.
    seed : random seed for replication purposes.
    """
    if seed is not None:
        random.seed(seed)
    
    E = np.random.poisson(callsperday, days)
    dates = pd.date_range(startdate, periods = days)
    dates_col = np.repeat(dates, E)
    df = pd.DataFrame(data = dates_col, columns = ['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y%m%d'))
    
    ## Now we generate the A_num and B_num lists using graph G.
        ## First line randomly selects the appropriate number of edges for each
        ##  day and then compiles a list of lists. Second line turns the list
        ##  of lists into a flattened list. Third line shuffles tuples so that
        ##  A_num won't always be the lower numbered node.
    sample_e = [random.sample(G.edges(), x) for x in E]
    sample_e = [item for sublist in sample_e for item in sublist]
    shuffled_e = [random.sample(sample_e[x], 2) for x in range(len(sample_e))]
    u, v = zip(*shuffled_e)
    df['A_num'] = u
    df['B_num'] = v
    return(df)

def generateCallData(data, mean_calls = 5, call_dur = 1.15, 
                    mean_sms = 25, mean_mms = 10, seed = None):
    """Takes a generateDateCallers() dataframe and returns one with call info.
    
    This new dataframe will contain four new columns:
            1) 'min' : number of total minutes between callers
            2) 'calls' : number of total calls (per day) between nodes
            3) 'sms' : number of total sms (per day) between nodes
            4) 'mms' : number of total mms (per day) between nodes
    
    Parameters
    ----------
    data : your pandas dataframe as created by generateDateCallers
    mean_calls : mean of Poisson distribution to draw number of calls between
        nodes for that day.
    min_dur : the shape parameter of a log-logistic distribution to describe
        duration of calls. (Note: Drawn multiple times and then summed over.)
    mean_sms : mean of Poisson distribution from which to draw SMS data
    mean_mms : mean of Poisson distribution from which to draw MMS data
    """
    dfrows = len(data)
    if seed is not None:
        random.seed(seed)
    calls = np.random.poisson(mean_calls, dfrows)
    data['calls'] = calls
    data['min'] = [round(np.sum(fisk.rvs(call_dur, size=x)), 1) for x in calls]
    data['sms'] = np.random.poisson(mean_sms, dfrows)
    data['mms'] = np.random.poisson(mean_mms, dfrows)
    return(data)

##  Reciprocating calls function
def reciprocate(df_call, r_prob = .33):
    """Takes a generateCallData() dataframe and reciprocates calls randomly. 
    
    Randomly selects r_prob proportion for each day in a generateCallData() df
    and then generates reciprocating call data. 
    """
    
    # Make a list of randomly selected indices for each day in the original
    subindex = []
    for day in pd.unique(df_call['date']):
        cdayi = df_call[df_call['date'] == day].index.tolist()
        subsample = random.sample(cdayi, int(r_prob * len(cdayi)))
        subindex.append(subsample)
    subindex = [item for sublist in subindex for item in sublist]
    
    # Get the new subsample and three columns we need
    df2 = df_call.ix[subindex, :3]
    
    # Swap the A_num and B_num columns (reciprocate calls)
    df2.rename(columns = {"A_num" : "B_num", "B_num" : "A_num"}, inplace = True)
    
    # Reorder the columns back to the original for consistency
    df2 = df2.ix[:, [0, 2, 1]]
    
    # Regenerate new call data
    df2 = generateCallData(data = df2)
    
    # Append to old dataframe; sort it
    df3 = df_call.append(df2)
    df3 = df3.sort(columns = ["date", "A_num"])
    
    # Return data
    return df3

def makeData(postcodes, ageweight, nodes = 30, edges = 10, days = 10,
                callsperday = 20, startdate = "20130101", 
                mean_calls = 5, call_dur = 1.15,
                mean_sms = 25, mean_mms = 10, 
                r_prob = .33, seed = None,
                maleid = "M", femaleid = "F"):
    """Returns 1 graph and two dataframes -- one for attributes; one for calls.
    
    Uses generateCallData(), generateDateCallers(), and reciprocate() to return
    2 pandas dataframes that will mimic the European CDR dataset -- one for call
    information (df) and one for attribute information (attr).
    
    See docstring of generateCallData(), generateDateCallers(), and 
    reciprocate() for more information on parameters. Will return both 
    complete datesets and the underlying graph upon which it is based. 
        
    For missingness, see insertMissing().
        
    Example usage: 'G, df, attr = makeData()'
    """
    G = nx.barabasi_albert_graph(n = nodes, m = edges, seed = seed)
    G.remove_node(0) # testing something out -- think errors are because of 0.
    
    df = generateDateCallers(G = G, days = days, 
                             callsperday = callsperday, 
                             startdate = startdate, seed = seed)
    
    df = generateCallData(data = df, mean_calls = mean_calls, 
                          call_dur = call_dur, mean_sms = mean_sms, 
                          mean_mms = mean_mms, seed = seed)
    
    df = reciprocate(df_call = df, r_prob = r_prob)
    
    attr = pd.DataFrame(data = G.nodes(), columns = ['A_num'])
    attrrows = len(attr)
    attr['postcode'] = np.random.choice(postcodes['Postal Code'], attrrows)
    attr['gender'] = np.random.choice([femaleid, maleid], attrrows)
    attr['age'] = np.random.choice(range(18, 106), 
                            p = ageweight, size = attrrows)
    
    return(G, df, attr)

def insertMissing(attr, seed = None, p_post = 0, p_age = 0, p_gender = 0):
    """Outputs new attributes dataframe with random missingness.
     
    Takes as input, an 'attr' dataframe generated by makeData() and
    creates missing values in the postcode, age, and gender columns.
        
    Parameters
    ----------
    attr : an attribute datafile that has already been generated by makeData()
    p_* : the probability of a missing value in any of the three columns (age,
            postcode, or gender). Must be between [0, 1].    
    """
    
    if (p_post > 1) or (p_age > 1) or (p_gender > 1):
        return "Probability greater than 1"
    if (p_post < 0) or (p_age < 0) or (p_gender < 0):
        return "Probability less than 0"
    df2 = attr.copy()
    attr_rows = len(df2)
    if seed is not None:
        random.seed(seed)
    if (p_post != 0):
        i_post = random.sample(range(attr_rows), int(p_post * attr_rows))
        df2.ix[i_post, "postcode"] = np.nan
    if (p_age != 0):
        i_age = random.sample(range(attr_rows), int(p_age * attr_rows))
        df2.ix[i_age, "age"] = np.nan
    if (p_gender != 0): 
        i_gender = random.sample(range(attr_rows), int(p_gender * attr_rows))
        df2.ix[i_gender, "gender"] = np.nan
    return(df2)


################################################################################
##  Convert NaN columns back to integer on export
##      NOTE: A caveat of numpy and pandas is that when you insert an NA or NaN
##              that column changes from integer64 to float. This function will
##              change any of those columns back into integer upon export to 
##              make sure the data look as close to the real data as possible.
################################################################################
def exportAttrData(df_attr, filename = "../data/fake1attrdata.txt"):
    df_attr.to_csv(filename, index = False, sep = ";", float_format = '%.0f', 
                    na_rep = " ", header = False)

def exportCallData(df_call, filename = "../data/fake1calldata.txt"):
    df_call.to_csv(filename, index = False, sep = ";", na_rep = " ", 
                    header = False)
