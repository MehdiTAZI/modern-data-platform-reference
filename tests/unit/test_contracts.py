from mdpr.retail.contracts import expectation_map, load_contract


def test_contract_loads():
    contract = load_contract("contracts/retail/orders.yml")
    assert contract.dataset == "orders" and contract.keys == ("event_id",)
    assert "event_id_not_null" in expectation_map(contract, "fail")
