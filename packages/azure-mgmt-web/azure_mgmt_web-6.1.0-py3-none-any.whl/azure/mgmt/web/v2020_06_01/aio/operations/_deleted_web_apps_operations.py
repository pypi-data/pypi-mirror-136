# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import functools
from typing import Any, AsyncIterable, Callable, Dict, Generic, Optional, TypeVar
import warnings

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.mgmt.core.exceptions import ARMErrorFormat

from ... import models as _models
from ..._vendor import _convert_request
from ...operations._deleted_web_apps_operations import build_get_deleted_web_app_by_location_request, build_list_by_location_request, build_list_request
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

class DeletedWebAppsOperations:
    """DeletedWebAppsOperations async operations.

    You should not instantiate this class directly. Instead, you should create a Client instance that
    instantiates it for you and attaches it as an attribute.

    :ivar models: Alias to model classes used in this operation group.
    :type models: ~azure.mgmt.web.v2020_06_01.models
    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = _models

    def __init__(self, client, config, serializer, deserializer) -> None:
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    @distributed_trace
    def list(
        self,
        **kwargs: Any
    ) -> AsyncIterable["_models.DeletedWebAppCollection"]:
        """Get all deleted apps for a subscription.

        Description for Get all deleted apps for a subscription.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either DeletedWebAppCollection or the result of
         cls(response)
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.mgmt.web.v2020_06_01.models.DeletedWebAppCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.DeletedWebAppCollection"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_list_request(
                    subscription_id=self._config.subscription_id,
                    template_url=self.list.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_list_request(
                    subscription_id=self._config.subscription_id,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        async def extract_data(pipeline_response):
            deserialized = self._deserialize("DeletedWebAppCollection", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return AsyncItemPaged(
            get_next, extract_data
        )
    list.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/deletedSites'}  # type: ignore

    @distributed_trace
    def list_by_location(
        self,
        location: str,
        **kwargs: Any
    ) -> AsyncIterable["_models.DeletedWebAppCollection"]:
        """Get all deleted apps for a subscription at location.

        Description for Get all deleted apps for a subscription at location.

        :param location:
        :type location: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either DeletedWebAppCollection or the result of
         cls(response)
        :rtype:
         ~azure.core.async_paging.AsyncItemPaged[~azure.mgmt.web.v2020_06_01.models.DeletedWebAppCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.DeletedWebAppCollection"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_list_by_location_request(
                    location=location,
                    subscription_id=self._config.subscription_id,
                    template_url=self.list_by_location.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_list_by_location_request(
                    location=location,
                    subscription_id=self._config.subscription_id,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        async def extract_data(pipeline_response):
            deserialized = self._deserialize("DeletedWebAppCollection", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return AsyncItemPaged(
            get_next, extract_data
        )
    list_by_location.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/locations/{location}/deletedSites'}  # type: ignore

    @distributed_trace_async
    async def get_deleted_web_app_by_location(
        self,
        location: str,
        deleted_site_id: str,
        **kwargs: Any
    ) -> "_models.DeletedSite":
        """Get deleted app for a subscription at location.

        Description for Get deleted app for a subscription at location.

        :param location:
        :type location: str
        :param deleted_site_id: The numeric ID of the deleted app, e.g. 12345.
        :type deleted_site_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: DeletedSite, or the result of cls(response)
        :rtype: ~azure.mgmt.web.v2020_06_01.models.DeletedSite
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.DeletedSite"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_get_deleted_web_app_by_location_request(
            location=location,
            deleted_site_id=deleted_site_id,
            subscription_id=self._config.subscription_id,
            template_url=self.get_deleted_web_app_by_location.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = self._deserialize('DeletedSite', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    get_deleted_web_app_by_location.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/locations/{location}/deletedSites/{deletedSiteId}'}  # type: ignore

