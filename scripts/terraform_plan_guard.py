import argparse
from pathlib import Path

from mdpr.terraform_plan_guard import evaluate_plan, load_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail when a Terraform JSON plan contains unapproved delete/replace actions."
    )
    parser.add_argument("plan_json", type=Path, help="Path produced by `terraform show -json PLAN`")
    parser.add_argument(
        "--allow-address",
        action="append",
        default=[],
        metavar="GLOB",
        help="Explicit resource-address glob allowed to be deleted/replaced; repeatable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        plan = load_plan(args.plan_json)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    violations = evaluate_plan(plan, args.allow_address)
    if violations:
        details = "\n".join(f"- {violation}" for violation in violations)
        message = (
            "Blocked destructive Terraform plan. Review the plan and explicitly allow only "
            f"expected resource addresses:\n{details}"
        )
        raise SystemExit(message)

    print("OK: Terraform plan contains no unapproved destructive changes")


if __name__ == "__main__":
    main()
