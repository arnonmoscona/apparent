#  Copyright (c) Arnon Moscona 2023. under Apache2 license
import statistics
from unittest import TestCase

from apparent.timing import RunningVariance

S1 = [1.5, 2.5, 2.5, 2.75, 3.25, 4.75]
S2 = [0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25]
S3 = [2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5]
EXAMPLES = (S1, S2, S3)


class VarianceTests(TestCase):
    def setUp(self) -> None:
        self.v1 = RunningVariance()
        self.v2 = RunningVariance()
        self.v3 = RunningVariance()
        self.variances = (self.v1, self.v2, self.v3)

        for v, s in ((self.v1, S1), (self.v2, S2), (self.v3, S3)):
            for x in s:
                v.add(x)

    def test_n(self):
        expected = [len(s) for s in EXAMPLES]
        actual = [v.n for v in self.variances]
        self.assertEqual(expected, actual)

    def test_mean(self):
        expected = [sum(s) / len(s) for s in EXAMPLES]
        actual = [v.mean() for v in self.variances]
        self.assertEqual(expected, actual)

    def test_stdev(self):
        expected = [round(statistics.stdev(s), 15) for s in EXAMPLES]
        actual = [round(v.stdev(), 15) for v in self.variances]
        self.assertEqual(expected, actual)

    def test_stdevp(self):
        expected = [round(statistics.pstdev(s), 15) for s in EXAMPLES]
        actual = [round(v.stdevp(), 15) for v in self.variances]
        self.assertEqual(expected, actual)

    def test_variance(self):
        expected = [round(statistics.variance(s), 15) for s in EXAMPLES]
        actual = [round(v.variance(), 15) for v in self.variances]
        self.assertEqual(expected, actual)
