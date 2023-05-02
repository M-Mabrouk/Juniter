import asyncio
import sys
import argparse
import Juniter
import pandas as pd

def progress(info):
    print("The current progress is {0} out of {1} steps".format(info['current'], info['total']), end='\r')

def main():

    parser = argparse.ArgumentParser(description='Process plain java projects with junit tests.')
    parser.add_argument('projects', metavar='P', type=str, help='path to the projects\' compressed file')
    parser.add_argument('tests', metavar='T', type=str, help='path to the tests\' compressed file')
    parser.add_argument('-m', '--mapping', metavar='M', type=str, help='path to the mapping file')
    parser.add_argument('-o', '--output', metavar='O', type=str, help='path to the output directory')
    args = parser.parse_args()

    Juniter.clear_files()
    if not Juniter.bootstrap(args.projects, args.tests):
        print("Could not bootstrap the projects and tests.")
        return None
    map = None
    if args.mapping is not None:
        df = pd.read_csv(args.mapping)
        map = dict()
        for i in range(len(df)):
            map[str(df.iloc[i, 0])] = str(df.iloc[i, 1])
    if args.output is not None:
        Juniter.save_results(asyncio.run(Juniter.run(progress=progress, mapping=map)), args.output)
    else:
         Juniter.save_results(asyncio.run(Juniter.run(progress=progress, mapping=map)))
    Juniter.clear_files()

if __name__ == "__main__":
	main()