import logging
import sys
from typing import Iterable

from flask import Blueprint

LOGGER = logging.getLogger(__name__)


class APIBlueprint(Blueprint):
    """Extended blueprint that exposes more convenient methods to develop APIs
    
    Arguments:
        tags: List of openapi tags that apply to all views registered in this blueprint
    """

    def __init__(self, tags: Iterable[str] = None):
        super().__init__(
            self.get_caller_module_name().replace(".", "-"),
            self.get_caller_module_name(),
        )
        self.tags = set() if tags is None else set(tags)

    @classmethod
    def get_caller_module_name(cls):
        caller = sys._getframe(1)  # Obtain calling frame
        return caller.f_globals["__name__"]

    def get(self, rule: str, **options):
        options["methods"] = ("GET",)
        return self.route(rule, **options)

    def put(self, rule: str, **options):
        options["methods"] = ("PUT",)
        return self.route(rule, **options)

    def post(self, rule: str, **options):
        options["methods"] = ("POST",)
        return self.route(rule, **options)

    def delete(self, rule: str, **options):
        options["methods"] = ("DELETE",)
        return self.route(rule, **options)
