from pynput import keyboard
import time

# TODO: not being used currently, but was thought as a script to validate the timing of the
# platform


class ExperimentValidation:
    def __init__(self):
        # To start: Ctrl + Alt + s
        self.hotkey = keyboard.HotKey(
            keyboard.HotKey.parse("<ctrl>+<alt>+s"), self.on_activate
        )
        self.activated = False
        self.keyboard_controller = keyboard.Controller()

    def on_activate(self):
        self.run()

    def for_canonical(self, f):
        return lambda k: f(self.listener.canonical(k))

    def wait_for_hotkey(self):
        self.listener = keyboard.Listener(
            on_press=self.for_canonical(self.hotkey.press),
            on_release=self.for_canonical(self.hotkey.release),
        )
        self.listener.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                pass

    def run(self):
        for i in range(1, 6):
            self.press_and_release(str(i))
            time.sleep(0.1)

    def press_and_release(self, key):
        self.keyboard_controller.press(key)
        self.keyboard_controller.release(key)


if __name__ == "__main__":
    validation = ExperimentValidation()
    validation.wait_for_hotkey()
