"""
Type annotations for route53-recovery-cluster service type definitions.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_route53_recovery_cluster/type_defs/)

Usage::

    ```python
    from types_aiobotocore_route53_recovery_cluster.type_defs import GetRoutingControlStateRequestRequestTypeDef

    data: GetRoutingControlStateRequestRequestTypeDef = {...}
    ```
"""
import sys
from typing import Dict, Sequence

from .literals import RoutingControlStateType

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "GetRoutingControlStateRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "UpdateRoutingControlStateEntryTypeDef",
    "UpdateRoutingControlStateRequestRequestTypeDef",
    "GetRoutingControlStateResponseTypeDef",
    "UpdateRoutingControlStatesRequestRequestTypeDef",
)

GetRoutingControlStateRequestRequestTypeDef = TypedDict(
    "GetRoutingControlStateRequestRequestTypeDef",
    {
        "RoutingControlArn": str,
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

UpdateRoutingControlStateEntryTypeDef = TypedDict(
    "UpdateRoutingControlStateEntryTypeDef",
    {
        "RoutingControlArn": str,
        "RoutingControlState": RoutingControlStateType,
    },
)

_RequiredUpdateRoutingControlStateRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRoutingControlStateRequestRequestTypeDef",
    {
        "RoutingControlArn": str,
        "RoutingControlState": RoutingControlStateType,
    },
)
_OptionalUpdateRoutingControlStateRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRoutingControlStateRequestRequestTypeDef",
    {
        "SafetyRulesToOverride": Sequence[str],
    },
    total=False,
)


class UpdateRoutingControlStateRequestRequestTypeDef(
    _RequiredUpdateRoutingControlStateRequestRequestTypeDef,
    _OptionalUpdateRoutingControlStateRequestRequestTypeDef,
):
    pass


GetRoutingControlStateResponseTypeDef = TypedDict(
    "GetRoutingControlStateResponseTypeDef",
    {
        "RoutingControlArn": str,
        "RoutingControlState": RoutingControlStateType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredUpdateRoutingControlStatesRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRoutingControlStatesRequestRequestTypeDef",
    {
        "UpdateRoutingControlStateEntries": Sequence[UpdateRoutingControlStateEntryTypeDef],
    },
)
_OptionalUpdateRoutingControlStatesRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRoutingControlStatesRequestRequestTypeDef",
    {
        "SafetyRulesToOverride": Sequence[str],
    },
    total=False,
)


class UpdateRoutingControlStatesRequestRequestTypeDef(
    _RequiredUpdateRoutingControlStatesRequestRequestTypeDef,
    _OptionalUpdateRoutingControlStatesRequestRequestTypeDef,
):
    pass
