"""
Analyze epd test with the engine.


Attributes:
  enginefile: The path/filename or filename of the engine to be tested.
  inputfile: The epd test file.
  outputfile: The summary output of the engine.
  masterfile: All analysis are stored in the file. It can be used to
              generate engine results summary, unsolved test and others.
  movetime: Analysis time in seconds.
  engineoptions: Engine options like Hash and Threads.
  workers: Number of cores to use to work on the test. If your processor
           has 4 cores for example, you can use --workers 3.
  islogging: To log engine output and other per worker.
  enginename: To change engine name for display purposes.
"""


from pathlib import Path
from typing import List, Optional
from ast import literal_eval
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor

import chess
import chess.engine
import pandas as pd
from pretty_html_table import build_table
import numpy as np
from tagasuri.logging import create_log_handler


master_header = ['EPD', 'ID', 'Bm', 'Am', 'EngMv', 'Hit', 'Time',
                 'Name', 'EPDFile']


class EpdTest:
    def __init__(self, enginefile: str, inputfile: str, outputfile: str,
                 masterfile: str = 'master.csv',  movetime: float = 1.0,
                 engineoptions: Optional[str] = None, workers: int = 1,
                 islogging: bool = False, enginename: Optional[str] = None):
        self.enginefile = enginefile
        self.engineoptions = engineoptions
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.masterfile = masterfile
        self.movetime = movetime
        self.workers = workers
        self.islogging = islogging
        self.enginename = enginename

        if engineoptions is not None:
            self.engineoptions = literal_eval(engineoptions)
        self.inputfilename = Path(inputfile).name

        if self.enginename is None:
            engine = chess.engine.SimpleEngine.popen_uci(self.enginefile)
            self.enginename = engine.id['name']
            engine.quit()

    def get_epds(self) -> List:
        """Converts epd file to a list.

        Returns:
          A list of epd positions.
        """
        epds = []
        with open(self.inputfile, 'r') as f:
            for lines in f:
                line = lines.rstrip()
                epds.append(line)
        return epds

    def get_master(self) -> None:
        """Get contents of master.csv file.]
        """
        df = pd.read_csv(self.masterfile, names=master_header)
        return df

    def save_to_master(self, df: pd.DataFrame) -> None:
        """Save epd analysis per engine.

        The header is ['EPD', 'BestMv', 'EngMv', 'Hit', 'Time', 'Name']
        """
        df.to_csv(self.masterfile, mode='a', index=False, header=None)

    def get_summary(self):
        """Gets result summary of engine tests.
        """
        df = pd.read_csv(self.masterfile, names=master_header)
        epdfilename = self.inputfilename
        movetime = self.movetime
        dft = df.loc[(df['EPDFile'] == epdfilename) & (df['Time'] == movetime)]
        names = dft.Name.unique()

        data = []
        for n in names:
            totalpos = len(df.loc[(df['Name'] == n) &
                                  (df['EPDFile'] == epdfilename) &
                                  (df['Time'] == movetime)])
            correct = len(df.loc[(df.Name == n) & (df.Hit == 1) &
                                 (df.EPDFile == epdfilename) &
                                 (df.Time == movetime)])
            pct = round(100 * correct / totalpos, 2)
            data.append([n, totalpos, correct, pct, movetime, epdfilename])
        return pd.DataFrame(data)

    def save_output(
            self, df: pd.DataFrame, fn: str,
            tablecolor: str = 'blue_light') -> None:
        """Save the output to a file.

        The output can be a csv, txt and html.
        Args:
          df: A pandas dataframe.
          fn: The output filename.
          tablecolor: The table color for html output.
        """
        ext = Path(fn).suffix
        if ext == '.html':
            html_table = build_table(
                df,
                tablecolor,
                font_size='medium',
                text_align='center',
                font_family='Calibri, Verdana, Tahoma, Georgia, serif, arial')
            with open(fn, 'w') as f:
                f.write(html_table)
        elif ext == '.csv':
            df.to_csv(fn, index=False)
        else:
            df.to_string(fn, index=False)

    def run(self, epds, num) -> pd.DataFrame:
        """Test the engine on the test file.

        Save number of correct and all positins counts.

        Returns:
          A dataframe of analysis results.
        """
        if self.islogging:
            logger = create_log_handler(f'run_{num}')
            logger.info(f'engine: {self.enginename}')

        data = []
        engine = chess.engine.SimpleEngine.popen_uci(self.enginefile)
        if self.islogging:
            logger.info(engine.options)
        if self.engineoptions is not None:
            for k, v in self.engineoptions.items():
                if k in engine.options:
                    engine.configure({k: v})
                    if self.islogging:
                        logger.info(f'set {k} to value {v}')

        for epd in epds:
            if self.islogging:
                logger.info(epd)
            ok = 0
            board, info = chess.Board.from_epd(epd)
            bms = info.get('bm', None)
            ams = info.get('am', None)
            id = info.get('id', None)
            bepd = board.epd()
            result = engine.analyse(
                board,
                chess.engine.Limit(time=self.movetime), game=object())

            if self.islogging:
                logger.info(result)

            move = result['pv'][0]
            sanmv = board.san(move)

            if self.islogging:
                logger.info(f'engine bestmove: {sanmv}')

            if bms is not None and ams is not None:
                if move in bms and move not in ams:
                    ok = 1
            elif bms is not None and move in bms:
                ok = 1
            elif ams is not None and move not in ams:
                ok = 1

            if self.islogging:
                logger.info(f'solved: {ok}')

            if bms is not None:
                bms_l = [board.san(m) for m in bms]
                bms_h = ' '.join(bms_l)
            else:
                bms_h = None

            if ams is not None:
                ams_l = [board.san(m) for m in ams]
                ams_h = ' '.join(ams_l)
            else:
                ams_h = None

            data.append(
                [bepd, id, bms_h, ams_h, sanmv,
                 ok, self.movetime, self.enginename, self.inputfilename])
        engine.quit()
        df = pd.DataFrame(data, columns=master_header)
        return df

    def start(self):
        job_list = []
        epds = self.get_epds()
        splits = np.array_split(epds, self.workers)
        dflist = []

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            for i, epdv in enumerate(splits):
                s_epd = list(epdv)
                job = executor.submit(self.run, s_epd, i)
                job_list.append(job)

            for future in concurrent.futures.as_completed(job_list):
                try:
                    df = future.result()
                    dflist.append(df)
                except concurrent.futures.process.BrokenProcessPool as ex:
                    print(f'{ex}')

        df = pd.concat(dflist)
        return df
