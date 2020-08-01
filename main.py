""" Gather all modules to a one program"""

import main_smoothing
import json_preparation
import sys
from CustomModules import global_vars



global_vars.BOARD_ID = sys.argv[1];
global_vars.REV_ID  = sys.argv[2];
global_vars.INPUT_PATH  = ("/tmp/boards/" + global_vars.BOARD_ID + "/inputs/")
global_vars.OUTPUT_PATH = ("/tmp/boards/" + global_vars.BOARD_ID + "/outputs/")


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
    