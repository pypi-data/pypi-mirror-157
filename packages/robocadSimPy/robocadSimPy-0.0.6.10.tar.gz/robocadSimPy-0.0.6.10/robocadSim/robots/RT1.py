from .dev import connection_helper
from . import line_sensor_cls
from .dev.holder import *


class RT1:
    """
    Class for RT-1 robot
    """

    def __init__(self):
        self.__right_motor_speed = 0.0
        self.__left_motor_speed = 0.0
        self.__back_motor_speed = 0.0

        self.__right_motor_enc = 0.0
        self.__left_motor_enc = 0.0
        self.__back_motor_enc = 0.0

        self.__reset_right_enc = False
        self.__reset_left_enc = False
        self.__reset_back_enc = False

        self.__reset_imu = False

        self.__button_ems = False
        self.__button_start = False
        self.__button_reset = False
        self.__button_stop = False

        self.__led_green = False
        self.__led_red = False

        self.__right_us = 0.0
        self.__left_us = 0.0
        self.__right_ir = 0.0
        self.__left_ir = 0.0
        self.__imu = 0.0
        self.__line_sensor = line_sensor_cls.LineSensor()

        self.__connection_helper = connection_helper.ConnectionHelper(CONN_OTHER | CONN_MOTORS_AND_ENCS |
                                                                      CONN_RESETS | CONN_SENS | CONN_BUTTONS)

    def connect(self):
        self.__connection_helper.start_channels()

    def disconnect(self):
        self.__connection_helper.stop_channels()

    def __update_other(self):
        self.__connection_helper.set_other(
                (
                    int(self.__led_green),
                    int(self.__led_red),
                ))

    def __update_motors(self):
        self.__connection_helper.set_motors(
            (
                self.__right_motor_speed,
                self.__left_motor_speed,
                self.__back_motor_speed,
            ))

    def __update_resets(self):
        self.__connection_helper.set_resets(
            (
                self.__reset_right_enc,
                self.__reset_left_enc,
                self.__reset_back_enc,
                self.__reset_imu,
            ))

    def __update_encs(self):
        values = self.__connection_helper.get_encs()
        if len(values) == 3:
            self.__right_motor_enc = values[0]
            self.__left_motor_enc = values[1]
            self.__back_motor_enc = values[2]

    def __update_sensors(self):
        values = self.__connection_helper.get_sens()
        if len(values) == 9:
            self.__right_us = values[0]
            self.__left_us = values[1]
            self.__right_ir = values[2]
            self.__left_ir = values[3]
            self.__imu = values[4]
            self.__line_sensor.s1 = values[5]
            self.__line_sensor.s2 = values[6]
            self.__line_sensor.s3 = values[7]
            self.__line_sensor.s4 = values[8]

    def __update_buttons(self):
        values = self.__connection_helper.get_buttons()
        if len(values) == 4:
            self.__button_ems = values[0]
            self.__button_start = values[1]
            self.__button_reset = values[2]
            self.__button_stop = values[3]

    @property
    def right_motor_speed(self):
        return self.__right_motor_speed

    @right_motor_speed.setter
    def right_motor_speed(self, value):
        self.__right_motor_speed = value
        self.__update_motors()

    @property
    def left_motor_speed(self):
        return self.__left_motor_speed

    @left_motor_speed.setter
    def left_motor_speed(self, value):
        self.__left_motor_speed = value
        self.__update_motors()

    @property
    def back_motor_speed(self):
        return self.__back_motor_speed

    @back_motor_speed.setter
    def back_motor_speed(self, value):
        self.__back_motor_speed = value
        self.__update_motors()

    @property
    def reset_right_enc(self):
        return self.__reset_right_enc

    @reset_right_enc.setter
    def reset_right_enc(self, value):
        self.__reset_right_enc = value
        self.__update_resets()

    @property
    def reset_left_enc(self):
        return self.__reset_left_enc

    @reset_left_enc.setter
    def reset_left_enc(self, value):
        self.__reset_left_enc = value
        self.__update_resets()

    @property
    def reset_back_enc(self):
        return self.__reset_back_enc

    @reset_back_enc.setter
    def reset_back_enc(self, value):
        self.__reset_back_enc = value
        self.__update_resets()

    @property
    def reset_imu(self):
        return self.__reset_imu

    @reset_imu.setter
    def reset_imu(self, value):
        self.__reset_imu = value
        self.__update_resets()

    @property
    def led_green(self):
        return self.__led_green

    @led_green.setter
    def led_green(self, value):
        self.__led_green = value
        self.__update_other()

    @property
    def led_red(self):
        return self.__led_red

    @led_red.setter
    def led_red(self, value):
        self.__led_red = value
        self.__update_other()

    @property
    def right_motor_enc(self):
        self.__update_encs()
        return self.__right_motor_enc

    @property
    def left_motor_enc(self):
        self.__update_encs()
        return self.__left_motor_enc

    @property
    def back_motor_enc(self):
        self.__update_encs()
        return self.__back_motor_enc

    @property
    def button_ems(self):
        self.__update_buttons()
        return self.__button_ems

    @property
    def button_start(self):
        self.__update_buttons()
        return self.__button_start

    @property
    def button_reset(self):
        self.__update_buttons()
        return self.__button_reset

    @property
    def button_stop(self):
        self.__update_buttons()
        return self.__button_stop

    @property
    def line_sensor(self) -> line_sensor_cls.LineSensor:
        self.__update_sensors()
        return self.__line_sensor

    @property
    def right_us(self):
        self.__update_sensors()
        return self.__right_us

    @property
    def left_us(self):
        self.__update_sensors()
        return self.__left_us

    @property
    def right_ir(self):
        self.__update_sensors()
        return self.__right_ir

    @property
    def left_ir(self):
        self.__update_sensors()
        return self.__left_ir

    @property
    def imu(self):
        self.__update_sensors()
        return self.__imu
