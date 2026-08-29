from mdpr.retail.sample_data import generate

def test_generator_is_deterministic(tmp_path):
    a=generate(tmp_path/"a"); b=generate(tmp_path/"b")
    for name in ["customers.csv","products.csv","orders.jsonl"]:
        assert (a/name).read_bytes() == (b/name).read_bytes()
    assert "bad-json" in (a/"orders.jsonl").read_text()
