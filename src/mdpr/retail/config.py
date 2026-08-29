from dataclasses import dataclass

ENV_PREFIX = {"dev": "dev", "staging": "stg", "prod": "prd"}

@dataclass(frozen=True)
class RetailConfig:
    environment: str
    catalog: str
    landing_volume: str = "landing"

    @classmethod
    def for_environment(cls, environment: str) -> "RetailConfig":
        env = environment.lower()
        if env not in ENV_PREFIX:
            raise ValueError(f"Unsupported environment: {environment}")
        return cls(environment=env, catalog=f"retail_{ENV_PREFIX[env]}")

    def table(self, layer: str, name: str) -> str:
        if layer not in {"bronze", "silver", "gold", "ops"}:
            raise ValueError(f"Unsupported layer: {layer}")
        return f"{self.catalog}.{layer}.{name}"
