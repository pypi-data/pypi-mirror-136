# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import functools
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
import warnings

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.mgmt.core.exceptions import ARMErrorFormat
from msrest import Serializer

from .. import models as _models
from .._vendor import _convert_request, _format_url_section
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

def build_get_deleted_web_app_request(
    deleted_site_id: str,
    subscription_id: str,
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-12-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/providers/Microsoft.Web/deletedSites/{deletedSiteId}')
    path_format_arguments = {
        "deletedSiteId": _SERIALIZER.url("deleted_site_id", deleted_site_id, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="GET",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )


def build_get_deleted_web_app_snapshots_request(
    deleted_site_id: str,
    subscription_id: str,
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-12-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/providers/Microsoft.Web/deletedSites/{deletedSiteId}/snapshots')
    path_format_arguments = {
        "deletedSiteId": _SERIALIZER.url("deleted_site_id", deleted_site_id, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="GET",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )


def build_get_subscription_operation_with_async_response_request(
    location: str,
    operation_id: str,
    subscription_id: str,
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-12-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/providers/Microsoft.Web/locations/{location}/operations/{operationId}')
    path_format_arguments = {
        "location": _SERIALIZER.url("location", location, 'str'),
        "operationId": _SERIALIZER.url("operation_id", operation_id, 'str'),
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    query_parameters['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    header_parameters = kwargs.pop("headers", {})  # type: Dict[str, Any]
    header_parameters['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="GET",
        url=url,
        params=query_parameters,
        headers=header_parameters,
        **kwargs
    )

class GlobalOperations(object):
    """GlobalOperations operations.

    You should not instantiate this class directly. Instead, you should create a Client instance that
    instantiates it for you and attaches it as an attribute.

    :ivar models: Alias to model classes used in this operation group.
    :type models: ~azure.mgmt.web.v2020_12_01.models
    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = _models

    def __init__(self, client, config, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    @distributed_trace
    def get_deleted_web_app(
        self,
        deleted_site_id: str,
        **kwargs: Any
    ) -> "_models.DeletedSite":
        """Get deleted app for a subscription.

        Description for Get deleted app for a subscription.

        :param deleted_site_id: The numeric ID of the deleted app, e.g. 12345.
        :type deleted_site_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: DeletedSite, or the result of cls(response)
        :rtype: ~azure.mgmt.web.v2020_12_01.models.DeletedSite
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.DeletedSite"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_get_deleted_web_app_request(
            deleted_site_id=deleted_site_id,
            subscription_id=self._config.subscription_id,
            template_url=self.get_deleted_web_app.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = self._deserialize('DeletedSite', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    get_deleted_web_app.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/deletedSites/{deletedSiteId}'}  # type: ignore


    @distributed_trace
    def get_deleted_web_app_snapshots(
        self,
        deleted_site_id: str,
        **kwargs: Any
    ) -> List["_models.Snapshot"]:
        """Get all deleted apps for a subscription.

        Description for Get all deleted apps for a subscription.

        :param deleted_site_id: The numeric ID of the deleted app, e.g. 12345.
        :type deleted_site_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: list of Snapshot, or the result of cls(response)
        :rtype: list[~azure.mgmt.web.v2020_12_01.models.Snapshot]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[List["_models.Snapshot"]]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_get_deleted_web_app_snapshots_request(
            deleted_site_id=deleted_site_id,
            subscription_id=self._config.subscription_id,
            template_url=self.get_deleted_web_app_snapshots.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = self._deserialize('[Snapshot]', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    get_deleted_web_app_snapshots.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/deletedSites/{deletedSiteId}/snapshots'}  # type: ignore


    @distributed_trace
    def get_subscription_operation_with_async_response(
        self,
        location: str,
        operation_id: str,
        **kwargs: Any
    ) -> None:
        """Gets an operation in a subscription and given region.

        Description for Gets an operation in a subscription and given region.

        :param location: Location name.
        :type location: str
        :param operation_id: Operation Id.
        :type operation_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))

        
        request = build_get_subscription_operation_with_async_response_request(
            location=location,
            operation_id=operation_id,
            subscription_id=self._config.subscription_id,
            template_url=self.get_subscription_operation_with_async_response.metadata['url'],
        )
        request = _convert_request(request)
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [204]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        if cls:
            return cls(pipeline_response, None, {})

    get_subscription_operation_with_async_response.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/locations/{location}/operations/{operationId}'}  # type: ignore

