LOG_ALL: int = 0  # печатает все
LOG_EXC_INFO: int = 1  # все, кроме простой информации
LOG_EXC_WARN: int = 2  # все, кроме предупреждений
LOG_NOTHING: int = 3  # ничего

LOG_LEVEL: int = LOG_EXC_WARN

# для connection helper
CONN_OTHER: int = 0x0001
CONN_MOTORS_AND_ENCS: int = 0x0002
CONN_OMS: int = 0x0004
CONN_RESETS: int = 0x0008
CONN_SENS: int = 0x0010
CONN_BUTTONS: int = 0x0020
CONN_CAMERA: int = 0x0040


class ConnectionResetWarning(Warning):
    pass
