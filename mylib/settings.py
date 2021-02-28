# config file
CONFIG_FILE = 'config/ui_config.json'

# roi
CAMERA_ROI = [
    [0.14, 0.07, 0.875, 0.89],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
    [0.01, 0.05, 0.96, 0.95],
]

# engine
RUN_MODE_THREAD = True
RESIZE_FACTOR = 1.0
DISPLAY_DETECT_FRAME_ONLY = False
COUNTING_INTEGRATE = True
SEND_SQL = False
SAVE_PATH = 'videos'

# detector
DETECT_ENABLE = False
DETECTION_THRESHOLD = 0.1

# tracker
TRACKER_THRESHOLD_DISTANCE = 90  # 90
TRACKER_BUFFER_LENGTH = 100
TRACKER_KEEP_LENGTH = 30

# UI
PIECE_WIDTH = 510
PIECE_HEIGHT = 300
