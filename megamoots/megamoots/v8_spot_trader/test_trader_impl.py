from megamoots.v8_spot_trader.trader_impl import choose_market
def test_spot_choose():
    offers = [{"cloud":"a","price":3,"reliability":0.9},{"cloud":"b","price":2.8,"reliability":0.5}]
    assert choose_market(offers)["cloud"] in ("a","b")
