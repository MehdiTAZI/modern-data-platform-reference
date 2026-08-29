from mdpr.retail.contracts import expectation_map, load_contract

def test_contract_loads():
    c=load_contract("contracts/retail/orders.yml")
    assert c.dataset == "orders" and c.keys == ("event_id",)
    assert "event_id_not_null" in expectation_map(c, "fail")
