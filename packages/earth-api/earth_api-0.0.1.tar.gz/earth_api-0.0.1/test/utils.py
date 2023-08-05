POSITION_FIELD = "position"
TILT_FIELD = "tilt"
API_VERSION_CURRENT = "1.16"
API_VERSION_1_12 = "1.12"
API_VERSION_1_0 = "1.0"


def is_equal(a, b):
    if abs(a-b) < 0.00001:
        return True
    else:
        return False
