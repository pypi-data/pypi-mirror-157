from typing import Optional
from tagasuri.epd import EpdTest


def epd_test(
        enginepath, inputfile, outputfile, masterfile: str = 'master.csv',
        movetime: float = 1.0, engineoptions: Optional[str] = None,
        workers: int = 1, islogging: bool = False,
        enginename: Optional[str] = None):

    a = EpdTest(
        enginepath, inputfile, outputfile, masterfile=masterfile,
        movetime=movetime, engineoptions=engineoptions, workers=workers,
        islogging=islogging, enginename=enginename)

    df = a.start()
    a.save_to_master(df)
    dfs = a.get_summary()
    dfs.columns = ['Name', 'Total', 'Correct', 'Pct', 'Time', 'EPDFile']
    dfs = dfs.sort_values(by=['Correct'], ascending=[False])
    a.save_output(dfs, outputfile)

    # Save unsolved
    dfm = a.get_master()
    dfu = dfm.loc[(dfm.Name == a.enginename) &
        (dfm.Time == a.movetime) &
        (dfm.EPDFile == a.inputfilename) &
        (dfm.Hit == 0)]
    a.save_output(dfu, f'unsolved_{a.inputfilename[:-4]}_{a.movetime}s_{a.enginename}.txt')
