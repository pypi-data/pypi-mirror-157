
from typing import List, Optional, Dict, Set
from pyterraformer.core.resources import ResourceObject
from pyterraformer.core.generics import BlockList, BlockSet
from pyterraformer.core.objects import ObjectMetadata
from dataclasses import dataclass




# this block can contain multiple items, items in a list are required
@dataclass
class ActionItem():
    type:str
    # non-optional-blocks
    storage_class: Optional[str] = None

# wrapper list class
class Action(BlockSet):
    items: Set[ActionItem]




# this block can contain multiple items, items in a list are required
@dataclass
class ConditionItem():
    # non-optional-blocks
    age: Optional[float] = None
    created_before: Optional[str] = None
    custom_time_before: Optional[str] = None
    days_since_custom_time: Optional[float] = None
    days_since_noncurrent_time: Optional[float] = None
    matches_storage_class: Optional[List[str]] = None
    noncurrent_time_before: Optional[str] = None
    num_newer_versions: Optional[float] = None
    with_state: Optional[str] = None

# wrapper list class
class Condition(BlockSet):
    items: Set[ConditionItem]




# this block can contain multiple items, items in a list are required
@dataclass
class CorsItem():
    # non-optional-blocks
    max_age_seconds: Optional[float] = None
    method: Optional[List[str]] = None
    origin: Optional[List[str]] = None
    response_header: Optional[List[str]] = None

# wrapper list class
class Cors(BlockList):
    items: List[CorsItem]





# this block can contain multiple items, items in a list are required
@dataclass
class EncryptionItem():
    default_kms_key_name:str
    # non-optional-blocks

# wrapper list class
class Encryption(BlockList):
    items: List[EncryptionItem]





# this block can contain multiple items, items in a list are required
@dataclass
class LifecycleRuleItem():
    # non-optional-blocks
    action: Optional[Action]=None,
    condition: Optional[Condition]=None,

# wrapper list class
class LifecycleRule(BlockList):
    items: List[LifecycleRuleItem]





# this block can contain multiple items, items in a list are required
@dataclass
class LoggingItem():
    log_bucket:str
    # non-optional-blocks
    log_object_prefix: Optional[str] = None

# wrapper list class
class Logging(BlockList):
    items: List[LoggingItem]





# this block can contain multiple items, items in a list are required
@dataclass
class RetentionPolicyItem():
    retention_period:float
    # non-optional-blocks
    is_locked: Optional[bool] = None

# wrapper list class
class RetentionPolicy(BlockList):
    items: List[RetentionPolicyItem]




# this block accepts only a single value, set the class directly
@dataclass
class Timeouts():
    # non-optional-blocks
    create: Optional[str] = None
    read: Optional[str] = None
    update: Optional[str] = None





# this block can contain multiple items, items in a list are required
@dataclass
class VersioningItem():
    enabled:bool
    # non-optional-blocks

# wrapper list class
class Versioning(BlockList):
    items: List[VersioningItem]





# this block can contain multiple items, items in a list are required
@dataclass
class WebsiteItem():
    # non-optional-blocks
    main_page_suffix: Optional[str] = None
    not_found_page: Optional[str] = None

# wrapper list class
class Website(BlockList):
    items: List[WebsiteItem]





class GoogleStorageBucket(ResourceObject):
    """
    Args:
        location (str): The Google Cloud Storage location
        name (str): The name of the bucket.
    """
    _type = 'google_storage_bucket'

    def __init__(self,
                 tf_id: str,
                 location:str,
                 name:str,
                 # non-optional-blocks
                 #optional
                 metadata: Optional[ObjectMetadata] = None,
                 default_event_based_hold: Optional[bool] = None,
                 force_destroy: Optional[bool] = None,
                 id: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None,
                 project: Optional[str] = None,
                 requester_pays: Optional[bool] = None,
                 storage_class: Optional[str] = None,
                 uniform_bucket_level_access: Optional[bool] = None,
                 action: Optional[Action]=None,
                 condition: Optional[Condition]=None,
                 cors: Optional[Cors]=None,
                 encryption: Optional[Encryption]=None,
                 lifecycle_rule: Optional[LifecycleRule]=None,
                 logging: Optional[Logging]=None,
                 retention_policy: Optional[RetentionPolicy]=None,
                 timeouts: Optional[Timeouts]=None,
                 versioning: Optional[Versioning]=None,
                 website: Optional[Website]=None,
                 ):
        kwargs = {}
        if location is not None:
            kwargs['location'] = location
        if name is not None:
            kwargs['name'] = name
        if default_event_based_hold is not None:
            kwargs['default_event_based_hold'] = default_event_based_hold
        if force_destroy is not None:
            kwargs['force_destroy'] = force_destroy
        if id is not None:
            kwargs['id'] = id
        if labels is not None:
            kwargs['labels'] = labels
        if project is not None:
            kwargs['project'] = project
        if requester_pays is not None:
            kwargs['requester_pays'] = requester_pays
        if storage_class is not None:
            kwargs['storage_class'] = storage_class
        if uniform_bucket_level_access is not None:
            kwargs['uniform_bucket_level_access'] = uniform_bucket_level_access
        if action is not None:
            kwargs['action'] = action
        if condition is not None:
            kwargs['condition'] = condition
        if cors is not None:
            kwargs['cors'] = cors
        if encryption is not None:
            kwargs['encryption'] = encryption
        if lifecycle_rule is not None:
            kwargs['lifecycle_rule'] = lifecycle_rule
        if logging is not None:
            kwargs['logging'] = logging
        if retention_policy is not None:
            kwargs['retention_policy'] = retention_policy
        if timeouts is not None:
            kwargs['timeouts'] = timeouts
        if versioning is not None:
            kwargs['versioning'] = versioning
        if website is not None:
            kwargs['website'] = website

        super().__init__(tf_id=tf_id, metadata=metadata, **kwargs)



