import numpy as np
import pytest

from portfolio_optimization.exceptions import DomainValidationError
from portfolio_optimization.optimization.sga import SGAConfig, run_sga


MEAN_RETURNS = np.array([0.010, 0.012, 0.008, 0.011])
COVARIANCE = np.array(
    [
        [0.040, 0.010, 0.008, 0.009],
        [0.010, 0.050, 0.007, 0.011],
        [0.008, 0.007, 0.030, 0.006],
        [0.009, 0.011, 0.006, 0.045],
    ]
)


def test_sga_is_reproducible_and_respects_weight_constraints() -> None:
    config = SGAConfig(
        population_size=30,
        generations=20,
        max_weight=0.4,
        seed=29,
    )

    first = run_sga(MEAN_RETURNS, COVARIANCE, config)
    second = run_sga(MEAN_RETURNS, COVARIANCE, config)

    np.testing.assert_allclose(first.weights, second.weights)
    assert first.weights.sum() == pytest.approx(1.0)
    assert np.all(first.weights >= 0.0)
    assert np.all(first.weights <= 0.4 + 1e-9)
    assert np.isfinite(first.best_fitness)
    assert np.isfinite(first.sharpe_ratio)
    assert len(first.history_best) == 20


def test_sga_rejects_infeasible_maximum_weight() -> None:
    config = SGAConfig(max_weight=0.2)

    with pytest.raises(
        DomainValidationError,
        match="max_weight is infeasible",
    ):
        run_sga(MEAN_RETURNS, COVARIANCE, config)
