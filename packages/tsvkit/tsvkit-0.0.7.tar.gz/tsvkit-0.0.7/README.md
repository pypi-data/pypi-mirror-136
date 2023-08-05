# tsvkit

TSV toolkit

## Install

```shell
pip install tsvkit==0.0.7
```

## Usage

```
$ tsvkit --help
usage: tsvkit [-h] [-H] [-v] [-s] [-p PATTERN] [-l LIMIT] [-n NLINES] [-c COLUMN] [-V] [input]

TSV toolkit v0.0.7

positional arguments:
  input                 file to parse, tab-delimited, default: stdin

optional arguments:
  -h, --help            show this help message and exit
  -H, --header          print header or include header in the output
  -v, --view            aligned display of each column
  -s, --stat            descriptive statistics
  -p PATTERN, --pattern PATTERN
                        pattern to match, wrap in single quotes
  -l LIMIT, --limit LIMIT
                        limit of column width, used with -v, default 100
  -n NLINES, --nlines NLINES
                        max number of lines to view, used with -v, default 100
  -c COLUMN, --column COLUMN
                        column number to match (1-based), used with -s or -p, default all columns
  -V, --version         show program's version number and exit
```

## Example

```
$ head data.tsv 
instant	weekday	workingday	weathersit	temp	atemp	hum	windspeed	casual	registered	cnt
1	6	0	2	0.344167	0.363625	0.805833	0.160446	331	654	985
2	0	0	2	0.363478	0.353739	0.696087	0.248539	131	670	801
3	1	1	1	0.196364	0.189405	0.437273	0.248309	120	1229	1349
4	2	1	1	0.2	0.212122	0.590435	0.160296	108	1454	1562
5	3	1	1	0.226957	0.22927	0.436957	0.1869	82	1518	1600
6	4	1	1	0.204348	0.233209	0.518261	0.0895652	88	1518	1606
7	5	1	2	0.196522	0.208839	0.498696	0.168726	148	1362	1510
8	6	0	2	0.165	0.162254	0.535833	0.266804	68	891	959
9	0	0	1	0.138333	0.116175	0.434167	0.36195	54	768	822
```

### print header or include header in output

```
$ tsvkit -H data.tsv 
1	instant
2	weekday
3	workingday
4	weathersit
5	temp
6	atemp
7	hum
8	windspeed
9	casual
10	registered
11	cnt
```

### aligned display of each column

```
$ head data.tsv | tsvkit -v
instant  weekday  workingday  weathersit  temp      atemp     hum       windspeed  casual  registered  cnt
1        6        0           2           0.344167  0.363625  0.805833  0.160446   331     654         985
2        0        0           2           0.363478  0.353739  0.696087  0.248539   131     670         801
3        1        1           1           0.196364  0.189405  0.437273  0.248309   120     1229        1349
4        2        1           1           0.2       0.212122  0.590435  0.160296   108     1454        1562
5        3        1           1           0.226957  0.22927   0.436957  0.1869     82      1518        1600
6        4        1           1           0.204348  0.233209  0.518261  0.0895652  88      1518        1606
7        5        1           2           0.196522  0.208839  0.498696  0.168726   148     1362        1510
8        6        0           2           0.165     0.162254  0.535833  0.266804   68      891         959
9        0        0           1           0.138333  0.116175  0.434167  0.36195    54      768         822

$ head data.tsv | tsvkit -v -l 5
insta  weekd  worki  weath  temp   atemp  hum    winds  casua  regis  cnt
1      6      0      2      0.344  0.363  0.805  0.160  331    654    985
2      0      0      2      0.363  0.353  0.696  0.248  131    670    801
3      1      1      1      0.196  0.189  0.437  0.248  120    1229   1349
4      2      1      1      0.2    0.212  0.590  0.160  108    1454   1562
5      3      1      1      0.226  0.229  0.436  0.186  82     1518   1600
6      4      1      1      0.204  0.233  0.518  0.089  88     1518   1606
7      5      1      2      0.196  0.208  0.498  0.168  148    1362   1510
8      6      0      2      0.165  0.162  0.535  0.266  68     891    959
9      0      0      1      0.138  0.116  0.434  0.361  54     768    822
```

### descriptive statistics

```
$ tsvkit -s -H -v data.tsv 
column  instant  weekday  workingday  weathersit  temp    atemp   hum     windspeed  casual    registered  cnt
count   50       50       50          50          50      50      50      50         50        50          50
min     1.0      0.0      0.0         1.0         0.0591  0.0791  0.1879  0.0454     9.0       416.0       431.0
max     50.0     6.0      1.0         3.0         0.5217  0.512   0.9292  0.5075     579.0     2348.0      2927.0
mean    25.5     3.06     0.68        1.4         0.2271  0.2327  0.5656  0.2088     136.98    1283.68     1420.66
median  25.5     3.0      1.0         1.0         0.2078  0.226   0.5367  0.1914     90.5      1321.5      1486.5
std     14.4309  2.024    0.4665      0.5292      0.0877  0.085   0.1515  0.092      123.3146  406.043     451.2542
```

### pattern to match

```
$ cat data.tsv | tsvkit -p '$1>40' -H -v
instant  weekday  workingday  weathersit  temp      atemp     hum       windspeed  casual  registered  cnt
41       4        1           1           0.144348  0.149548  0.437391  0.221935   47      1491        1538
42       5        1           1           0.189091  0.213509  0.506364  0.10855    149     1597        1746
43       6        0           1           0.2225    0.232954  0.544167  0.203367   288     1184        1472
44       0        0           1           0.316522  0.324113  0.457391  0.260883   397     1192        1589
45       1        1           1           0.415     0.39835   0.375833  0.417908   208     1705        1913
46       2        1           1           0.266087  0.254274  0.314348  0.291374   140     1675        1815
47       3        1           1           0.318261  0.3162    0.423478  0.251791   218     1897        2115
48       4        1           1           0.435833  0.428658  0.505     0.230104   259     2216        2475
49       5        1           1           0.521667  0.511983  0.516667  0.264925   579     2348        2927
50       6        0           1           0.399167  0.391404  0.187917  0.507463   532     1103        1635

$ cat data.tsv | tsvkit -p '0\.1\d+[5-9]$' -c 5 -H -v
instant  weekday  workingday  weathersit  temp      atemp     hum       windspeed  casual  registered  cnt
8        6        0           2           0.165     0.162254  0.535833  0.266804   68      891         959
12       3        1           1           0.172727  0.160473  0.599545  0.304627   25      1137        1162
13       4        1           1           0.165     0.150883  0.470417  0.301      38      1368        1406
14       5        1           1           0.16087   0.188413  0.537826  0.126548   54      1367        1421
21       5        1           1           0.1775    0.157833  0.457083  0.353242   75      1468        1543
27       4        1           1           0.195     0.2197    0.6875    0.113837   15      416         431
34       4        1           1           0.186957  0.177878  0.437826  0.277752   61      1489        1550
41       4        1           1           0.144348  0.149548  0.437391  0.221935   47      1491        1538
```

