from dataclasses import dataclass

import numpy as np

from portfolio_optimization.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class SGAConfig:
    population_size: int = 100
    generations: int = 100
    max_weight: float = 0.3
    diversification_penalty: float = 0.1
    crossover_rate: float = 0.9
    mutation_rate: float = 0.1
    mutation_scale: float = 0.05
    tournament_size: int = 3
    seed: int = 29


@dataclass(frozen=True, slots=True)
class SGAResult:
    weights: np.ndarray
    best_fitness: float
    expected_return: float
    volatility: float
    sharpe_ratio: float
    convergence_generation: int
    history_best: tuple[float, ...]
    history_average: tuple[float, ...]
    history_diversity: tuple[float, ...]


def portfolio_fitness(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    *,
    diversification_penalty: float,
    max_weight: float,
) -> float:
    expected_return = float(weights @ mean_returns)
    variance = float(weights.T @ covariance @ weights)
    volatility = float(np.sqrt(max(variance, 0.0) + 1e-6))
    sharpe_ratio = expected_return / volatility
    diversification = float(np.sum(weights**2))
    violations = np.maximum(0.0, weights - max_weight)
    maximum_weight_penalty = 1000.0 * float(np.sum(violations**2))
    return (
        -sharpe_ratio
        + diversification_penalty * diversification
        + maximum_weight_penalty
    )


def repair_weights(
    weights: np.ndarray,
    *,
    max_weight: float,
    rng: np.random.Generator,
) -> np.ndarray:
    repaired = np.clip(np.asarray(weights, dtype=float), 0.0, max_weight)
    if float(repaired.sum()) == 0.0:
        repaired = rng.random(len(repaired))
    repaired /= repaired.sum()

    for _ in range(100):
        over = repaired > max_weight + 1e-12
        if not np.any(over):
            break
        excess = float(np.sum(repaired[over] - max_weight))
        repaired[over] = max_weight
        under = repaired < max_weight - 1e-12
        capacity = max_weight - repaired[under]
        capacity_total = float(capacity.sum())
        if capacity_total <= 0.0:
            break
        repaired[under] += excess * capacity / capacity_total

    repaired /= repaired.sum()
    if np.any(repaired > max_weight + 1e-9):
        raise DomainValidationError("Unable to satisfy max_weight constraint")
    return repaired


def run_sga(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    config: SGAConfig = SGAConfig(),
) -> SGAResult:
    mean_returns = np.asarray(mean_returns, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    asset_count = len(mean_returns)
    if asset_count < 2:
        raise DomainValidationError("At least two Assets are required")
    if covariance.shape != (asset_count, asset_count):
        raise DomainValidationError("Invalid covariance matrix shape")
    if not np.all(np.isfinite(mean_returns)) or not np.all(np.isfinite(covariance)):
        raise DomainValidationError("Portfolio statistics must be finite")
    if config.population_size < config.tournament_size:
        raise DomainValidationError(
            "population_size must be at least tournament_size"
        )
    if config.generations < 1:
        raise DomainValidationError("generations must be positive")
    if config.tournament_size < 2:
        raise DomainValidationError("tournament_size must be at least two")
    if not 0.0 < config.max_weight <= 1.0:
        raise DomainValidationError("max_weight must be between zero and one")
    if not 0.0 <= config.crossover_rate <= 1.0:
        raise DomainValidationError(
            "crossover_rate must be between zero and one"
        )
    if not 0.0 <= config.mutation_rate <= 1.0:
        raise DomainValidationError(
            "mutation_rate must be between zero and one"
        )
    if config.mutation_scale <= 0.0:
        raise DomainValidationError("mutation_scale must be positive")
    if config.diversification_penalty < 0.0:
        raise DomainValidationError(
            "diversification_penalty must not be negative"
        )
    if asset_count * config.max_weight < 1.0 - 1e-12:
        raise DomainValidationError(
            "max_weight is infeasible for the number of Assets"
        )

    rng = np.random.default_rng(config.seed)
    population = np.array([
        repair_weights(rng.random(asset_count), max_weight=config.max_weight, rng=rng)
        for _ in range(config.population_size)
    ])
    best_weights = population[0].copy()
    best_fitness = float("inf")
    convergence_generation = 0
    history_best: list[float] = []
    history_average: list[float] = []
    history_diversity: list[float] = []

    for generation in range(config.generations):
        fitness = np.array([
            portfolio_fitness(
                individual,
                mean_returns,
                covariance,
                diversification_penalty=config.diversification_penalty,
                max_weight=config.max_weight,
            )
            for individual in population
        ])
        generation_best_index = int(np.argmin(fitness))
        generation_best = float(fitness[generation_best_index])
        if generation_best < best_fitness - 1e-6:
            best_fitness = generation_best
            best_weights = population[generation_best_index].copy()
            convergence_generation = generation
        history_best.append(generation_best)
        history_average.append(float(fitness.mean()))
        history_diversity.append(float(np.mean(np.std(population, axis=0))))

        children: list[np.ndarray] = []
        while len(children) < config.population_size:
            candidates1 = rng.choice(
                len(population), config.tournament_size, replace=False
            )
            candidates2 = rng.choice(
                len(population), config.tournament_size, replace=False
            )
            parent1 = population[candidates1[np.argmin(fitness[candidates1])]]
            parent2 = population[candidates2[np.argmin(fitness[candidates2])]]
            child = parent1.copy()
            if rng.random() <= config.crossover_rate:
                alpha = rng.random()
                child = alpha * parent1 + (1.0 - alpha) * parent2
            mutation_mask = rng.random(asset_count) < config.mutation_rate
            child[mutation_mask] += rng.normal(
                0.0, config.mutation_scale, int(mutation_mask.sum())
            )
            children.append(
                repair_weights(child, max_weight=config.max_weight, rng=rng)
            )
        population = np.array(children)

    expected_return = float(best_weights @ mean_returns)
    variance = float(best_weights.T @ covariance @ best_weights)
    volatility = float(np.sqrt(max(variance, 0.0)))
    sharpe_ratio = expected_return / volatility if volatility else 0.0
    return SGAResult(
        weights=best_weights,
        best_fitness=best_fitness,
        expected_return=expected_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        convergence_generation=convergence_generation,
        history_best=tuple(history_best),
        history_average=tuple(history_average),
        history_diversity=tuple(history_diversity),
    )
