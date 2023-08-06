import argparse
from msilib import type_string
from pickle import FALSE

from markupsafe import string
from commands.version import VersionCommand
from commands.init_project import InitProject
from commands.delete_project import DeleteProject

# Defining main function
def main():
    parser = argparse.ArgumentParser(description='Setup requirements project.')
    parser.add_argument('-i', '--init', nargs=1, type=str, default=0,
                        help='init a requirements project in folder INIT')
    parser.add_argument('-d', '--delete', nargs=1, type=str, default=0,
                        help='delete requirements project in folder INIT')
    parser.add_argument('-v', '--version', default=0, action="store_true",
                        help='version of requirements management tool')

    args = parser.parse_args()

    if args.init!=0:
        print("Init project")
        InitProject.execute(args.init[0])

    if args.delete!=0 and args.init==0:
        print("Remove project ")
        DeleteProject.execute(args.delete[0])

    if args.version:
        VersionCommand.execute()

  
  
# Using the special variable 
# __name__
if __name__=="__main__":
    main()
