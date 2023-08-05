# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import functools
from typing import Any, Callable, Dict, Generic, Iterable, Optional, TypeVar, Union
import warnings

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.paging import ItemPaged
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

def build_get_available_stacks_request(
    *,
    os_type_selected: Optional[Union[str, "_models.Enum4"]] = None,
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-06-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/providers/Microsoft.Web/availableStacks')

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    if os_type_selected is not None:
        query_parameters['osTypeSelected'] = _SERIALIZER.query("os_type_selected", os_type_selected, 'str')
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


def build_list_operations_request(
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-06-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/providers/Microsoft.Web/operations')

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


def build_get_available_stacks_on_prem_request(
    subscription_id: str,
    *,
    os_type_selected: Optional[Union[str, "_models.Enum5"]] = None,
    **kwargs: Any
) -> HttpRequest:
    api_version = "2020-06-01"
    accept = "application/json"
    # Construct URL
    url = kwargs.pop("template_url", '/subscriptions/{subscriptionId}/providers/Microsoft.Web/availableStacks')
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, 'str'),
    }

    url = _format_url_section(url, **path_format_arguments)

    # Construct parameters
    query_parameters = kwargs.pop("params", {})  # type: Dict[str, Any]
    if os_type_selected is not None:
        query_parameters['osTypeSelected'] = _SERIALIZER.query("os_type_selected", os_type_selected, 'str')
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

class ProviderOperations(object):
    """ProviderOperations operations.

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

    def __init__(self, client, config, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config

    @distributed_trace
    def get_available_stacks(
        self,
        os_type_selected: Optional[Union[str, "_models.Enum4"]] = None,
        **kwargs: Any
    ) -> Iterable["_models.ApplicationStackCollection"]:
        """Get available application frameworks and their versions.

        Description for Get available application frameworks and their versions.

        :param os_type_selected:
        :type os_type_selected: str or ~azure.mgmt.web.v2020_06_01.models.Enum4
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either ApplicationStackCollection or the result of
         cls(response)
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.mgmt.web.v2020_06_01.models.ApplicationStackCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.ApplicationStackCollection"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_get_available_stacks_request(
                    os_type_selected=os_type_selected,
                    template_url=self.get_available_stacks.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_get_available_stacks_request(
                    os_type_selected=os_type_selected,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("ApplicationStackCollection", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return ItemPaged(
            get_next, extract_data
        )
    get_available_stacks.metadata = {'url': '/providers/Microsoft.Web/availableStacks'}  # type: ignore

    @distributed_trace
    def list_operations(
        self,
        **kwargs: Any
    ) -> Iterable["_models.CsmOperationCollection"]:
        """Gets all available operations for the Microsoft.Web resource provider. Also exposes resource
        metric definitions.

        Description for Gets all available operations for the Microsoft.Web resource provider. Also
        exposes resource metric definitions.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either CsmOperationCollection or the result of
         cls(response)
        :rtype: ~azure.core.paging.ItemPaged[~azure.mgmt.web.v2020_06_01.models.CsmOperationCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.CsmOperationCollection"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_list_operations_request(
                    template_url=self.list_operations.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_list_operations_request(
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("CsmOperationCollection", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return ItemPaged(
            get_next, extract_data
        )
    list_operations.metadata = {'url': '/providers/Microsoft.Web/operations'}  # type: ignore

    @distributed_trace
    def get_available_stacks_on_prem(
        self,
        os_type_selected: Optional[Union[str, "_models.Enum5"]] = None,
        **kwargs: Any
    ) -> Iterable["_models.ApplicationStackCollection"]:
        """Get available application frameworks and their versions.

        Description for Get available application frameworks and their versions.

        :param os_type_selected:
        :type os_type_selected: str or ~azure.mgmt.web.v2020_06_01.models.Enum5
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An iterator like instance of either ApplicationStackCollection or the result of
         cls(response)
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.mgmt.web.v2020_06_01.models.ApplicationStackCollection]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["_models.ApplicationStackCollection"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                
                request = build_get_available_stacks_on_prem_request(
                    subscription_id=self._config.subscription_id,
                    os_type_selected=os_type_selected,
                    template_url=self.get_available_stacks_on_prem.metadata['url'],
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)

            else:
                
                request = build_get_available_stacks_on_prem_request(
                    subscription_id=self._config.subscription_id,
                    os_type_selected=os_type_selected,
                    template_url=next_link,
                )
                request = _convert_request(request)
                request.url = self._client.format_url(request.url)
                request.method = "GET"
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("ApplicationStackCollection", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.DefaultErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

            return pipeline_response


        return ItemPaged(
            get_next, extract_data
        )
    get_available_stacks_on_prem.metadata = {'url': '/subscriptions/{subscriptionId}/providers/Microsoft.Web/availableStacks'}  # type: ignore
