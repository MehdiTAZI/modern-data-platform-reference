from dataclasses import dataclass


@dataclass(frozen=True)
class RetailConfig:
    environment: str
    bronze_catalog: str
    silver_catalog: str
    gold_catalog: str
    schema: str = "retail"

    @classmethod
    def for_environment(cls, environment: str) -> "RetailConfig":
        env = environment.lower()
        if env not in {"dev", "staging", "prod"}:
            raise ValueError(f"Unsupported environment: {environment}")
        prefix = "stg" if env == "staging" else ("prd" if env == "prod" else "dev")
        return cls(
            environment=env,
            bronze_catalog=f"{prefix}_bronze",
            silver_catalog=f"{prefix}_silver",
            gold_catalog=f"{prefix}_gold",
        )
