"""Stand-in for Lock when running without the Pi hardware: prints instead of moving the servo and LEDs."""

import time

from config import FAIL_COOLDOWN, RECOGNITION_COOLDOWN


class FakeLock:
    def __init__(self):
        self.unlocked_at = None
        self.denied_at = None
        print("[lock] fake lock in use, locked")

    def unlock(self):
        print("[lock] UNLOCKED (green LED on)")
        self.unlocked_at = time.time()

    def deny(self):
        print("[lock] DENIED (red LED blinking)")
        self.denied_at = time.time()

    def update(self):
        now = time.time()
        if self.denied_at is not None and now - self.denied_at > FAIL_COOLDOWN:
            print("[lock] red LED off")
            self.denied_at = None
        if self.unlocked_at is not None and now - self.unlocked_at >= RECOGNITION_COOLDOWN:
            print("[lock] locked (green LED off)")
            self.unlocked_at = None

    def close(self):
        print("[lock] closed")
