"""The door lock: a servo that moves the bolt, a green LED for granted and a red LED for denied."""

import time

from gpiozero import LED, AngularServo

from config.config import (
    FAIL_COOLDOWN,
    GREEN_LED_PIN,
    RECOGNITION_COOLDOWN,
    RED_LED_PIN,
    SERVO_FRAME_WIDTH,
    SERVO_LOCKED_ANGLE,
    SERVO_MAX_PULSE,
    SERVO_MIN_PULSE,
    SERVO_PIN,
    SERVO_UNLOCKED_ANGLE,
)


class Lock:
    def __init__(self):
        self.servo = AngularServo(
            SERVO_PIN,
            min_pulse_width=SERVO_MIN_PULSE,
            max_pulse_width=SERVO_MAX_PULSE,
            frame_width=SERVO_FRAME_WIDTH,
        )
        self.green_led = LED(GREEN_LED_PIN)
        self.red_led = LED(RED_LED_PIN)
        self.unlocked_at = None
        self.denied_at = None
        self.servo.angle = SERVO_LOCKED_ANGLE

    def unlock(self):
        """Open the lock. It closes again by itself RECOGNITION_COOLDOWN seconds later, see update()."""
        self.green_led.on()
        self.servo.angle = SERVO_UNLOCKED_ANGLE
        self.unlocked_at = time.time()

    def deny(self):
        """Blink the red LED. It is switched off again FAIL_COOLDOWN seconds later, see update()."""
        self.red_led.blink(on_time=0.25, off_time=0.25)
        self.denied_at = time.time()

    def update(self):
        """Call regularly: closes the lock and switches off the red LED once their time is up."""
        now = time.time()
        if self.denied_at is not None and now - self.denied_at > FAIL_COOLDOWN:
            self.red_led.off()
            self.denied_at = None
        if self.unlocked_at is not None and now - self.unlocked_at >= RECOGNITION_COOLDOWN:
            self.servo.angle = SERVO_LOCKED_ANGLE
            self.green_led.off()
            self.unlocked_at = None

    def close(self):
        """Lock and release the GPIO pins."""
        self.servo.angle = SERVO_LOCKED_ANGLE
        self.green_led.close()
        self.red_led.close()
        self.servo.close()
