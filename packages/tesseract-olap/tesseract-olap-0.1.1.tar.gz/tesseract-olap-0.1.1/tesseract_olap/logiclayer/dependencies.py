from typing import Dict, List, Optional, Tuple

from fastapi import Depends, Query, Request
from typing_extensions import Literal

from tesseract_olap.query import (DataRequest, DataRequestParams,
                                  MembersRequest, MembersRequestParams)


def query_cuts_include(request: Request):
    return {key: value.split(",")
            for key, value in request.query_params.items()
            if key[0].isupper()}


def query_cuts_exclude(exclude: str = ""):
    return {key: value.split(",")
            for key, value in (
                item.split(":")[:2]
                for item in exclude.split(";")
                if item != ""
            )}


def query_sorting(sort: Optional[str] = None):
    return None if sort is None else sort.split(".")[:2]


def query_pagination(limit: Optional[str] = None):
    """Parses pagination parameters.

    The shape of the parameters is:
        `[int]`       : Defines the max amount of items in the response data.
        `[int],[int]` : The first integer defines the max amount of items in the
                        response data; the second defines the index of the first
                        item in the full list where the list in the response
                        data will start.
    """
    return None if limit is None else tuple(int(i) for i in limit.split(",")[:2])


def dataquery_params(
    cube_name: str = Query(..., alias="cube"),
    drilldowns: str = Query(...),
    measures: str = Query(...),
    properties: Optional[str] = None,
    cuts_include: Dict[str, List[str]] = Depends(query_cuts_include),
    cuts_exclude: Dict[str, List[str]] = Depends(query_cuts_exclude),
    locale: Optional[str] = None,
    limit: Optional[Tuple[int, int]] = Depends(query_pagination),
    sorting: Optional[Tuple[str, Literal["asc", "desc"]]] = Depends(query_sorting),
    time: Optional[str] = None,
    parents: bool = False,
):
    params: DataRequestParams = {
        "drilldowns": [item.strip() for item in drilldowns.split(",")],
        "measures": [item.strip() for item in measures.split(",")],
        "parents": parents,
        "cuts_include": cuts_include,
        "cuts_exclude": cuts_exclude,
    }

    if locale is not None:
        params["locale"] = locale

    if properties is not None:
        params["properties"] = properties.split(",")

    if time is not None:
        params["time"] = time

    if limit is not None:
        params["pagination"] = limit

    if sorting is not None:
        params["sorting"] = sorting

    return DataRequest.new(cube_name, params)


def membersquery_params(
    cube_name: str = Query(..., alias="cube"),
    level: str = Query(...),
    locale: Optional[str] = None,
    search: str = "",
    limit: Optional[Tuple[int, int]] = Depends(query_pagination),
):
    params: MembersRequestParams = {
        "level": level,
    }

    if locale is not None:
        params["locale"] = locale

    if limit is not None:
        params["pagination"] = limit

    if search != "":
        params["search"] = search

    return MembersRequest.new(cube_name, params)
