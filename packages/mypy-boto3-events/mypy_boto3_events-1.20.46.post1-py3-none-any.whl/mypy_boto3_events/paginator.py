"""
Type annotations for events service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_events import EventBridgeClient
    from mypy_boto3_events.paginator import (
        ListRuleNamesByTargetPaginator,
        ListRulesPaginator,
        ListTargetsByRulePaginator,
    )

    client: EventBridgeClient = boto3.client("events")

    list_rule_names_by_target_paginator: ListRuleNamesByTargetPaginator = client.get_paginator("list_rule_names_by_target")
    list_rules_paginator: ListRulesPaginator = client.get_paginator("list_rules")
    list_targets_by_rule_paginator: ListTargetsByRulePaginator = client.get_paginator("list_targets_by_rule")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    ListRuleNamesByTargetResponseTypeDef,
    ListRulesResponseTypeDef,
    ListTargetsByRuleResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = ("ListRuleNamesByTargetPaginator", "ListRulesPaginator", "ListTargetsByRulePaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListRuleNamesByTargetPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListRuleNamesByTarget)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listrulenamesbytargetpaginator)
    """

    def paginate(
        self,
        *,
        TargetArn: str,
        EventBusName: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRuleNamesByTargetResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListRuleNamesByTarget.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listrulenamesbytargetpaginator)
        """


class ListRulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListRules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listrulespaginator)
    """

    def paginate(
        self,
        *,
        NamePrefix: str = ...,
        EventBusName: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRulesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListRules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listrulespaginator)
        """


class ListTargetsByRulePaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListTargetsByRule)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listtargetsbyrulepaginator)
    """

    def paginate(
        self, *, Rule: str, EventBusName: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListTargetsByRuleResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/events.html#EventBridge.Paginator.ListTargetsByRule.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_events/paginators.html#listtargetsbyrulepaginator)
        """
