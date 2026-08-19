from portfolio_optimization.domain import PortfolioBrief, RiskProfile
from portfolio_optimization.repositories.postgres_briefs import (
    PostgresPortfolioBriefRepository,
)


_STUB_SUMMARIES = {
    RiskProfile.CONSERVATIVE: (
        "AI stub: prioritize capital preservation with 70% bonds, "
        "20% broad-market equity, and 10% cash."
    ),
    RiskProfile.BALANCED: (
        "AI stub: balance growth and stability with 50% broad-market equity, "
        "40% bonds, and 10% cash."
    ),
    RiskProfile.GROWTH: (
        "AI stub: prioritize long-term growth with 80% broad-market equity, "
        "15% bonds, and 5% cash."
    ),
}


class PortfolioBriefService:
    def __init__(self, repository: PostgresPortfolioBriefRepository) -> None:
        self._repository = repository

    def create(self, *, name: str, risk_profile: RiskProfile) -> PortfolioBrief:
        brief = PortfolioBrief(
            name=name,
            risk_profile=risk_profile,
            ai_summary=_STUB_SUMMARIES[risk_profile],
        )
        return self._repository.create(brief)

    def list_all(self) -> tuple[PortfolioBrief, ...]:
        return self._repository.list_all()

