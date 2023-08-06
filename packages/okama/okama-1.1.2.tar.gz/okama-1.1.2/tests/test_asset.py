from pandas._testing import assert_series_equal
from pytest import mark
from pytest import approx
import pandas as pd

from .conftest import data_folder


@mark.asset
@mark.smoke
def test_get_symbol_data(init_asset_spy):
    assert init_asset_spy.name == "SPDR S&P 500 ETF Trust"
    assert init_asset_spy.country == "USA"
    assert init_asset_spy.currency == "USD"
    assert init_asset_spy.type == "ETF"
    assert init_asset_spy.inflation == "USD.INFL"
    assert init_asset_spy.first_date == pd.to_datetime("1993-02")
    assert init_asset_spy.isin == "US78462F1030"


def test_usdrub(init_asset_usdrub):
    close_daily_sample = pd.read_pickle(data_folder / "usdrub_close_daily.pkl")
    close_monthly_sample = pd.read_pickle(data_folder / "usdrub_close_monthly.pkl")
    adj_close_sample = pd.read_pickle(data_folder / "usdrub_adj_close.pkl")
    assert_series_equal(init_asset_usdrub.close_daily['2019-01': '2020-01'], close_daily_sample)
    assert_series_equal(init_asset_usdrub.close_monthly['2019-01': '2020-01'], close_monthly_sample)
    assert_series_equal(init_asset_usdrub.adj_close['2019-01': '2020-01'], adj_close_sample)


def test_close_daily(init_asset_spy, init_asset_usdrub):
    assert init_asset_spy.close_daily.loc['2000-01-20'] == 144.75


def test_close_monthly(init_asset_spy):
    assert init_asset_spy.close_monthly.loc['2000-01'] == 139.5625


def test_adj_close(init_asset_spy):
    assert init_asset_spy.adj_close.loc['2000-01-20'] == approx(97.0629, rel=1e-2)


def test_price(init_asset_spy):
    assert type(init_asset_spy.price) == float


def test_dividends(init_asset_spy):
    assert init_asset_spy.dividends["2019"].iloc[-1] == 1.57


def test_nav_ts(init_asset_pif):
    assert init_asset_pif.nav_ts[0] == 101820352.18
