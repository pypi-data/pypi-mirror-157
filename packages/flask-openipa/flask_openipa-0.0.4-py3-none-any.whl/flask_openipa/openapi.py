import dataclasses
from typing import Dict, List, Set


def remove_empty_keys(data: dict):
    """Remove keys from a dict whose values are None"""

    for field, value in tuple(data.items()):
        if value is None:
            data.pop(field)
    return data


@dataclasses.dataclass
class OpenAPIRequestBody:
    content_type: str = None
    content_schema: dict = None

    def __post_init__(self):
        if self.content_type is None and self.content_schema is not None:
            self.content_type = "application/json"

    def to_spec(self):
        spec = {}
        if self.content_type is not None:
            spec["content"] = {self.content_type: {}}
        if self.content_schema is not None:
            spec["content"][self.content_type] = {"schema": self.content_schema}
        return spec


@dataclasses.dataclass
class OpenAPIParameter:
    ...


@dataclasses.dataclass
class OpenAPIResponse:
    ...


@dataclasses.dataclass
class OpenAPIOperation:
    """Describes a single API [operation](https://swagger.io/specification/#operation-object) on a path.

    Arguments:
        tags: A list of tags for API documentation control. Tags can be used for logical grouping of operations by resources or any other qualifier.
        summary: A short summary of what the operation does.
        description: A verbose explanation of the operation behavior. CommonMark syntax MAY be used for rich text representation.
        external_docs: External Documentation Object	Additional external documentation for this operation.
        operation_id: Unique string used to identify the operation. The id MUST be unique among all operations described in the API. The operationId value is case-sensitive. Tools and libraries MAY use the operationId to uniquely identify an operation, therefore, it is RECOMMENDED to follow common programming naming conventions.
        parameters: A list of parameters that are applicable for this operation. If a parameter is already defined at the Path Item, the new definition will override it but can never remove it. The list MUST NOT include duplicated parameters. A unique parameter is defined by a combination of a name and location. The list can use the Reference Object to link to parameters that are defined at the OpenAPI Object's components/parameters.
        request_body: The request body applicable for this operation. The requestBody is only supported in HTTP methods where the HTTP 1.1 specification RFC7231 has explicitly defined semantics for request bodies. In other cases where the HTTP spec is vague, requestBody SHALL be ignored by consumers.
        responses: The list of possible responses as they are returned from executing this operation.
        security: A declaration of which security mechanisms can be used for this operation. The list of values includes alternative security requirement objects that can be used. Only one of the security requirement objects need to be satisfied to authorize a request. To make security optional, an empty security requirement ({}) can be included in the array. This definition overrides any declared top-level security. To remove a top-level security declaration, an empty array can be used.
    """

    summary: str = None
    description: str = None
    tags: List[str] = None
    external_docs: str = None
    operation_id: str = None
    parameters: List[OpenAPIParameter] = None
    request_body: OpenAPIRequestBody = None
    responses: List[OpenAPIResponse] = None
    security: List[str] = None

    def to_spec(self):
        spec = dataclasses.asdict(self)
        spec.pop("request_body")
        spec["requestBody"] = self.request_body.to_spec()
        return remove_empty_keys(spec)


class OpenAPIPath(Dict[str, OpenAPIOperation]):
    def add_operation(self, method: str, operation: OpenAPIOperation):
        self[method] = operation

    def to_dict(self):
        return {
            method: operation_obj.to_spec() for method, operation_obj in self.items()
        }


@dataclasses.dataclass
class OpenAPIContact:
    """[Contact](https://swagger.io/specification/#contact-object) information for the exposed API.

    Arguments:
        name: The identifying name of the contact person/organization.
        url: The URL pointing to the contact information. MUST be in the format of a URL.
        email: The email address of the contact person/organization. MUST be in the format of an email address.
    """

    name: str
    url: str
    email: str


@dataclasses.dataclass
class OpenAPILicense:
    """[License](https://swagger.io/specification/#license-object) information for the exposed API.

    Arguments:
        name: The license name used for the API.
        url: A URL to the license used for the API. MUST be in the format of a URL.
    """

    name: str
    url: str


@dataclasses.dataclass
class OpenAPIInfo:
    """[Information](https://swagger.io/specification/#info-object) about the API.

    Arguments:
        title: The title of the API.
        description: A short description of the API. CommonMark syntax MAY be used for rich text representation.
        terms_of_service_url: A URL to the Terms of Service for the API. MUST be in the format of a URL.
        contact: The contact information for the exposed API.
        license: The license information for the exposed API.
        version: The version of the OpenAPI document (which is distinct from the OpenAPI Specification version or the API implementation version).
    """

    title: str = None
    description: str = None
    terms_of_service_url: str = None
    version: str = None
    contact: OpenAPIContact = None
    license: OpenAPILicense = None

    def to_dict(self):
        data = dataclasses.asdict(self)
        return remove_empty_keys(data)


@dataclasses.dataclass
class OpenAPIComponents:
    security_schemes: dict = dataclasses.field(default=dict)
    schemas: dict = dataclasses.field(default_factory=dict)

    def to_dict(self):
        data = dataclasses.asdict(self)
        data["securitySchemes"] = data.pop("security_schemes")
        return remove_empty_keys(data)


@dataclasses.dataclass
class OpenAPIServer:
    url: str

    def __hash__(self):
        return hash(self.url)

    def to_spec(self):
        return {"url": self.url}


@dataclasses.dataclass
class OpenAPIServers:
    _servers: Set[OpenAPIServer] = dataclasses.field(default_factory=set)

    def add(self, url: str):
        self._servers.add(OpenAPIServer(url))

    def to_spec(self):
        if len(self._servers) == 0:
            return None
        return [server.to_spec() for server in self._servers]


@dataclasses.dataclass
class OpenAPITag:
    name: str
    description: str = ""
    doc_description: str = "doc"
    doc_url: str = None

    def __hash__(self):
        return hash(self.name)

    def to_spec(self):
        data = {"name": self.name, "description": self.description}
        if self.doc_url is not None:
            data["externalDocs"] = {
                "description": self.doc_description,
                "url": self.doc_url,
            }
        return data


@dataclasses.dataclass
class OpenAPITags:
    _tags: Set[OpenAPITag] = dataclasses.field(default_factory=set)

    def add(
        self,
        name: str,
        description: str = None,
        doc_description: str = "doc",
        doc_url: str = None,
    ):
        self._tags.add(OpenAPITag(name, description, doc_description, doc_url))

    def to_spec(self):
        if len(self._tags) == 0:
            return None
        return [tag.to_spec() for tag in self._tags]


@dataclasses.dataclass
class OpenAPISpec:
    """Represents openapi specification."""

    openapi: str = "3.0.0"
    info: OpenAPIInfo = None
    paths: Dict[str, OpenAPIPath] = dataclasses.field(default_factory=dict)
    components: OpenAPIComponents = dataclasses.field(default_factory=OpenAPIComponents)
    servers: OpenAPIServers = dataclasses.field(default_factory=OpenAPIServers)
    tags: OpenAPITags = dataclasses.field(default_factory=OpenAPITags)

    def add_schema(self, name: str, schema: dict):
        self.components.schemas[name] = schema

    def add_operation(self, url: str, method: str, operation: OpenAPIOperation):
        if self.paths.get(url) is None:
            self.paths[url] = OpenAPIPath()
        self.paths[url].add_operation(method, operation)

    def add_server(self, url: str):
        self.servers.add(url)

    def add_tag(
        self,
        name: str,
        description: str = None,
        doc_description: str = "doc",
        doc_url: str = None,
    ):
        self.tags.add(name, description, doc_description, doc_url)

    def to_dict(self):
        return remove_empty_keys(
            {
                "openapi": self.openapi,
                "info": self.info.to_dict(),
                "paths": {
                    url: path_obj.to_dict() for url, path_obj in self.paths.items()
                },
                "components": self.components.to_dict(),
                "servers": self.servers.to_spec(),
                "tags": self.tags.to_spec(),
            }
        )
