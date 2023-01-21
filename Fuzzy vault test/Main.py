from App import capture_new_fp_xyt, enroll_new_fingerprint

from Strings import *
from Constants import *

if __name__ == '__main__':
    enrolling_fp = "FP dataset/Real/1__M_Left_index_finger.jpg"
    verifying_fp = ""
    
    print("Start Enrolling")
    #  Enroll a new fingerprint
    good_fp = False
    
    ## Capture a new fingerprint
    good_fp = capture_new_fp_xyt(enrolling_fp)
    
    ## If good fp enroll
    ## else error
    if not good_fp:
        print(APP_RETRY_FP)
    else:
        enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.xyt')
    
    
    
    
    