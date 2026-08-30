from mdpr.retail.sample_data import generate


def test_generator_is_deterministic(tmp_path):
    first = generate(tmp_path / "first")
    second = generate(tmp_path / "second")
    for name in [
        "customers.csv",
        "products.csv",
        "orders.jsonl",
        "recovery/customers-reference-catchup.csv",
    ]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert "bad-json" in (first / "orders.jsonl").read_text()
    assert "C999" in (first / "recovery/customers-reference-catchup.csv").read_text()
