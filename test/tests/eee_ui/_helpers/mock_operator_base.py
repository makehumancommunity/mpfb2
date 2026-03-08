"""MockOperatorBase: simulates the 'self' argument passed to Operator.execute()."""

from .mock_report import MockReport


class MockOperatorBase:
    """Simulates the 'self' argument passed to Operator.execute() / hardened_execute()."""

    def __init__(self, **kwargs):
        self.mock_report = MockReport()
        self.report = self.mock_report   # wired as callable
        self.filepath = ""
        self.armature_type = "default"
        for k, v in kwargs.items():
            setattr(self, k, v)
