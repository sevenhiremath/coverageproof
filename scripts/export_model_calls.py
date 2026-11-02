"""Explicit private export; raw model output is never printed or published."""
import argparse
from coverageproof.model_diagnostics import export_calls




def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True)
    parser.add_argument('--assessment')
    parser.add_argument('--out',required=True,help='New private directory, preferably under ignored output/')
    args=parser.parse_args()
    count=export_calls(args.db,args.out,args.assessment)
    print(f'Exported {count} model call(s) privately. Do not commit raw output or the database.')

if __name__=='__main__':main()
