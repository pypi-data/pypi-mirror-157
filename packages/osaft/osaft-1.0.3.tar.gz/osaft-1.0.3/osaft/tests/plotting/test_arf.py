import inspect
import unittest

import numpy as np
from matplotlib import pyplot as plt

from osaft import ARFPlot, WaveType, gorkov1962, king1934, yosioka1955
from osaft.solutions.base_arf import BaseARF
from osaft.tests.basetest_plotting import BaseTestPlotting


class TestARFPlot(BaseTestPlotting):

    def setUp(self) -> None:
        super().setUp()

        self.plotter = ARFPlot()

    def create_solutions(self) -> list[BaseARF]:
        f = 1e6
        R_0 = 1e-6
        rho_s = 1850
        c_s = 5000
        rho_f = 997
        c_f = 1500
        p_0 = 1e5
        wave_types = WaveType.TRAVELLING
        position = None

        out = []
        out.append(
            king1934.ARF(
                f, R_0,
                rho_s,
                rho_f, c_f,
                p_0, wave_types, position,
            ),
        )

        out.append(
            yosioka1955.ARF(
                f, R_0,
                rho_s, c_s,
                rho_f, c_f,
                p_0, wave_types, position,
            ),
        )

        out.append(
            gorkov1962.ARF(
                f, R_0,
                rho_s, c_s,
                rho_f, c_f,
                p_0, wave_types, position,
            ),
        )

        return out

    def test_name_error(self) -> None:
        solutions = self.create_solutions()
        for sol in solutions:
            self.plotter.add_solutions(sol)
            self.assertRaises(ValueError, self.plotter.add_solutions, sol)

    def test_error_add_zero_solutions(self) -> None:
        self.assertRaises(TypeError, self.plotter.add_solutions)

    def test_add_multiple_solutions(self):
        solutions = self.create_solutions()
        self.plotter.add_solutions(*solutions)

        # Test if solutions are inside
        for sol in solutions:
            self.assertTrue(sol.name in self.plotter._solutions.keys())

    def test_modulo_in_linestyles(self) -> None:
        solutions = self.create_solutions()
        for i in np.arange(6):
            for sol in solutions:
                tmp = sol
                tmp.name = f'{tmp.name}_{i}'
                self.plotter.add_solutions(tmp)

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5), 'R_0')

        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_add_and_remove_solutions(self) -> None:
        solutions = self.create_solutions()
        for sol in solutions:
            self.plotter.add_solutions(sol)
        self.plotter.remove_solution(solutions[1])

    def test_repeated_ARF_over_R(self) -> None:
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5), 'R_0')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions()
        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_ARF_over_R(self) -> None:
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e-6, 1e-5, num=100), 'R_0')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions()

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f(self) -> None:
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f_semilogx(self) -> None:
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
            plot_method=plt.semilogx,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_normARF_over_f_loglog(self) -> None:
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization=solutions[1].name,
            plot_method=plt.loglog,
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)

    def test_max_norm_over_f(self):
        solutions = self.create_solutions()

        self.plotter.set_abscissa(np.linspace(1e4, 5e6, num=100), 'f')

        for sol in solutions:
            self.plotter.add_solutions(sol)

        fig, ax = self.plotter.plot_solutions(
            normalization='max',
        )

        name = inspect.stack()[0][3]  # method name
        self.save_fig(fig, name)


if __name__ == '__main__':
    unittest.main()
