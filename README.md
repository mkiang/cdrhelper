# cdrhelper -- Make and analyze fake CDR data
## Introduction
Just a small, simple Python package I made to help people simulate, import, and analyze network data -- 
specifically, network data represented in the form of call detail records (CDR) aggregated up to the day level.

Why? Well, it turns out getting actual CDR data is incredibly difficult and a lot of people simply want the 
experience of playing with "real" network data. This package will help create files that look and feel like
real CDR files using an underlying network that is known to (and specified by) the user. It's derived mostly
from my own simulation exercise, but enough people expressed interest that I'm putting it up here in a 
refactored, probably-still-buggy form.

## CDR format
CDRs come in a wide range of formats and styles, but the most basic (aggregated) CDR will look something like this:
```
20130101;26;357;9;40.7;23;9
20130101;52;504;15;73.3;30;24
20130101;89;158;24;64.6;22;14
20130101;235;447;19;122.7;30;12
20130101;293;849;15;18.7;31;12
```

Representing `date`, `caller id`, `recipient id`, `number of calls`, `minutes`, `text messages`, and `mms messages`, respectively. 
Each column is delimited by a semicolon (`;`) and missingness is represented by a blank space (` `). Each column is `integer` 
except for `minutes` which is `float`.

If you're lucky, you'll sometimes get an attribute file which will look like this:
```
1;1554;F;46
2;1179;M;45
3;4795;M;46
4;2066;F; 
5;1356;F;59
```
Representing `caller id`, `zip code`, `sex`, and `age`, respectively. Again, delimited by semicolon with a space to represent a missing 
value.


## Usage
### Import
```
from cdrhelper import *
```

### Generate location and population information
Note, if you have actual postcode or age populatoin data, use the `sourcefile` option for both commands.
```
postcodes = generatePostcode()
ageweight = generatePopulation()
```

### Generate the call information
There are two ways to generate call information. The first way (easy way) is just a wrapper for the second way. 
The second way offers more control.

#### (1) The easy way
```
G, df, attr = makeData(postcodes = postcodes, ageweight = ageweight)
```
Note, `makeData()` has quite a few parameters that allow you to control most of the interesting bits.
```
def makeData(postcodes, ageweight, nodes = 30, edges = 10, days = 10,
                callsperday = 20, startdate = "20130101", 
                mean_calls = 5, call_dur = 1.15,
                mean_sms = 25, mean_mms = 10, 
                r_prob = .33, seed = None,
                maleid = "M", femaleid = "F"):
```

#### (2) The long way
Make a graph representing your "ground truth" network -- i.e., the network in the whole world.
```
G = nx.barabasi_albert_graph(n = 1000, m = 25)
```

This step isn't necessary, but in my experience, CDR indices are hashed or start at 1, never 0. Remove it for authenticity.
```
G.remove_node(0)
```

Now make a dataframe with mobile interactions and dates. Note, you may not be able to get back to your "ground truth" network
if your observations of interactions are sparse (relative to the size of the network). This is true in the real world as well
where you may only get data from a single telecommunications company and cannot observe the "true" network.
```
df = generateDateCallers(G = G, days = 30, callsperday = 10, 
                            startdate = "20130101")
```

Now populate this dataframe with random interactions (calls, texts, sms)
```
df = generateCallData(data = df, mean_calls = 20, call_dur = 1.15, 
                        mean_sms = 30, mean_mms = 15)
```

Finally, reciprocate some of these calls.
df = reciprocate(df_call = df, r_prob = .4)

### Generate attribute information
This is an example of generating attribute information. You can add more information (e.g., height, weight, etc), but 
this is the minimum requirement for the rest of the module to work.
```
attr = pd.DataFrame(data = G.nodes(), columns = ['A_num'])
attrrows = len(attr)
attr['postcode'] = np.random.choice(postcodes['Postal Code'], attrrows)
attr['gender'] = np.random.choice(["F", "M"], attrrows)
attr['age'] = np.random.choice(range(18, 106), 
                        p = ageweight, size = attrrows)
```

### Insert missingness
Most CDR attribute data will contain (sometimes significant) missingness. Add some here.
```
attr = insertMissing(attr = attr, p_post = .1, p_age = .15, p_gender = .2)
```

### Export to CDR-esque files.
```
folderCheck("../data")
exportAttrData(attr, filename = "../data/myfakeattrdata.txt")
exportCallData(df, filename = "../data/myfakecalldata.txt")
```

## Importing data
Once you have data, you can import it in two ways -- (1) as a `NetworkX` object or (2) as a `pandas` dataframe.
```
from cdrhelper import *
```
### Import as `NetworkX` object
This will import three `NetworkX` objects --- (1) `Nodes` which is a node-only network, (2) `G` which is an undirected graph, 
and (3) `D` which is a directed graph. Obviously, only `D` and `G` will have edge information. Note that the undirected graph, 
`G`, is **not** the same as turning `D` into an undirected graph using `NetworkX`. Specifically, my code will take the sum
of weights between `(u, v)` and `(v, u)` directed edges while the `NetworkX` code just takes the weight of the first `(u, v)`
edge.
```
Nodes = importNodes("../data/myfakeattrdata.txt")
G = importEdges("../data/myfakecalldata.txt", Nodes)
D = importEdges("../data/myfakecalldata.txt", Nodes, directed = True)
```

### Importing as `pandas` object
Pretty straightforward. Use `attr.head()` and `call.head()` to see the basic structure.
```
attr = importAttr("../data/myfakeattrdata.txt")
call = importCalls("../data/myfakecalldata.txt")
```

## Analyzing
I'll keep building the `analyze` portion of the module as I get more time, but here are some basic things you can do now:
```
olap = overlapDistribution(G)
relativeLWCCsize(D)
summaryStats(attr)

## Directed network stats
DNetworkSummary(D, qtr = 1)

## Undirected network stats
GNetworkSummary(G, qtr = 1)

## Get a list of nodes that subsets out age and sex (see ?agexsexsubset)
agexsex = agexsexsubset(G)
```

