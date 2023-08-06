import pandas as pd

from archimedes.data.api import _make_api_request, get_api_base_url_v2


def rk_within_day_directions(
    start: str,
    end: str,
    price_area: str,
    ref_dt: str = None,
    *,
    access_token: str = None,
):
    """
    Method to get directions for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        access_token: Access token
    """
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/directions",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_distributions(
    start: str,
    end: str,
    price_area: str,
    ref_dt: str = None,
    *,
    access_token: str = None,
):
    """
    Method to get distributions for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        access_token: Access token
    """
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/distributions",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_large_up_fps(
    start: str,
    end: str,
    price_area: str,
    ref_dt: str = None,
    conditional: bool = False,
    *,
    access_token: str = None,
):
    """
    Method to get large up for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        conditional: If set to False, ignores the direction of RK
        access_token: Access token
    """
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "conditional": conditional,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/large_up_fps",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_large_down_fps(
    start: str,
    end: str,
    price_area: str,
    ref_dt: str = None,
    conditional: bool = False,
    *,
    access_token: str = None,
):
    """
    Method to get large down for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        conditional: If set to False, ignores the direction of RK
        access_token: Access token
    """
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "conditional": conditional,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/large_down_fps",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_comparison_by_price(
    start: str,
    price_area: str,
    ref_price: int,
    *,
    access_token: str = None,
):
    """
    Method to get probability for rk within day in comparison to provided price
    Parameters:
        start: Start timestamp
        price_area: Price area
        ref_price: Reference price to compare against
        access_token: Access token
    """
    query = {
        "start_time": start,
        "price_area": price_area,
        "ref_price": ref_price,
    }
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/price_comparison/by_price",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_comparison_by_probability(
    start: str,
    price_area: str,
    ref_probability: int,
    *,
    access_token: str = None,
):
    """
    Method to get probability for rk within day in comparison to provided price
    Parameters:
        start: Start timestamp
        price_area: Price area
        ref_probability: Reference probability to compare against
        access_token: Access token
    """
    query = {
        "start_time": start,
        "price_area": price_area,
        "ref_probability": ref_probability,
    }
    data = _make_api_request(
        f"{get_api_base_url_v2()}/rk_within_day/price_comparison/by_probability",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)
