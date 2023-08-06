import sys

if __name__ == "__main__":

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()

from PyQt6.QtWidgets import QProgressBar


from q2gui.pyqt6.q2widget import Q2Widget


class q2progressbar(QProgressBar, Q2Widget):
    def __init__(self, meta):
        super().__init__(meta)
        self.set_text(meta["label"])
        self.setMaximum(0)
        self.setMinimum(0)

    # def showEvent(self, a0):
        # self.parent().setFixedHeight(100)
        # self.parent().parent().setFixedHeight(200)
        # self.parent().parent().parent().setFixedHeight(100)
        # return super().showEvent(a0)

    def set_max(self, value):
        self.setMaximum(value)

    def set_min(self, value):
        self.setMinimum(value)

    def set_value(self, value):
        self.setValue(value)
