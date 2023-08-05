# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, Awaitable, Optional, TYPE_CHECKING

from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.mgmt.core import AsyncARMPipelineClient
from msrest import Deserializer, Serializer

from .. import models
from ._configuration import WebSiteManagementClientConfiguration
from .operations import AppServiceCertificateOrdersOperations, AppServiceEnvironmentsOperations, AppServicePlansOperations, CertificateOrdersDiagnosticsOperations, CertificateRegistrationProviderOperations, CertificatesOperations, ContainerAppsOperations, ContainerAppsRevisionsOperations, DeletedWebAppsOperations, DiagnosticsOperations, DomainRegistrationProviderOperations, DomainsOperations, GlobalOperations, KubeEnvironmentsOperations, ProviderOperations, RecommendationsOperations, ResourceHealthMetadataOperations, StaticSitesOperations, TopLevelDomainsOperations, WebAppsOperations, WebSiteManagementClientOperationsMixin

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential

class WebSiteManagementClient(WebSiteManagementClientOperationsMixin):
    """WebSite Management Client.

    :ivar app_service_certificate_orders: AppServiceCertificateOrdersOperations operations
    :vartype app_service_certificate_orders:
     azure.mgmt.web.v2021_03_01.aio.operations.AppServiceCertificateOrdersOperations
    :ivar certificate_orders_diagnostics: CertificateOrdersDiagnosticsOperations operations
    :vartype certificate_orders_diagnostics:
     azure.mgmt.web.v2021_03_01.aio.operations.CertificateOrdersDiagnosticsOperations
    :ivar certificate_registration_provider: CertificateRegistrationProviderOperations operations
    :vartype certificate_registration_provider:
     azure.mgmt.web.v2021_03_01.aio.operations.CertificateRegistrationProviderOperations
    :ivar domains: DomainsOperations operations
    :vartype domains: azure.mgmt.web.v2021_03_01.aio.operations.DomainsOperations
    :ivar top_level_domains: TopLevelDomainsOperations operations
    :vartype top_level_domains: azure.mgmt.web.v2021_03_01.aio.operations.TopLevelDomainsOperations
    :ivar domain_registration_provider: DomainRegistrationProviderOperations operations
    :vartype domain_registration_provider:
     azure.mgmt.web.v2021_03_01.aio.operations.DomainRegistrationProviderOperations
    :ivar app_service_environments: AppServiceEnvironmentsOperations operations
    :vartype app_service_environments:
     azure.mgmt.web.v2021_03_01.aio.operations.AppServiceEnvironmentsOperations
    :ivar app_service_plans: AppServicePlansOperations operations
    :vartype app_service_plans: azure.mgmt.web.v2021_03_01.aio.operations.AppServicePlansOperations
    :ivar certificates: CertificatesOperations operations
    :vartype certificates: azure.mgmt.web.v2021_03_01.aio.operations.CertificatesOperations
    :ivar container_apps: ContainerAppsOperations operations
    :vartype container_apps: azure.mgmt.web.v2021_03_01.aio.operations.ContainerAppsOperations
    :ivar container_apps_revisions: ContainerAppsRevisionsOperations operations
    :vartype container_apps_revisions:
     azure.mgmt.web.v2021_03_01.aio.operations.ContainerAppsRevisionsOperations
    :ivar deleted_web_apps: DeletedWebAppsOperations operations
    :vartype deleted_web_apps: azure.mgmt.web.v2021_03_01.aio.operations.DeletedWebAppsOperations
    :ivar diagnostics: DiagnosticsOperations operations
    :vartype diagnostics: azure.mgmt.web.v2021_03_01.aio.operations.DiagnosticsOperations
    :ivar global_operations: GlobalOperations operations
    :vartype global_operations: azure.mgmt.web.v2021_03_01.aio.operations.GlobalOperations
    :ivar kube_environments: KubeEnvironmentsOperations operations
    :vartype kube_environments:
     azure.mgmt.web.v2021_03_01.aio.operations.KubeEnvironmentsOperations
    :ivar provider: ProviderOperations operations
    :vartype provider: azure.mgmt.web.v2021_03_01.aio.operations.ProviderOperations
    :ivar recommendations: RecommendationsOperations operations
    :vartype recommendations: azure.mgmt.web.v2021_03_01.aio.operations.RecommendationsOperations
    :ivar resource_health_metadata: ResourceHealthMetadataOperations operations
    :vartype resource_health_metadata:
     azure.mgmt.web.v2021_03_01.aio.operations.ResourceHealthMetadataOperations
    :ivar static_sites: StaticSitesOperations operations
    :vartype static_sites: azure.mgmt.web.v2021_03_01.aio.operations.StaticSitesOperations
    :ivar web_apps: WebAppsOperations operations
    :vartype web_apps: azure.mgmt.web.v2021_03_01.aio.operations.WebAppsOperations
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param subscription_id: Your Azure subscription ID. This is a GUID-formatted string (e.g.
     00000000-0000-0000-0000-000000000000).
    :type subscription_id: str
    :param base_url: Service URL. Default value is 'https://management.azure.com'.
    :type base_url: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: "AsyncTokenCredential",
        subscription_id: str,
        base_url: str = "https://management.azure.com",
        **kwargs: Any
    ) -> None:
        self._config = WebSiteManagementClientConfiguration(credential=credential, subscription_id=subscription_id, **kwargs)
        self._client = AsyncARMPipelineClient(base_url=base_url, config=self._config, **kwargs)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False
        self.app_service_certificate_orders = AppServiceCertificateOrdersOperations(self._client, self._config, self._serialize, self._deserialize)
        self.certificate_orders_diagnostics = CertificateOrdersDiagnosticsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.certificate_registration_provider = CertificateRegistrationProviderOperations(self._client, self._config, self._serialize, self._deserialize)
        self.domains = DomainsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.top_level_domains = TopLevelDomainsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.domain_registration_provider = DomainRegistrationProviderOperations(self._client, self._config, self._serialize, self._deserialize)
        self.app_service_environments = AppServiceEnvironmentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.app_service_plans = AppServicePlansOperations(self._client, self._config, self._serialize, self._deserialize)
        self.certificates = CertificatesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.container_apps = ContainerAppsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.container_apps_revisions = ContainerAppsRevisionsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.deleted_web_apps = DeletedWebAppsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.diagnostics = DiagnosticsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.global_operations = GlobalOperations(self._client, self._config, self._serialize, self._deserialize)
        self.kube_environments = KubeEnvironmentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.provider = ProviderOperations(self._client, self._config, self._serialize, self._deserialize)
        self.recommendations = RecommendationsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.resource_health_metadata = ResourceHealthMetadataOperations(self._client, self._config, self._serialize, self._deserialize)
        self.static_sites = StaticSitesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.web_apps = WebAppsOperations(self._client, self._config, self._serialize, self._deserialize)


    def _send_request(
        self,
        request: HttpRequest,
        **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = await client._send_request(request)
        <AsyncHttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/python/protocol/quickstart

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """

        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, **kwargs)

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "WebSiteManagementClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)
