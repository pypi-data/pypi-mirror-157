# Tagasuri
An application that will test a computer chess program on epd test suites.

It detects avoid move `am` and supports parallel test for processors with more than 1 core.

All test results are saved in master.csv file for later processing. Output summary can be saved either in csv, txt and html file formats.

## Installation
`pip install -U tagasuri`


## Dependencies
Tagasuri is dependent on the following packages:

1. python chess
2. pandas
3. pretty-html-table

They are installed automatically when tagasuri is installed.


## Command line

Test the engine with a chess puzzle in epd file.

```
tagasuri epd-test --input-file "7men_human.epd" --engine-file "c:/engines/sf15.exe" --engine-options "{'Hash': 128, 'Threads': 1}" --workers 1 --move-time 1 --output-file 7men.txt
```

Unsolved puzzles are saved in `unsolved_7men_human_1.0s_Stockfish 15.txt.`

Sample output

```
                       Name  Total  Correct   Pct  Time        EPDFile
               Stockfish 15   1110     1103 99.37   1.0 7men_human.epd
Lc0 v0.29.0-dev+git.025105e   1110     1096 98.74   1.0 7men_human.epd
      Komodo 12.1.1 64-bit    1110     1064 95.86   1.0 7men_human.epd
                 Texel 1.07   1110     1045 94.14   1.0 7men_human.epd
                 Cheng 4.40   1110     1042 93.87   1.0 7men_human.epd
         CT800 V1.43 64 bit   1110     1023 92.16   1.0 7men_human.epd
                CDrill 1800   1110      899 80.99   1.0 7men_human.epd
```

If your processor has a quad or 4 cores, you can increase the workers to 3 with `--workers 3` for example to finish the test early. If you use Lc0 with GPU and your system has only 1 GPU just use `--workers 1`.

#### Output
*All test results are saved in master.csv file. If Hit value is 1 that means the puzzle is solved.*

```
c:\tmp_tagasuri> python

>>> import pandas as pd

>>> df = pd.read_csv('master.csv', names=['EPD', 'ID', 'Bm', 'Am', 'EngMv', 'Hit', 'Time', 'Name', 'EPDFile'])
>>> df
                                     EPD              ID   Bm  Am EngMv  Hit  Time          Name         EPDFile
0       8/8/2k3K1/8/7P/R5P1/p4r2/8 b - -     7menhuman_1  Rg2 NaN   Rg2    1   1.0  Stockfish 15  7men_human.epd
1     8/8/6k1/3p4/3P4/4K1p1/7p/2R5 b - -     7menhuman_2   g2 NaN    g2    1   1.0  Stockfish 15  7men_human.epd
2       8/8/p4pk1/8/4P3/5P2/1K6/n7 w - -     7menhuman_3   f4 NaN    f4    1   1.0  Stockfish 15  7men_human.epd
3         8/7k/5Kp1/7p/2r4P/8/8/R7 w - -     7menhuman_4  Rh1 NaN   Rh1    1   1.0  Stockfish 15  7men_human.epd
4      8/3n4/5kp1/3P3p/8/3K4/8/3B4 b - -     7menhuman_5  Ke5 NaN   Ke5    1   1.0  Stockfish 15  7men_human.epd
...                                  ...             ...  ...  ..   ...  ...   ...           ...             ...
1105  8/5p2/2K1n1p1/2P5/P7/4k3/8/8 w - -  7menhuman_1106   a5 NaN    a5    1   1.0  Stockfish 15  7men_human.epd
1106    8/8/rP2k3/4pp2/2R5/2K5/8/8 w - -  7menhuman_1107   b7 NaN    b7    1   1.0  Stockfish 15  7men_human.epd
1107     8/8/2k5/1p6/5p1P/KPP5/8/8 w - -  7menhuman_1108   h5 NaN    h5    1   1.0  Stockfish 15  7men_human.epd
1108  5k2/R7/8/1K1N4/6r1/1P3p2/8/8 b - -  7menhuman_1109   f2 NaN    f2    1   1.0  Stockfish 15  7men_human.epd
1109    8/8/8/4Rpk1/3r4/5Pp1/8/5K2 w - -  7menhuman_1110  Kg2 NaN   Kg2    1   1.0  Stockfish 15  7men_human.epd
```

## Link

* [tagasuri python package](https://pypi.org/project/tagasuri/)


## Help
Access help from command line.

`tagasuri -h`

`tagasuri epd-test -h`

## Credits
* [Python chess](https://python-chess.readthedocs.io/en/latest/)
* [Pandas](https://pandas.pydata.org/)
* [pretty-html-table](https://pypi.org/project/pretty-html-table/)

## Change Log

### Version 0.5.0 [2022-07-05]

**Bug fix**
* Fix logging

**New Feature**
* Add --engine-name option

Example:  
`tagasuri epd-test --engine-name "Lc0 0.29 rc0" --engine-file "c:/chess/engines/lc0/lc0_0.29/lc0.exe" ...`


