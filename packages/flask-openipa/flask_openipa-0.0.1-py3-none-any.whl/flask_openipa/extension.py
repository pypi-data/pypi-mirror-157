import functools
import logging
import uuid
from typing import Any, Callable, Iterable, List, Tuple

import werkzeug.routing
from flask import Flask, jsonify

from flask_openipa import defaults
from flask_openipa.exceptions import MissingSettingException
from flask_openipa.openapi import (
    OpenAPIInfo,
    OpenAPIOperation,
    OpenAPIRequestBody,
    OpenAPISpec,
)
from flask_openipa.schemas.builder import OpenAPISchemaBuilder
from flask_openipa.schemas.plugins.base import BaseSchemaPlugin

LOGGER = logging.getLogger(__name__)


def operation_from_view(
    schema_builder: OpenAPISchemaBuilder,
    view_name: str,
    view_func: Callable,
    view_specs: dict,
):
    summary = view_specs.get("summary")
    if summary is None:
        summary = view_func.__name__.replace("_", " ").capitalize()

    try:
        description = view_specs.get("description")
        if description is None:
            description = view_func.__doc__.strip()
    except AttributeError:
        description = ""

    security_schemes = view_specs.get("security", None)
    if isinstance(security_schemes, str):
        security_schemes = (security_schemes,)

    security = None
    if security_schemes is not None:
        security = [{security_scheme: []} for security_scheme in security_schemes]

    # process request body
    reference_schema = None
    if view_specs.get("input_model"):
        reference_schema = schema_builder.add_schema(view_specs["input_model"])

    request_body = OpenAPIRequestBody(
        content_type=view_specs.get("input_type"), content_schema=reference_schema
    )

    return OpenAPIOperation(
        operation_id=view_name,
        summary=summary,
        description=description,
        tags=view_specs.get("tags", []),
        external_docs=view_specs.get("external_docs", None),
        request_body=request_body,
        security=security,
    )


class FlaskOpenIPA:
    """Flask extension used to generate openapi spec automatically.

    All arguments are optional at init and might be provided in init_app

    :param app: Flask application.
    :param openapi_url: If provided, url of the endpoint that will serve openapi spec.
    :param openapi_format: Can be one of 'json' or 'yaml'. (defaults to 'json')
    """

    operations = {}

    def __init__(self, app: Flask = None, plugins: Tuple[BaseSchemaPlugin, ...] = None):
        self.plugins = plugins

        if app is not None:
            self.init_app(app, plugins)

    def __get_setting(self, setting_name: str) -> Any:
        """Get extension setting from app config, or return its default value.
        
        :raises AttributeError: If no value exists
        """
        try:
            setting_value = self.app.config[setting_name]
            LOGGER.debug(
                "Setting %s retrieved from app config: %s", setting_name, setting_value
            )
            return setting_value
        except KeyError:
            # don't fail as a default value might existing in settings
            pass

        try:
            setting_value = getattr(defaults, setting_name)
            LOGGER.debug(
                "Setting %s retrieved from FlaskOpenIPA defaults: %s",
                setting_name,
                setting_value,
            )
            return setting_value
        except AttributeError as error:
            raise MissingSettingException(
                f"Your flask configuration is missing variable '{setting_name}' required by FlaskOpenIPA!"
            ) from error

    def init_app(self, app: Flask, plugins: Tuple[BaseSchemaPlugin, ...] = None):
        """Initialize extension settings out of initializer

        :param app: Flask application.
        :param openapi_url: If provided, url of the endpoint that will serve openapi spec.
        :param openapi_format: Can be one of 'json' or 'yaml'. (defaults to 'json')
        """
        if not isinstance(app, Flask):
            raise ValueError("Not a valid flask app")

        self.app = app

        if plugins:
            self.plugins = plugins

        self.schema_builder = OpenAPISchemaBuilder(plugins=self.plugins)
        self.schema_builder.on_new_schema(self._new_schema_handler)

        # required parameters
        self.api_title: str = self.__get_setting("API_TITLE")
        self.api_description: str = self.__get_setting("API_DESCRIPTION")
        self.api_version: str = self.__get_setting("API_VERSION")

        # parameters with default values
        self.openapi_url: str = self.__get_setting("API_SPEC_URL")
        self.openapi_format: str = self.__get_setting("API_SPEC_FORMAT")
        self.documented_methods: Iterable[str] = self.__get_setting(
            "API_SPEC_DOCUMENTED_METHODS"
        )
        self.security_schemes: dict = self.__get_setting("API_SECURITY_SCHEMES")
        self.openapi_tags: List[dict] = self.__get_setting("API_SPECS_TAGS")

        #
        self.reconfigure()

    def _new_schema_handler(self, name: str, schema: dict):
        self.openapi_spec.add_schema(name, schema)

    def expose_swagger_ui(self):
        from flask_swagger_ui import get_swaggerui_blueprint

        swaggerui_blueprint = get_swaggerui_blueprint("/docs", "/openapi.json")
        self.app.register_blueprint(swaggerui_blueprint)

    def reconfigure(self):
        """Apply actions depending of settings.
        
        Triggered only once app has been provided to the extension.
        """
        # setup swagger ui
        self.expose_swagger_ui()

        # initialize openapi spec from configuration
        self.openapi_spec = OpenAPISpec(
            info=OpenAPIInfo(
                title=self.api_title,
                description=self.api_description,
                version=self.api_version,
            ),
        )
        self.openapi_spec.components.security_schemes = self.security_schemes
        for tag_data in self.openapi_tags:
            self.openapi_spec.add_tag(**tag_data)

        # register endpoint to serve openapi spec if openapi_url is provided
        if self.openapi_url is not None:
            self.app.route(self.openapi_url, methods=["GET"])(self.get_openapi_view)

    def get_openapi_view(self):
        """Endpoint automatically generated by extension to serve openapi spec."""

        for url, method, operation in self.iterate_openapi_operations():
            self.openapi_spec.add_operation(url, method, operation)

        # if request.path.endswith(".yaml") or request.path.endswith(".yml"):
        #     return Response(self.spec.to_yaml(), headers={"Content-Type": "text/yaml"})
        # else:
        #     return Response(
        #         self.spec.to_json(indent=4),
        #         headers={"Content-Type": "application/json"},
        #     )
        return jsonify(self.openapi_spec.to_dict())

    def spec(self, **options):
        """Decorator used to add openapi specifications to a flask view"""

        def decorator(func: Callable):
            # inject __operation_uid attribute in view_func to be able to find associated spec
            operation_uid = uuid.uuid4()
            setattr(func, "__operation_uid", operation_uid)
            self.operations[operation_uid] = options

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def iterate_openapi_operations(self) -> Iterable[Tuple[str, str, OpenAPIOperation]]:
        """Iterate through app views that should be documented through openapi"""
        rule: werkzeug.routing.Rule
        view_func: Callable
        view_specs: dict

        for view_name, view_func in self.app.view_functions.items():
            try:
                operation_uid = getattr(view_func, "__operation_uid")
            except AttributeError:
                # if view does not contains __operation_uid, no spec is provided, skip it...
                continue

            view_specs = self.operations[operation_uid]

            operation = operation_from_view(
                self.schema_builder, view_name, view_func, view_specs
            )

            for rule in self.app.url_map.iter_rules(view_name):
                for method in rule.methods:
                    if method in self.documented_methods:
                        yield (rule.rule, method.lower(), operation)
