"""
Type annotations for opsworks service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworks/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_opsworks import OpsWorksClient
    from mypy_boto3_opsworks.paginator import (
        DescribeEcsClustersPaginator,
    )

    client: OpsWorksClient = boto3.client("opsworks")

    describe_ecs_clusters_paginator: DescribeEcsClustersPaginator = client.get_paginator("describe_ecs_clusters")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import DescribeEcsClustersResultTypeDef, PaginatorConfigTypeDef

__all__ = ("DescribeEcsClustersPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeEcsClustersPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/opsworks.html#OpsWorks.Paginator.DescribeEcsClusters)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworks/paginators.html#describeecsclusterspaginator)
    """

    def paginate(
        self,
        *,
        EcsClusterArns: Sequence[str] = ...,
        StackId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeEcsClustersResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/opsworks.html#OpsWorks.Paginator.DescribeEcsClusters.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opsworks/paginators.html#describeecsclusterspaginator)
        """
