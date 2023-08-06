"""Tesseract Module for LogicLayer

This module contains an implementation of the :class:`LogicLayerModule` class,
for use with a :class:`LogicLayer` instance.
"""

from pathlib import Path
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from logiclayer import LogicLayerModule

from tesseract_olap.backend.exceptions import BackendError
from tesseract_olap.query import DataRequest, MembersRequest
from tesseract_olap.query.exceptions import QueryError
from tesseract_olap.server import OlapServer

from .dependencies import dataquery_params, membersquery_params


class TesseractModule(LogicLayerModule):
    """Tesseract OLAP server module for LogicLayer.

    It must be initialized with a :class:`logiclayer.OlapServer` instance, but
    can also be created directly with the schema path and the connection string
    using the helper method `TesseractModule.new(connection, schema)`.
    """

    server: OlapServer

    def __init__(self,
                 server: OlapServer,
                 *,
                 debug: Optional[bool] = False):
        self.server = server
        self._debug = debug

    @classmethod
    def new(cls, connection: str, schema: Union[str, Path]):
        """Creates a new :class:`TesseractModule` instance from the strings with
        the path to the schema file (or the schema content itself), and with the
        connection string to the backend.
        """
        server = OlapServer(connection, schema)
        return cls(server)

    def healthcheck(self):
        return self.server.ping()

    def setup(self, router: APIRouter):
        _setup_routes(self.server, router)
        return self.server.connect()

    def terminate(self):
        return self.server.disconnect()


def _setup_routes(server: OlapServer, router: APIRouter):
    """Setups the OLAP server routes."""

    @router.get("/")
    async def route_root():
        """Pings the backend configured in the tesseract server."""
        beat = await server.ping()
        return {
            "status": "ok" if beat else "error",
        }

    @router.get("/cubes")
    def route_publicschema_full(locale: Optional[str] = None):
        return server.schema.get_public_schema(locale=locale)

    @router.get("/cubes/{cube_name}")
    def route_publicschema_single(cube_name: str, locale: Optional[str] = None):
        locale = server.schema.default_locale if locale is None else locale
        cube = server.schema[cube_name]
        return cube.get_public_schema(locale=locale)

    @router.get("/data")
    def route_data(request: Request):
        return RedirectResponse(f"{request.url.path}.jsonrecords?{request.url.query}")

    @router.get("/data.{filetype}")
    async def route_data_format(
        filetype: str = "jsonrecords",
        query: DataRequest = Depends(dataquery_params),
    ):
        try:
            result = await server.get_data(query)
        except QueryError as exc:
            raise HTTPException(status_code=403, detail=exc.message) from None
        except BackendError as exc:
            raise HTTPException(status_code=500, detail=exc.message) from None
        return {
            "data": result.data,
            "format": filetype,
            "sources": result.sources,
        }

    @router.get("/members")
    def route_members(request: Request):
        return RedirectResponse(f"{request.url.path}.jsonrecords?{request.url.query}")

    @router.get("/members.{filetype}")
    async def route_members_format(
        filetype: str = "jsonrecords",
        query: MembersRequest = Depends(membersquery_params),
    ):
        try:
            result = await server.get_members(query)
        except QueryError as exc:
            raise HTTPException(status_code=403, detail=exc.message) from None
        except BackendError as exc:
            raise HTTPException(status_code=500, detail=exc.message) from None
        return {
            "format": filetype,
            "data": result.data,
        }
