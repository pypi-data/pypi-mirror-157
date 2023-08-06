import logging

# Model building and feature ranking related
pytorch_seed = 94
numpy_seed = 904
standard_deviation_scale = [2, -2]
MODEL_THRESHOLD = 0.5

# Plotting-related
FIGSIZE = [5.5, 3.5]  # Adjustment for width and heigth
PLOT_FACE = "whitesmoke"
GRID = True
N_COLUMNS = 5
LABEL_SIZE = 12

# Logging levels for the modules
log = {'data': logging.INFO,
       'feature_ranking': logging.INFO,
       'models': logging.INFO,
       'visualization': 'debug'
       }
