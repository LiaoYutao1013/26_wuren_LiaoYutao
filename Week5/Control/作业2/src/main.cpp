#include <Eigen/Dense>

#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

namespace {

constexpr double kTolerance = 1e-3;
constexpr int kMaxIterations = 100000;

Eigen::Vector2d Target() {
  return Eigen::Vector2d{3.0, 3.0};
}

double Objective(const Eigen::Vector2d& x) {
  const double dx = x(0) - 3.0;
  const double dy = x(1) - 3.0;
  return 0.5 * dx * dx + 5.0 * dy * dy;
}

Eigen::Vector2d Gradient(const Eigen::Vector2d& x) {
  return Eigen::Vector2d{x(0) - 3.0, 10.0 * (x(1) - 3.0)};
}

struct GradientResult {
  double eta = 0.0;
  int iterations = 0;
  Eigen::Vector2d x = Eigen::Vector2d::Zero();
  double error = 0.0;
  bool converged = false;
};

GradientResult RunGradientDescent(double eta) {
  Eigen::Vector2d x{0.0, 0.0};

  for (int iteration = 1; iteration <= kMaxIterations; ++iteration) {
    x = x - eta * Gradient(x);
    const double error = (x - Target()).norm();
    if (error < kTolerance) {
      return GradientResult{eta, iteration, x, error, true};
    }
  }

  return GradientResult{eta, kMaxIterations, x, (x - Target()).norm(), false};
}

void PrintQ1() {
  std::cout << "Q1: unconstrained gradient descent\n";
  std::cout << "gradient = [x - 3, 10 * (y - 3)]^T\n";
  std::cout << "stop when ||X - [3, 3]^T|| < " << kTolerance << "\n\n";

  const std::vector<double> learning_rates{
      0.01, 0.05, 0.09, 0.10, 0.15, 0.18, 2.0 / 11.0, 0.19, 0.20};

  std::cout << std::fixed << std::setprecision(6);
  std::cout << "eta        iterations  x          y          error       status\n";

  for (const double eta : learning_rates) {
    const GradientResult result = RunGradientDescent(eta);
    std::cout << std::setw(10) << result.eta << "  " << std::setw(10)
              << result.iterations << "  " << std::setw(9) << result.x(0)
              << "  " << std::setw(9) << result.x(1) << "  " << std::scientific
              << std::setw(10) << result.error << std::fixed << "  "
              << (result.converged ? "converged" : "not converged") << "\n";
  }

  std::cout << "\n";
}

void PrintQ2() {
  const double mu = 20.0 / 11.0;
  const Eigen::Vector2d solution{13.0 / 11.0, 31.0 / 11.0};

  std::cout << "Q2: KKT solution for x + y <= 4\n";
  std::cout << "unconstrained minimizer [3, 3]^T is infeasible, so x + y = 4 is active.\n";
  std::cout << "mu = " << mu << "\n";
  std::cout << "x* = [" << solution(0) << ", " << solution(1) << "]^T\n";
  std::cout << "constraint residual x + y - 4 = " << solution.sum() - 4.0 << "\n";
  std::cout << "objective f(x*) = " << Objective(solution) << "\n\n";
}

void PrintQ3() {
  Eigen::Matrix2d p = Eigen::Matrix2d::Zero();
  p(0, 0) = 1.0;
  p(1, 1) = 10.0;

  const Eigen::Vector2d q{-3.0, -30.0};
  const Eigen::RowVector2d a{1.0, 1.0};
  const double lower_bound = -std::numeric_limits<double>::infinity();
  const double upper_bound = 4.0;

  std::cout << "Q3: OSQP standard form\n";
  std::cout << "min 0.5 * X^T P X + q^T X, subject to l <= A X <= u\n\n";
  std::cout << "P =\n" << p << "\n\n";
  std::cout << "q = [" << q.transpose() << "]^T\n";
  std::cout << "A = [" << a << "]\n";
  std::cout << "l = [" << lower_bound << "]\n";
  std::cout << "u = [" << upper_bound << "]\n\n";

  Eigen::Matrix3d kkt = Eigen::Matrix3d::Zero();
  kkt.block<2, 2>(0, 0) = p;
  kkt.block<2, 1>(0, 2) = a.transpose();
  kkt.block<1, 2>(2, 0) = a;

  Eigen::Vector3d rhs;
  rhs << -q, upper_bound;

  const Eigen::Vector3d active_solution = kkt.colPivHouseholderQr().solve(rhs);
  std::cout << "active-constraint KKT check [x, y, mu] = ["
            << active_solution.transpose() << "]\n";
  std::cout << "Run scripts/q3_osqp.py to solve the same QP with OSQP.\n";
}

}  // namespace

int main() {
  PrintQ1();
  PrintQ2();
  PrintQ3();
  return 0;
}
