""" Gather all modules to a one program"""

import main_smoothing
import json_preparation
from CustomModules import global_vars

on_off = global_vars.OFFLINE_ONLINE 
if on_off:
    import sys
    board_ID = sys.argv[1]
    rev_Id = sys.argv[2]
    input_path = ("/tmp/boards/" + board_ID + "/inputs/")
    output_path = ("/tmp/boards/" + board_ID + "/outputs/")
else:
    import GepettoApp
    board_ID = ""
    rev_Id = ""
    input_path = ""
    output_path = ""

def main():
    if on_off:
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
    else:
        failure = GepettoApp.main()
        if not failure:
            print("GUI FINISHED USER POINTS GENERATED")
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
        else:
            print("GUI Failure")

if __name__ == "__main__":
    main()