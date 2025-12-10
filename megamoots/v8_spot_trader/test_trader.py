from megamoots.v8_spot_trader.trader import choose_market

def test_choose():
    s = [{"cloud":"a","price":5},{"cloud":"b","price":3}]
    assert choose_market(s)["cloud"] == "b"
