# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from six import with_metaclass
from azure.core import CaseInsensitiveEnumMeta


class AccessControlEntryAction(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Action object.
    """

    PERMIT = "Permit"
    DENY = "Deny"

class AutoHealActionType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Predefined action to be taken.
    """

    RECYCLE = "Recycle"
    LOG_EVENT = "LogEvent"
    CUSTOM_ACTION = "CustomAction"

class ComputeModeOptions(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Shared/dedicated workers.
    """

    SHARED = "Shared"
    DEDICATED = "Dedicated"
    DYNAMIC = "Dynamic"

class ConnectionStringType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Type of database.
    """

    MY_SQL = "MySql"
    SQL_SERVER = "SQLServer"
    SQL_AZURE = "SQLAzure"
    CUSTOM = "Custom"
    NOTIFICATION_HUB = "NotificationHub"
    SERVICE_BUS = "ServiceBus"
    EVENT_HUB = "EventHub"
    API_HUB = "ApiHub"
    DOC_DB = "DocDb"
    REDIS_CACHE = "RedisCache"
    POSTGRE_SQL = "PostgreSQL"

class HostingEnvironmentStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Current status of the App Service Environment.
    """

    PREPARING = "Preparing"
    READY = "Ready"
    SCALING = "Scaling"
    DELETING = "Deleting"

class HostType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Indicates whether the hostname is a standard or repository hostname.
    """

    STANDARD = "Standard"
    REPOSITORY = "Repository"

class InternalLoadBalancingMode(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Specifies which endpoints to serve internally in the Virtual Network for the App Service
    Environment.
    """

    NONE = "None"
    WEB = "Web"
    PUBLISHING = "Publishing"

class ManagedPipelineMode(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Managed pipeline mode.
    """

    INTEGRATED = "Integrated"
    CLASSIC = "Classic"

class ManagedServiceIdentityType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Type of managed service identity.
    """

    SYSTEM_ASSIGNED = "SystemAssigned"

class OperationStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The current status of the operation.
    """

    IN_PROGRESS = "InProgress"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    TIMED_OUT = "TimedOut"
    CREATED = "Created"

class ProvisioningState(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Provisioning state of the App Service Environment.
    """

    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"
    IN_PROGRESS = "InProgress"
    DELETING = "Deleting"

class RouteType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The type of route this is:
    DEFAULT - By default, every app has routes to the local address ranges specified by RFC1918
    INHERITED - Routes inherited from the real Virtual Network routes
    STATIC - Static route set on the app only
    
    These values will be used for syncing an app's routes with those from a Virtual Network.
    """

    DEFAULT = "DEFAULT"
    INHERITED = "INHERITED"
    STATIC = "STATIC"

class ScmType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """SCM type.
    """

    NONE = "None"
    DROPBOX = "Dropbox"
    TFS = "Tfs"
    LOCAL_GIT = "LocalGit"
    GIT_HUB = "GitHub"
    CODE_PLEX_GIT = "CodePlexGit"
    CODE_PLEX_HG = "CodePlexHg"
    BITBUCKET_GIT = "BitbucketGit"
    BITBUCKET_HG = "BitbucketHg"
    EXTERNAL_GIT = "ExternalGit"
    EXTERNAL_HG = "ExternalHg"
    ONE_DRIVE = "OneDrive"
    VSO = "VSO"

class SiteAvailabilityState(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Management information availability state for the app.
    """

    NORMAL = "Normal"
    LIMITED = "Limited"
    DISASTER_RECOVERY_MODE = "DisasterRecoveryMode"

class SiteLoadBalancing(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Site load balancing.
    """

    WEIGHTED_ROUND_ROBIN = "WeightedRoundRobin"
    LEAST_REQUESTS = "LeastRequests"
    LEAST_RESPONSE_TIME = "LeastResponseTime"
    WEIGHTED_TOTAL_TRAFFIC = "WeightedTotalTraffic"
    REQUEST_HASH = "RequestHash"

class SslState(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """SSL type.
    """

    DISABLED = "Disabled"
    SNI_ENABLED = "SniEnabled"
    IP_BASED_ENABLED = "IpBasedEnabled"

class StatusOptions(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """App Service plan status.
    """

    READY = "Ready"
    PENDING = "Pending"
    CREATING = "Creating"

class SupportedTlsVersions(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """MinTlsVersion: configures the minimum version of TLS required for SSL requests
    """

    ONE0 = "1.0"
    ONE1 = "1.1"
    ONE2 = "1.2"

class UsageState(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """State indicating whether the app has exceeded its quota usage. Read-only.
    """

    NORMAL = "Normal"
    EXCEEDED = "Exceeded"

class WorkerSizeOptions(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Size of the machines.
    """

    DEFAULT = "Default"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
