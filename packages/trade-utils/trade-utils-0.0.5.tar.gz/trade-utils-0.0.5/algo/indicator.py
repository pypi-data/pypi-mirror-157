
class Indicator:
    pass


class MAverage(Indicator):
    def __init__(self, period: int) -> None:
        self._data_stack = []
        self._period = int(period)

    def tick(self, new_data: float) -> None:
        self._data_stack.append(new_data)
        if len(self._data_stack) > self._period:
            self._data_stack.pop(0)

    def ready(self):
        """true if there is enough data"""
        return len(self._data_stack) == self._period

    @property
    def value(self) -> float:
        return sum(self._data_stack) / len(self._data_stack)

    def __str__(self) -> str:
        return f'<MAverage({self._period}): {self.value}>'
