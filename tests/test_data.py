from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]

def load(name):
    df = pd.read_csv(ROOT / "data" / name, parse_dates=["date"])
    return df

def test_dates_are_unique_and_sorted():
    for name in ["inflation.csv", "confidence.csv", "gst.csv", "passenger_vehicles.csv"]:
        df = load(name)
        assert df.date.is_unique
        assert df.date.is_monotonic_increasing

def test_ranges_and_cutoff():
    assert load("inflation.csv").cpi_inflation_yoy.between(-10, 20).all()
    confidence = load("confidence.csv")
    assert confidence.csi.between(0, 200).all()
    assert confidence.fei.between(0, 200).all()
    assert load("gst.csv").gross_gst_crore.gt(0).all()
    pv = load("passenger_vehicles.csv")
    assert len(pv) == 23
    assert pv.domestic_sales_units.gt(0).all()
    assert max(d.date.max() for d in [load("inflation.csv"), load("confidence.csv"), load("gst.csv"), pv]) < pd.Timestamp("2026-08-01")
