## Population (Age * Sex) Data
Collection of randomly generated population structure files --- note: they are **very** random and will likely not reflect a true population. I just made it as a positive control and to display the proper format.

## Format
These are all in the format required for the `sourcefile` option of the `generatePopulation()` function.

Specifically, these are delimited with commas, contain a header, and have four columns (though the header has an empty left column). The datatype within each column is `int`. In general (but not always), the `head` of the table will look like so:

||Both sexes| Males | Females | 
|---|---|---|---|
0|59335|30330|29005
1|61440|31532|29908
2|62184|32035|30149
3|63986|32758|31228
4|64967|33362|31605
5|63832|32859|30973

Obviously, all those numbers are made up. The leftmost column (missing header) is the age and the right three columns represent the count of people in that population. Thus, there are 59335 infants in this population (30330 of whom are male).

## Real Examples
As I get more time, I'll get real data from counties and generate `csv`s that match this format.

