# Segmentation evaluation

This scripts reads two files.  
It compares the number of sentences and the average of words in sentences.  
Then, it counts sentences whose ending word match.

It can also print sentences with matching cut or unmatching cut.

Arguments:
```
  evaluated_file        Specify the file to evaluate
  reference_file        Specify the reference file
```

optional arguments:
```
  -h, --help            show this help message and exit
  -c, --color           Print colors (default: false)
  -m, --matching-cuts   Prints phrases with matching cut
  -u, --unmatched       Prints phrases with unmatched cuts (from both files)
  -v, --verbose         Display statistics and phrases with matching cut
  -w WORDS, --words WORDS
                        Define the number of words to print; 0 will print full sentences
```

## Test

Run:

`python eval.py auto.txt manuel.txt -v -c -w 0`
