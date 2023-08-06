import argparse
import tagasuri
from tagasuri.app import epd_test


def main():
    parser = argparse.ArgumentParser()

    # Common parsers
    output_parser = argparse.ArgumentParser(add_help=False)
    output_parser.add_argument(
        '--output-file', type=str, required=True,
        help='Output file, .csv, .txt, .html. Required=True.')

    input_parser = argparse.ArgumentParser(add_help=False)
    input_parser.add_argument(
        '--input-file', type=str, required=True,
        help='Input epd file. Required=True.')

    engine_parser = argparse.ArgumentParser(add_help=False)
    engine_parser.add_argument(
        '--engine-file', type=str, required=True,
        help='Input engine file. Required=True.')

    engine_options_parser = argparse.ArgumentParser(add_help=False)
    engine_options_parser.add_argument(
        '--engine-options', type=str, required=False, default=None,
        help='Input engine options. Required=False, default=None')

    move_time_parser = argparse.ArgumentParser(add_help=False)
    move_time_parser.add_argument(
        '--move-time', type=float, required=False,
        default=1.0,
        help='Input movetime in seconds. Required=False, default=1.0')

    # Sub parsers
    subparser = parser.add_subparsers(dest='command')

    epdtest = subparser.add_parser(
        'epd-test',
        parents=[input_parser, output_parser, engine_parser,
                 engine_options_parser, move_time_parser],
        help='Test the engine with puzzles in epd file.')

    # Additional options
    epdtest.add_argument(
        '--master-file', type=str, required=False, default='master.csv',
        help='The output master file to save all the analysis. '
        'Required=False, default=master.csv.')
    epdtest.add_argument(
        '--workers', type=int, required=False, default=1,
        help='The number of workers to work on the epd to speed up the process. '
        'If your processor has quad or 4 cores, you may use 3 cores. '
        'Required=False, default=1.')
    epdtest.add_argument(
        '--islogging', action='store_true',
        help='Log output to file by process id.')
    epdtest.add_argument(
        '--engine-name', type=str, required=False, default=None,
        help='Engine name, if not specified it will use engine id name.')

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{tagasuri.__version__}')

    args = parser.parse_args()

    if args.command == 'epd-test':
        if args.input_file == args.output_file:
            raise ValueError('Input and output filenames '
                             'should not be the same!')

        epd_test(
            args.engine_file, args.input_file, args.output_file,
            masterfile=args.master_file, movetime=args.move_time,
            engineoptions=args.engine_options, workers=args.workers,
            islogging=args.islogging, enginename=args.engine_name)


if __name__ == '__main__':
    main()
