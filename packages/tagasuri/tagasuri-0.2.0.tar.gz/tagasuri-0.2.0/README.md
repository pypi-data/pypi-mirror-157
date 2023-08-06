# Tagasuri
An application that will test a computer game program on epd test suites.

## Installation
`pip install tagasuri`


## Command line

#### Test engine

```
tagasuri epd-test --input-file "eret.epd" --engine-file "c:/engines/sf15.exe" --engine-options "{'Hash': 128, 'Threads': 1}" --move-time 5 --output-file eret.txt
```

Sample output

```
              Name  Total  Correct   Pct  Time  EPDFile
      Stockfish 15    111       90 81.08   5.0 eret.epd
       CDrill 1800    111       16 14.41   5.0 eret.epd
        Cheng 4.40    111       16 14.41   5.0 eret.epd
CT800 V1.43 64 bit    111       10  9.01   5.0 eret.epd
```

## Access help

`tagasuri -h`

`tagasuri epd-test -h`
