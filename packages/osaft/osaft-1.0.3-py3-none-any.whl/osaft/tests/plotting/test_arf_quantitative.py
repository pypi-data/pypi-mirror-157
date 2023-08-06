import unittest

import numpy as np

from osaft import ARFPlot
from osaft.solutions.base_arf import BaseARF


class DummyClass(BaseARF):
    """Dummy class to test methods
    """
    name = 'Dummy'
    R_0 = 1

    def compute_arf(self):
        return 2 * self.R_0


class TestARFNormalization(unittest.TestCase):

    def setUp(self) -> None:

        self.cls = DummyClass()
        self.R_values = np.arange(1, 10)

        self.arf_plot = ARFPlot('R_0', self.R_values)
        self.arf_plot.add_solutions(self.cls)

    def test_display_values(self):

        x_values = np.linspace(0, 1, len(self.R_values))
        _, ax = self.arf_plot.plot_solutions(display_values=x_values)
        abscissa = ax.lines[0].get_xdata()
        np.testing.assert_array_equal(x_values, abscissa)

    def test_max_norm(self) -> None:

        _, ax = self.arf_plot.plot_solutions(normalization='max')
        arf = ax.lines[0].get_ydata()
        self.assertAlmostEqual(max(arf), 1)
        self.assertTrue(np.all(arf <= 1))

    def test_other_class_norm(self):
        norm = 'Dummy'
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        self.assertAlmostEqual(max(arf), 1)

    def test_float_norm(self) -> None:

        norm = 5
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(2 * self.R_values / 5, arf)

    def test_array_norm(self) -> None:

        norm = np.arange(1, 10)
        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(2 * np.ones(len(norm)), arf)

    def test_callable_norm(self) -> None:
        def norm(R_0):
            return 2 * R_0

        _, ax = self.arf_plot.plot_solutions(normalization=norm)
        arf = ax.lines[0].get_ydata()
        np.testing.assert_array_equal(np.ones(len(self.R_values)), arf)

    def test_wrong_norm(self):
        self.assertRaises(
            ValueError, self.arf_plot.plot_solutions,
            normalization='blabla',
        )


if __name__ == '__main__':
    unittest.main()
