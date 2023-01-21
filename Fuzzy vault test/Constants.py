""" All changeable constants for fuzzy vault """

# Constants variable
POLY_DEGREE = 8
MINUTIAE_POINTS_AMOUNT = 30
CHAFF_POINTS_AMOUNT = 300

# Constants fixed
# Galois field exponent
GF_2_M = 32
CRC_LENGTH = 32

# input files
FP_TEMP_FOLDER = 'temp_fp/'
FP_OUTPUT_NAME = 'temp_fp'
VAULT_LOG_FOLDER = 'vault/'
VAULT_LOG_FILENAME = 'vault.txt'

# Distance that minutiae (genuine minutiae and chaff points) have to at least be apart
POINTS_DISTANCE = 10

# Check if chaff point mapping is on polynomial
CHECK_CHAFF_POINT_MAPPING = True

# Constants Vault_Verifier
X_THRESHOLD = 7 #12
Y_THRESHOLD = 7 #12
THETA_THRESHOLD = 7 #12
TOTAL_THRESHOLD = 16 #25
BASIS_THETA_THRESHOLD = 7 #10

# max threshold expected in fingerprint picture
MAX_ITERATION_THRESHOLD = 27000000

# threshold for geometric hashing: should be exactly POLY_DEGREE + 1 to ensure correctness
MATCH_THRESHOLD = POLY_DEGREE + 1

# # How many times the database is iterated through (at each iteration, parameters can be changed below
# # with CHANGE_* constants.
# RUN_DB_ITERATIONS = 4
# # Reuse generated vault for the same gallery template
# REUSE_VAULT = True
# Threshold to define when to use random subset evaluation
SUBSET_EVAL_THRES = 25
# Use random subset evaluation instead of generation of all subsets upfront
RANDOM_SUBSET_EVAL = True
# # Run 1vs1 and FVC protocol instead of all possible matches
# ONE_TO_ONE_FVC_PROTOCOL = True
# # Check if chaff point mapping is on polynomial
# CHECK_CHAFF_POINT_MAPPING = True