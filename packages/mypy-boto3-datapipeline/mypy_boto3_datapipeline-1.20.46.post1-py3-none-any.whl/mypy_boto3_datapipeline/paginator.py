"""
Type annotations for datapipeline service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_datapipeline import DataPipelineClient
    from mypy_boto3_datapipeline.paginator import (
        DescribeObjectsPaginator,
        ListPipelinesPaginator,
        QueryObjectsPaginator,
    )

    client: DataPipelineClient = boto3.client("datapipeline")

    describe_objects_paginator: DescribeObjectsPaginator = client.get_paginator("describe_objects")
    list_pipelines_paginator: ListPipelinesPaginator = client.get_paginator("list_pipelines")
    query_objects_paginator: QueryObjectsPaginator = client.get_paginator("query_objects")
    ```
"""
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    DescribeObjectsOutputTypeDef,
    ListPipelinesOutputTypeDef,
    PaginatorConfigTypeDef,
    QueryObjectsOutputTypeDef,
    QueryTypeDef,
)

__all__ = ("DescribeObjectsPaginator", "ListPipelinesPaginator", "QueryObjectsPaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class DescribeObjectsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.DescribeObjects)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#describeobjectspaginator)
    """

    def paginate(
        self,
        *,
        pipelineId: str,
        objectIds: Sequence[str],
        evaluateExpressions: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[DescribeObjectsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.DescribeObjects.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#describeobjectspaginator)
        """


class ListPipelinesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.ListPipelines)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#listpipelinespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPipelinesOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.ListPipelines.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#listpipelinespaginator)
        """


class QueryObjectsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.QueryObjects)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#queryobjectspaginator)
    """

    def paginate(
        self,
        *,
        pipelineId: str,
        sphere: str,
        query: "QueryTypeDef" = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[QueryObjectsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.46/reference/services/datapipeline.html#DataPipeline.Paginator.QueryObjects.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_datapipeline/paginators.html#queryobjectspaginator)
        """
