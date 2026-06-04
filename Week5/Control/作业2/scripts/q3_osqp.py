"""Solve the robot-dog constrained optimization problem with OSQP."""

from __future__ import annotations

import numpy as np
import osqp
from scipy import sparse


def objective(x: np.ndarray) -> float:
    dx = x[0] - 3.0
    dy = x[1] - 3.0
    return 0.5 * dx * dx + 5.0 * dy * dy


def main() -> None:
    # f(x, y) = 0.5 * x^2 + 5 * y^2 - 3 * x - 30 * y + constant
    p = sparse.csc_matrix([[1.0, 0.0], [0.0, 10.0]])
    q = np.array([-3.0, -30.0])

    # x + y <= 4, written as l <= A x <= u.
    a = sparse.csc_matrix([[1.0, 1.0]])
    l = np.array([-np.inf])
    u = np.array([4.0])

    solver = osqp.OSQP()
    solver.setup(P=p, q=q, A=a, l=l, u=u, eps_abs=1e-10, eps_rel=1e-10, verbose=False)
    result = solver.solve()

    if "solved" not in result.info.status.lower():
        raise RuntimeError(f"OSQP failed with status: {result.info.status}")

    x = result.x
    expected = np.array([13.0 / 11.0, 31.0 / 11.0])

    print("Q3 OSQP result")
    print(f"status: {result.info.status}")
    print(f"x*: [{x[0]:.10f}, {x[1]:.10f}]")
    print(f"objective f(x*): {objective(x):.10f}")
    print(f"x + y - 4: {x.sum() - 4.0:.3e}")
    print(f"KKT reference: [{expected[0]:.10f}, {expected[1]:.10f}]")
    print(f"difference: {np.linalg.norm(x - expected):.3e}")


if __name__ == "__main__":
    main()
