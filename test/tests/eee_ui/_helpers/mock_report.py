"""MockReport: records operator self.report() calls for assertions in tests."""


class MockReport:
    """Records operator self.report() calls as (type_str, message) tuples."""

    def __init__(self):
        self.reports = []

    def __call__(self, reporttype, reportmessage):
        """Callable wired as self.report in MockOperatorBase."""
        type_str = next(iter(reporttype))
        self.reports.append((type_str, reportmessage))

    def assert_no_errors(self):
        errors = [r for r in self.reports if r[0] == 'ERROR']
        assert not errors, f"Expected no errors, got: {errors}"

    def assert_reported(self, type_str, substring):
        matches = [r for r in self.reports if r[0] == type_str and substring in r[1]]
        assert matches, (
            f"Expected a {type_str!r} report containing {substring!r}. "
            f"All reports: {self.reports}"
        )
