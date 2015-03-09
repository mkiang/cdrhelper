## Postal Code Data
This is just a collection of data downloaded from AggData.com (see [this link](https://www.aggdata.com/search/node/list%20of%20postal%20codes) for specific query).

## Format
These are all in the format required for the `sourcefile` option of the `generatePostcode()` function.

Specifically, these are delimited with commas, contain a header, and have six columns. The datatype within each column depends on the specific format of that country. In general (but not always), the `head` of the table will look like so:

|Postal Code | Place name | State | County | Latitude | Longitude|
|---|---|---|---|---|---|
1111|StringA|Another StringU|Other StringM|11.2311|53.1231|
1111|StringB|Another StringV|Other StringN|15.2311|32.1231|
1111|StringC|Another StringX|Other StringO|18.2311|82.1231|
1111|StringD|Another StringY|Other StringP|31.2311|56.1231|
1111|StringE|Another StringZ|Other StringQ|86.2311|01.1231|

Obviously, all those numbers are made up, but in general the postal code will be `int` (sometimes a mix of `int` and `char`), names of the place, state, and county will all be `char` and latitude, longitude will be `float`.

## Countries
One day, when I find the time, I'll made a list of the abbreviations for each country. For now, you'll just have to google the state or county name and figure it out.
