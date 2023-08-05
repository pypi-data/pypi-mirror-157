from typing import Any, Dict, List, Optional

from botocore import xform_name as xform_name
from botocore.exceptions import BotoCoreError as BotoCoreError
from botocore.exceptions import ConnectionError as ConnectionError
from botocore.exceptions import HTTPClientError as HTTPClientError
from botocore.model import OperationModel
from botocore.model import OperationNotFoundError as OperationNotFoundError
from botocore.model import ServiceModel
from botocore.utils import CachedProperty as CachedProperty

class EndpointDiscoveryException(BotoCoreError): ...

class EndpointDiscoveryRequired(EndpointDiscoveryException):
    fmt: str = ...

class EndpointDiscoveryRefreshFailed(EndpointDiscoveryException):
    fmt: str = ...

def block_endpoint_discovery_required_operations(model: Any, **kwargs: Any) -> None: ...

class EndpointDiscoveryModel:
    def __init__(self, service_model: ServiceModel) -> None: ...
    @property
    def discovery_operation_name(self) -> str: ...
    @property
    def discovery_operation_keys(self) -> List[str]: ...
    def discovery_required_for(self, operation_name: str) -> bool: ...
    def discovery_operation_kwargs(self, **kwargs: Any) -> Dict[str, Any]: ...
    def gather_identifiers(self, operation: OperationModel, params: Any) -> Dict[str, Any]: ...

class EndpointDiscoveryManager:
    def __init__(
        self,
        client: Any,
        cache: Optional[Any] = ...,
        current_time: Optional[Any] = ...,
        always_discover: bool = ...,
    ) -> None: ...
    def gather_identifiers(self, operation: Any, params: Any) -> Any: ...
    def delete_endpoints(self, **kwargs: Any) -> None: ...
    def describe_endpoint(self, **kwargs: Any) -> Any: ...

class EndpointDiscoveryHandler:
    def __init__(self, manager: Any) -> None: ...
    def register(self, events: Any, service_id: Any) -> None: ...
    def gather_identifiers(self, params: Any, model: Any, context: Any, **kwargs: Any) -> None: ...
    def discover_endpoint(self, request: Any, operation_name: Any, **kwargs: Any) -> None: ...
    def handle_retries(
        self, request_dict: Any, response: Any, operation: Any, **kwargs: Any
    ) -> Any: ...
