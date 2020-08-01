""" Gather all modules to a one program"""

import main_smoothing
import json_preparation
import sys
from CustomModules import global_vars


board_ID = sys.argv[1]
rev_Id = sys.argv[2]
input_path = ("/tmp/boards/" + board_ID + "/inputs/")
output_path = ("/tmp/boards/" + board_ID + "/outputs/")



def main():

    failure = main_smoothing.main()
    if not failure:
        print("MOTOR PARAMETERS GENERATED")
        failure = json_preparation.main()
        if not failure:
            print("JSON FILES GENERATED")
        else:
            print("JSON FILES GENERATAION FAILED")
    else:
        print("MOTOR PARAMETER GENERATION FAILED")


if __name__ == "__main__":
    main()
    