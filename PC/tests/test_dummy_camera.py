import sys
sys.path.append('.')
from dummy_camera.dummy_camera import calculate_motor_speed


def test_calculate_motor_speed_1():
    # error within deadzone
    ERROR = 10
    DEADZONE = 20
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 1.0

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == 0


def test_calculate_motor_speed_2():
    # motor speed exceeds max speed
    # positive error

    ERROR = 10
    DEADZONE = 0
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 100.0

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == MAX_SPEED


def test_calculate_motor_speed_3():
    # motor speed exceeds max speed
    # negative error

    ERROR = -10
    DEADZONE = 0
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 100.0

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == -MAX_SPEED


def test_calculate_motor_speed_4():
    # motor speed lower than min speed
    # positive error

    ERROR = 10
    DEADZONE = 0
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 0.0001

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == MIN_SPEED

def test_calculate_motor_speed_5():
    # motor speed lower than min speed
    # positive error

    ERROR = -10
    DEADZONE = 0
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 0.0001

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == -MIN_SPEED


def test_calculate_motor_speed_6():
    # motor speed within min and max range
    # positive error

    ERROR = 150
    DEADZONE = 50
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 1.0

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == ERROR


def test_calculate_motor_speed_7():
    # motor speed within min and max range
    # positive error

    ERROR = -150
    DEADZONE = 50
    MIN_SPEED = 100
    MAX_SPEED = 255
    K = 1.0

    motor_speed = calculate_motor_speed(error=ERROR,
        deadzone=DEADZONE,
        min_motor_speed=MIN_SPEED,
        max_motor_speed=MAX_SPEED,
        k=K)

    assert motor_speed == ERROR
