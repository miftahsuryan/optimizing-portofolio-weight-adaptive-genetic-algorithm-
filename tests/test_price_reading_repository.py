from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from portfolio_optimization.domain import PriceReading
from portfolio_optimization.exceptions import DuplicateEntityError
from portfolio_optimization.repositories.in_memory import (
    InMemoryPriceReadingRepository,
)


OBSERVED_AT = datetime(2026, 8, 17, 9, 0, tzinfo=UTC)


def make_reading(
    *,
    asset_id: UUID | None = None,
    observed_at: datetime = OBSERVED_AT,
    close: str = "8500.50",
) -> PriceReading:
    return PriceReading(
        asset_id=asset_id or uuid4(),
        observed_at=observed_at,
        close=Decimal(close),
    )


def test_create_stores_and_returns_reading() -> None:
    repository = InMemoryPriceReadingRepository()
    reading = make_reading()

    result = repository.create(reading)

    assert result == reading
    assert repository.get(reading.id) == reading


def test_get_returns_none_for_unknown_id() -> None:
    repository = InMemoryPriceReadingRepository()

    result = repository.get(uuid4())

    assert result is None


def test_create_rejects_duplicate_id() -> None:
    repository = InMemoryPriceReadingRepository()
    existing = repository.create(make_reading())
    duplicate = PriceReading(
        id=existing.id,
        asset_id=uuid4(),
        observed_at=OBSERVED_AT,
        close=Decimal("100"),
    )

    with pytest.raises(
        DuplicateEntityError,
        match=f"PriceReading ID already exists: {existing.id}",
    ):
        repository.create(duplicate)


def test_create_rejects_duplicate_asset_and_observation_time() -> None:
    repository = InMemoryPriceReadingRepository()
    asset_id = uuid4()
    repository.create(make_reading(asset_id=asset_id))

    with pytest.raises(
        DuplicateEntityError,
        match="PriceReading already exists for Asset",
    ):
        repository.create(
            make_reading(
                asset_id=asset_id,
                observed_at=OBSERVED_AT,
                close="8600",
            )
        )


def test_same_observation_time_is_allowed_for_different_assets() -> None:
    repository = InMemoryPriceReadingRepository()
    first = repository.create(
        make_reading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
        )
    )
    second = repository.create(
        make_reading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
        )
    )

    assert repository.get(first.id) == first
    assert repository.get(second.id) == second


def test_list_for_asset_returns_chronological_readings() -> None:
    repository = InMemoryPriceReadingRepository()
    asset_id = uuid4()
    later = repository.create(
        make_reading(
            asset_id=asset_id,
            observed_at=OBSERVED_AT + timedelta(days=1),
            close="8600",
        )
    )
    earlier = repository.create(
        make_reading(
            asset_id=asset_id,
            observed_at=OBSERVED_AT,
            close="8500",
        )
    )
    repository.create(
        make_reading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
        )
    )

    result = repository.list_for_asset(asset_id)

    assert result == (earlier, later)


def test_list_for_asset_returns_empty_tuple() -> None:
    repository = InMemoryPriceReadingRepository()

    result = repository.list_for_asset(uuid4())

    assert result == ()


def test_delete_removes_existing_reading() -> None:
    repository = InMemoryPriceReadingRepository()
    reading = repository.create(make_reading())

    result = repository.delete(reading.id)

    assert result is True
    assert repository.get(reading.id) is None


def test_delete_returns_false_for_unknown_reading() -> None:
    repository = InMemoryPriceReadingRepository()

    result = repository.delete(uuid4())

    assert result is False


def test_create_many_stores_entire_batch() -> None:
    repository = InMemoryPriceReadingRepository()
    asset_id = uuid4()
    readings = (
        make_reading(
            asset_id=asset_id,
            observed_at=OBSERVED_AT,
        ),
        make_reading(
            asset_id=asset_id,
            observed_at=OBSERVED_AT + timedelta(days=1),
        ),
    )

    result = repository.create_many(readings)

    assert result == readings
    assert repository.list_for_asset(asset_id) == readings


def test_create_many_is_atomic_when_one_reading_conflicts() -> None:
    repository = InMemoryPriceReadingRepository()
    asset_id = uuid4()
    existing = repository.create(
        make_reading(
            asset_id=asset_id,
            observed_at=OBSERVED_AT,
        )
    )
    valid_new_reading = make_reading(
        asset_id=asset_id,
        observed_at=OBSERVED_AT + timedelta(days=1),
    )
    conflicting_reading = make_reading(
        asset_id=asset_id,
        observed_at=OBSERVED_AT,
        close="9000",
    )

    with pytest.raises(DuplicateEntityError):
        repository.create_many(
            (valid_new_reading, conflicting_reading)
        )

    assert repository.list_for_asset(asset_id) == (existing,)
    assert repository.get(valid_new_reading.id) is None


def test_create_many_rejects_duplicates_inside_batch_atomically() -> None:
    repository = InMemoryPriceReadingRepository()
    asset_id = uuid4()
    first = make_reading(
        asset_id=asset_id,
        observed_at=OBSERVED_AT,
    )
    duplicate = make_reading(
        asset_id=asset_id,
        observed_at=OBSERVED_AT,
        close="9000",
    )

    with pytest.raises(DuplicateEntityError):
        repository.create_many((first, duplicate))

    assert repository.list_for_asset(asset_id) == ()