Package `exchangelib`
------

`exchangelib.account``exchangelib.attachments``exchangelib.autodiscover``exchangelib.configuration``exchangelib.credentials`
Implements an Exchange user object and access types. Exchange provides two different ways of granting access for a login to a specific account …

`exchangelib.errors`
Stores errors specific to this package, and mirrors all the possible errors that EWS can return.

`exchangelib.ewsdatetime``exchangelib.extended_properties``exchangelib.fields``exchangelib.folders``exchangelib.indexed_properties``exchangelib.items``exchangelib.properties``exchangelib.protocol`
A protocol is an endpoint for EWS service connections. It contains all necessary information to make HTTPS connections …

`exchangelib.queryset``exchangelib.recurrence``exchangelib.restriction``exchangelib.services`
Implement a selection of EWS services (operations) …

`exchangelib.settings``exchangelib.transport``exchangelib.util``exchangelib.version``exchangelib.winzone`
A dict to translate from IANA location name to Windows timezone name. Translations taken from CLDR_WINZONE_URL

```
def UTC_NOW()
```

Expand source code`UTC_NOW = lambda: EWSDateTime.now(tz=UTC) # noqa: E731`

```
def close_connections()
```

Expand source code
```
def close_connections():
from .autodiscover import close_connections as close_autodiscover_connections
from .protocol import close_connections as close_protocol_connections

close_autodiscover_connections()
close_protocol_connections()
```

```
def discover(email, credentials=None, auth_type=None, retry_policy=None)
```

Expand source code
```
def discover(email, credentials=None, auth_type=None, retry_policy=None):
ad_response, protocol = Autodiscovery(email=email, credentials=credentials).discover()
if auth_type:
protocol.config.auth_type = auth_type
if retry_policy:
protocol.config.retry_policy = retry_policy
return ad_response, protocol
```

```
class AcceptItem
(**kwargs)
```

Expand source code
```
class AcceptItem(BaseMeetingReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/acceptitem"""

ELEMENT_NAME = "AcceptItem"
```

### Ancestors

* [BaseMeetingReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/calendar_item.html#exchangelib.items.calendar_item.BaseMeetingReplyItem "exchangelib.items.calendar_item.BaseMeetingReplyItem")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseMeetingReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attachments`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `deregister`
* `headers`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `item_class`
* `proposed_end`
* `proposed_start`
* `received_by`
* `received_representing`
* `reference_item_id`
* `register`
* `remove_field`
* `sender`
* `sensitivity`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class Account
(primary_smtp_address,fullname=None,access_type=None,autodiscover=False,credentials=None,config=None,locale=None,default_timezone=None)
```

Expand source code
```
class Account:
"""Models an Exchange server user account."""

def __init__(
self,
primary_smtp_address,
fullname=None,
access_type=None,
autodiscover=False,
credentials=None,
config=None,
locale=None,
default_timezone=None,
):
"""

:param primary_smtp_address: The primary email address associated with the account on the Exchange server
:param fullname: The full name of the account. Optional. (Default value = None)
:param access_type: The access type granted to 'credentials' for this account. Valid options are 'delegate'
and 'impersonation'. 'delegate' is default if 'credentials' is set. Otherwise, 'impersonation' is default.
:param autodiscover: Whether to look up the EWS endpoint automatically using the autodiscover protocol.
(Default value = False)
:param credentials: A Credentials object containing valid credentials for this account. (Default value = None)
:param config: A Configuration object containing EWS endpoint information. Required if autodiscover is disabled
(Default value = None)
:param locale: The locale of the user, e.g. 'en_US'. Defaults to the locale of the host, if available.
:param default_timezone: EWS may return some datetime values without timezone information. In this case, we will
assume values to be in the provided timezone. Defaults to the timezone of the host.
:return:
"""
if "@" not in primary_smtp_address:
raise ValueError(f"primary_smtp_address {primary_smtp_address!r} is not an email address")
self.fullname = fullname
# Assume delegate access if individual credentials are provided. Else, assume service user with impersonation
self.access_type = access_type or (DELEGATE if credentials else IMPERSONATION)
if self.access_type not in ACCESS_TYPES:
raise InvalidEnumValue("access_type", self.access_type, ACCESS_TYPES)
try:
# get_locale() might not be able to determine the locale
self.locale = locale or stdlib_locale.getlocale()[0] or None
except ValueError as e:
# getlocale() may throw ValueError if it fails to parse the system locale
log.warning("Failed to get locale (%s)", e)
self.locale = None
if not isinstance(self.locale, (type(None), str)):
raise InvalidTypeError("locale", self.locale, str)
if default_timezone:
try:
self.default_timezone = EWSTimeZone.from_timezone(default_timezone)
except TypeError:
raise InvalidTypeError("default_timezone", default_timezone, EWSTimeZone)
else:
try:
self.default_timezone = EWSTimeZone.localzone()
except (ValueError, UnknownTimeZone) as e:
# There is no translation from local timezone name to Windows timezone name, or e failed to find the
# local timezone.
log.warning("%s. Fallback to UTC", e.args[0])
self.default_timezone = UTC
if not isinstance(config, (Configuration, type(None))):
raise InvalidTypeError("config", config, Configuration)
if autodiscover:
if config:
auth_type, retry_policy, version, max_connections = (
config.auth_type,
config.retry_policy,
config.version,
config.max_connections,
)
if not credentials:
credentials = config.credentials
else:
auth_type, retry_policy, version, max_connections = None, None, None, None
self.ad_response, self.protocol = Autodiscovery(
email=primary_smtp_address, credentials=credentials
).discover()
# Let's not use the auth_package hint from the AD response. It could be incorrect and we can just guess.
self.protocol.config.auth_type = auth_type
if retry_policy:
self.protocol.config.retry_policy = retry_policy
if version:
self.protocol.config.version = version
self.protocol.max_connections = max_connections
primary_smtp_address = self.ad_response.autodiscover_smtp_address
else:
if not config:
raise AttributeError("non-autodiscover requires a config")
self.ad_response = None
self.protocol = Protocol(config=config)

# Other ways of identifying the account can be added later
self.identity = Identity(primary_smtp_address=primary_smtp_address)

# For maintaining affinity in e.g. subscriptions
self.affinity_cookie = None

self._version = None
self._version_lock = Lock()
log.debug("Added account: %s", self)

@property
def primary_smtp_address(self):
return self.identity.primary_smtp_address

@property
def version(self):
# We may need to override the default server version on a per-account basis because Microsoft may report one
# server version up-front but delegate account requests to an older backend server. Create a new instance to
# avoid changing the protocol version instance.
if self._version:
return self._version
with self._version_lock:
if self._version:
return self._version
self._version = self.protocol.version.copy()
return self._version

@version.setter
def version(self, value):
with self._version_lock:
self._version = value

@threaded_cached_property
def admin_audit_logs(self):
return self.root.get_default_folder(AdminAuditLogs)

@threaded_cached_property
def archive_deleted_items(self):
return self.archive_root.get_default_folder(ArchiveDeletedItems)

@threaded_cached_property
def archive_inbox(self):
return self.archive_root.get_default_folder(ArchiveInbox)

@threaded_cached_property
def archive_msg_folder_root(self):
return self.archive_root.get_default_folder(ArchiveMsgFolderRoot)

@threaded_cached_property
def archive_recoverable_items_deletions(self):
return self.archive_root.get_default_folder(ArchiveRecoverableItemsDeletions)

@threaded_cached_property
def archive_recoverable_items_purges(self):
return self.archive_root.get_default_folder(ArchiveRecoverableItemsPurges)

@threaded_cached_property
def archive_recoverable_items_root(self):
return self.archive_root.get_default_folder(ArchiveRecoverableItemsRoot)

@threaded_cached_property
def archive_recoverable_items_versions(self):
return self.archive_root.get_default_folder(ArchiveRecoverableItemsVersions)

@threaded_cached_property
def archive_root(self):
return ArchiveRoot.get_distinguished(account=self)

@threaded_cached_property
def calendar(self):
# If the account contains a shared calendar from a different user, that calendar will be in the folder list.
# Attempt not to return one of those. An account may not always have a calendar called "Calendar", but a
# Calendar folder with a localized name instead. Return that, if it's available, but always prefer any
# distinguished folder returned by the server.
return self.root.get_default_folder(Calendar)

@threaded_cached_property
def conflicts(self):
return self.root.get_default_folder(Conflicts)

@threaded_cached_property
def contacts(self):
return self.root.get_default_folder(Contacts)

@threaded_cached_property
def conversation_history(self):
return self.root.get_default_folder(ConversationHistory)

@threaded_cached_property
def directory(self):
return self.root.get_default_folder(Directory)

@threaded_cached_property
def drafts(self):
return self.root.get_default_folder(Drafts)

@threaded_cached_property
def favorites(self):
return self.root.get_default_folder(Favorites)

@threaded_cached_property
def im_contact_list(self):
return self.root.get_default_folder(IMContactList)

@threaded_cached_property
def inbox(self):
return self.root.get_default_folder(Inbox)

@threaded_cached_property
def journal(self):
return self.root.get_default_folder(Journal)

@threaded_cached_property
def junk(self):
return self.root.get_default_folder(JunkEmail)

@threaded_cached_property
def local_failures(self):
return self.root.get_default_folder(LocalFailures)

@threaded_cached_property
def msg_folder_root(self):
return self.root.get_default_folder(MsgFolderRoot)

@threaded_cached_property
def my_contacts(self):
return self.root.get_default_folder(MyContacts)

@threaded_cached_property
def notes(self):
return self.root.get_default_folder(Notes)

@threaded_cached_property
def outbox(self):
return self.root.get_default_folder(Outbox)

@threaded_cached_property
def people_connect(self):
return self.root.get_default_folder(PeopleConnect)

@threaded_cached_property
def public_folders_root(self):
return PublicFoldersRoot.get_distinguished(account=self)

@threaded_cached_property
def quick_contacts(self):
return self.root.get_default_folder(QuickContacts)

@threaded_cached_property
def recipient_cache(self):
return self.root.get_default_folder(RecipientCache)

@threaded_cached_property
def recoverable_items_deletions(self):
return self.root.get_default_folder(RecoverableItemsDeletions)

@threaded_cached_property
def recoverable_items_purges(self):
return self.root.get_default_folder(RecoverableItemsPurges)

@threaded_cached_property
def recoverable_items_root(self):
return self.root.get_default_folder(RecoverableItemsRoot)

@threaded_cached_property
def recoverable_items_versions(self):
return self.root.get_default_folder(RecoverableItemsVersions)

@threaded_cached_property
def root(self):
return Root.get_distinguished(account=self)

@threaded_cached_property
def search_folders(self):
return self.root.get_default_folder(SearchFolders)

@threaded_cached_property
def sent(self):
return self.root.get_default_folder(SentItems)

@threaded_cached_property
def server_failures(self):
return self.root.get_default_folder(ServerFailures)

@threaded_cached_property
def sync_issues(self):
return self.root.get_default_folder(SyncIssues)

@threaded_cached_property
def tasks(self):
return self.root.get_default_folder(Tasks)

@threaded_cached_property
def todo_search(self):
return self.root.get_default_folder(ToDoSearch)

@threaded_cached_property
def trash(self):
return self.root.get_default_folder(DeletedItems)

@threaded_cached_property
def voice_mail(self):
return self.root.get_default_folder(VoiceMail)

@property
def domain(self):
return get_domain(self.primary_smtp_address)

@property
def oof_settings(self):
# We don't want to cache this property because then we can't easily get updates. 'threaded_cached_property'
# supports the 'del self.oof_settings' syntax to invalidate the cache, but does not support custom setter
# methods. Having a non-cached service call here goes against the assumption that properties are cheap, but the
# alternative is to create get_oof_settings() and set_oof_settings(), and that's just too Java-ish for my taste.
return GetUserOofSettings(account=self).get(
mailbox=Mailbox(email_address=self.primary_smtp_address),
)

@oof_settings.setter
def oof_settings(self, value):
SetUserOofSettings(account=self).get(
oof_settings=value,
mailbox=Mailbox(email_address=self.primary_smtp_address),
)

def _consume_item_service(self, service_cls, items, chunk_size, kwargs):
if isinstance(items, QuerySet):
# We just want an iterator over the results
items = iter(items)
is_empty, items = peek(items)
if is_empty:
# We accept generators, so it's not always convenient for caller to know up-front if 'ids' is empty. Allow
# empty 'ids' and return early.
return
kwargs["items"] = items
yield from service_cls(account=self, chunk_size=chunk_size).call(**kwargs)

def export(self, items, chunk_size=None):
"""Return export strings of the given items.

:param items: An iterable containing the Items we want to export
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of strings, the exported representation of the object
"""
return list(self._consume_item_service(service_cls=ExportItems, items=items, chunk_size=chunk_size, kwargs={}))

def upload(self, data, chunk_size=None):
"""Upload objects retrieved from an export to the given folders.

:param data: An iterable of tuples containing the folder we want to upload the data to and the string outputs of
exports. If you want to update items instead of create, the data must be a tuple of
(ItemId, is_associated, data) values.
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of tuples with the new ids and changekeys

Example:
account.upload([
(account.inbox, "AABBCC..."),
(account.inbox, (ItemId('AA', 'BB'), False, "XXYYZZ...")),
(account.inbox, (('CC', 'DD'), None, "XXYYZZ...")),
(account.calendar, "ABCXYZ..."),
])
-> [("idA", "changekey"), ("idB", "changekey"), ("idC", "changekey")]
"""
items = ((f, (None, False, d) if isinstance(d, str) else d) for f, d in data)
return list(self._consume_item_service(service_cls=UploadItems, items=items, chunk_size=chunk_size, kwargs={}))

def bulk_create(
self, folder, items, message_disposition=SAVE_ONLY, send_meeting_invitations=SEND_TO_NONE, chunk_size=None
):
"""Create new items in 'folder'.

:param folder: the folder to create the items in
:param items: an iterable of Item objects
:param message_disposition: only applicable to Message items. Possible values are specified in
MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY)
:param send_meeting_invitations: only applicable to CalendarItem items. Possible values are specified in
SEND_MEETING_INVITATIONS_CHOICES (Default value = SEND_TO_NONE)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either BulkCreateResult or exception instances in the same order as the input. The returned
BulkCreateResult objects are normal Item objects except they only contain the 'id' and 'changekey'
of the created item, and the 'id' of any attachments that were also created.
"""
if isinstance(items, QuerySet):
# bulk_create() on a queryset does not make sense because it returns items that have already been created
raise ValueError("Cannot bulk create items from a QuerySet")
log.debug(
"Adding items for %s (folder %s, message_disposition: %s, send_meeting_invitations: %s)",
self,
folder,
message_disposition,
send_meeting_invitations,
)
return list(
self._consume_item_service(
service_cls=CreateItem,
items=items,
chunk_size=chunk_size,
kwargs=dict(
folder=folder,
message_disposition=message_disposition,
send_meeting_invitations=send_meeting_invitations,
),
)
)

def bulk_update(
self,
items,
conflict_resolution=AUTO_RESOLVE,
message_disposition=SAVE_ONLY,
send_meeting_invitations_or_cancellations=SEND_TO_NONE,
suppress_read_receipts=True,
chunk_size=None,
):
"""Bulk update existing items.

:param items: a list of (Item, fieldnames) tuples, where 'Item' is an Item object, and 'fieldnames' is a list
containing the attributes on this Item object that we want to be updated.
:param conflict_resolution: Possible values are specified in CONFLICT_RESOLUTION_CHOICES
(Default value = AUTO_RESOLVE)
:param message_disposition: only applicable to Message items. Possible values are specified in
MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY)
:param send_meeting_invitations_or_cancellations: only applicable to CalendarItem items. Possible values are
specified in SEND_MEETING_INVITATIONS_AND_CANCELLATIONS_CHOICES (Default value = SEND_TO_NONE)
:param suppress_read_receipts: nly supported from Exchange 2013. True or False (Default value = True)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either (id, changekey) tuples or exception instances, in the same order as the input
"""
# bulk_update() on a queryset does not make sense because there would be no opportunity to alter the items. In
# fact, it could be dangerous if the queryset contains an '.only()'. This would wipe out certain fields
# entirely.
if isinstance(items, QuerySet):
raise ValueError("Cannot bulk update on a queryset")
log.debug(
"Updating items for %s (conflict_resolution %s, message_disposition: %s, send_meeting_invitations: %s)",
self,
conflict_resolution,
message_disposition,
send_meeting_invitations_or_cancellations,
)
return list(
self._consume_item_service(
service_cls=UpdateItem,
items=items,
chunk_size=chunk_size,
kwargs=dict(
conflict_resolution=conflict_resolution,
message_disposition=message_disposition,
send_meeting_invitations_or_cancellations=send_meeting_invitations_or_cancellations,
suppress_read_receipts=suppress_read_receipts,
),
)
)

def bulk_delete(
self,
ids,
delete_type=HARD_DELETE,
send_meeting_cancellations=SEND_TO_NONE,
affected_task_occurrences=ALL_OCCURRENCES,
suppress_read_receipts=True,
chunk_size=None,
):
"""Bulk delete items.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param delete_type: the type of delete to perform. Possible values are specified in DELETE_TYPE_CHOICES
(Default value = HARD_DELETE)
:param send_meeting_cancellations: only applicable to CalendarItem. Possible values are specified in
SEND_MEETING_CANCELLATIONS_CHOICES. (Default value = SEND_TO_NONE)
:param affected_task_occurrences: only applicable for recurring Task items. Possible values are specified in
AFFECTED_TASK_OCCURRENCES_CHOICES. (Default value = ALL_OCCURRENCES)
:param suppress_read_receipts: only supported from Exchange 2013. True or False. (Default value = True)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either True or exception instances, in the same order as the input
"""
log.debug(
"Deleting items for %s (delete_type: %s, send_meeting_invitations: %s, affected_task_occurrences: %s)",
self,
delete_type,
send_meeting_cancellations,
affected_task_occurrences,
)
return list(
self._consume_item_service(
service_cls=DeleteItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
delete_type=delete_type,
send_meeting_cancellations=send_meeting_cancellations,
affected_task_occurrences=affected_task_occurrences,
suppress_read_receipts=suppress_read_receipts,
),
)
)

def bulk_send(self, ids, save_copy=True, copy_to_folder=None, chunk_size=None):
"""Send existing draft messages. If requested, save a copy in 'copy_to_folder'.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param save_copy: If true, saves a copy of the message (Default value = True)
:param copy_to_folder: If requested, save a copy of the message in this folder. Default is the Sent folder
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input
"""
if copy_to_folder and not save_copy:
raise AttributeError("'save_copy' must be True when 'copy_to_folder' is set")
if save_copy and not copy_to_folder:
copy_to_folder = self.sent # 'Sent' is default EWS behaviour
return list(
self._consume_item_service(
service_cls=SendItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
saved_item_folder=copy_to_folder,
),
)
)

def bulk_copy(self, ids, to_folder, chunk_size=None):
"""Copy items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the copy operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input
"""
return list(
self._consume_item_service(
service_cls=CopyItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)

def bulk_move(self, ids, to_folder, chunk_size=None):
"""Move items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the copy operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: The new IDs of the moved items, in the same order as the input. If 'to_folder' is a public folder or a
folder in a different mailbox, an empty list is returned.
"""
return list(
self._consume_item_service(
service_cls=MoveItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)

def bulk_archive(self, ids, to_folder, chunk_size=None):
"""Archive items to a folder in the archive mailbox. An archive mailbox must be enabled in order for this
to work.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the archive operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing True or an exception instance in stable order of the requested items
"""
return list(
self._consume_item_service(
service_cls=ArchiveItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)

def bulk_mark_as_junk(self, ids, is_junk, move_item, chunk_size=None):
"""Mark or un-mark message items as junk email and add or remove the sender from the blocked sender list.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param is_junk: Whether the messages are junk or not
:param move_item: Whether to move the messages to the junk folder or not
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing the new IDs of the moved items, if items were moved, or True, or an exception
instance, in stable order of the requested items.
"""
return list(
self._consume_item_service(
service_cls=MarkAsJunk,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
is_junk=is_junk,
move_item=move_item,
),
)
)

def fetch(self, ids, folder=None, only_fields=None, chunk_size=None):
"""Fetch items by ID.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param folder: used for validating 'only_fields' (Default value = None)
:param only_fields: A list of string or FieldPath items specifying the fields to fetch. Default to all fields
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A generator of Item objects, in the same order as the input
"""
validation_folder = folder or Folder(root=self.root) # Default to a folder type that supports all item types
# 'ids' could be an unevaluated QuerySet, e.g. if we ended up here via `fetch(ids=some_folder.filter(...))`. In
# that case, we want to use its iterator. Otherwise, peek() will start a count() which is wasteful because we
# need the item IDs immediately afterwards. iterator() will only do the bare minimum.
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {
FieldPath(field=f) for f in validation_folder.allowed_item_fields(version=self.version)
}
else:
for field in only_fields:
validation_folder.validate_item_field(field=field, version=self.version)
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields = {
f for f in validation_folder.normalize_fields(fields=only_fields) if not f.field.is_attribute
}
# Always use IdOnly here, because AllProperties doesn't actually get *all* properties
yield from self._consume_item_service(
service_cls=GetItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
additional_fields=additional_fields,
shape=ID_ONLY,
),
)

def fetch_personas(self, ids):
"""Fetch personas by ID.

:param ids: an iterable of either (id, changekey) tuples or Persona objects.
:return: A generator of Persona objects, in the same order as the input
"""
if isinstance(ids, QuerySet):
# We just want an iterator over the results
ids = iter(ids)
is_empty, ids = peek(ids)
if is_empty:
# We accept generators, so it's not always convenient for caller to know up-front if 'ids' is empty. Allow
# empty 'ids' and return early.
return
yield from GetPersona(account=self).call(personas=ids)

@property
def mail_tips(self):
"""See self.oof_settings about caching considerations."""
return GetMailTips(protocol=self.protocol).get(
sending_as=SendingAs(email_address=self.primary_smtp_address),
recipients=[Mailbox(email_address=self.primary_smtp_address)],
mail_tips_requested="All",
)

@property
def delegates(self):
"""Return a list of DelegateUser objects representing the delegates that are set on this account."""
return list(GetDelegate(account=self).call(user_ids=None, include_permissions=True))

@property
def rules(self):
"""Return a list of Rule objects representing the rules that are set on this account."""
return list(GetInboxRules(account=self).call())

def create_rule(self, rule: Rule):
"""Create an Inbox rule.

:param rule: The rule to create. Must have at least 'display_name' set.
:return: None if success, else raises an error.
"""
CreateInboxRule(account=self).get(rule=rule, remove_outlook_rule_blob=True)
# After creating the rule, query all rules,
# find the rule that was just created, and return its ID.
try:
rule.id = {i.display_name: i for i in GetInboxRules(account=self).call()}[rule.display_name].id
except KeyError:
raise ResponseMessageError(f"Failed to create rule ({rule.display_name})!")

def set_rule(self, rule: Rule):
"""Modify an Inbox rule.

:param rule: The rule to set. Must have an ID.
:return: None if success, else raises an error.
"""
SetInboxRule(account=self).get(rule=rule)

def delete_rule(self, rule: Rule):
"""Delete an Inbox rule.

:param rule: The rule to delete. Must have an ID.
:return: None if success, else raises an error.
"""
if not rule.id:
raise ValueError("Rule must have an ID")
DeleteInboxRule(account=self).get(rule=rule)
rule.id = None

def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60):
"""Create a pull subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPull.EVENT_TYPES
:param watermark: An event bookmark as returned by some sync services
:param timeout: Timeout of the subscription, in minutes. Timeout is reset when the server receives a
GetEvents request for this subscription.
:return: The subscription ID and a watermark
"""
if event_types is None:
event_types = SubscribeToPull.EVENT_TYPES
return SubscribeToPull(account=self).get(
folders=None,
event_types=event_types,
watermark=watermark,
timeout=timeout,
)

def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1):
"""Create a push subscription.

:param callback_url: A client-defined URL that the server will call
:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES
:param watermark: An event bookmark as returned by some sync services
:param status_frequency: The frequency, in minutes, that the callback URL will be called with.
:return: The subscription ID and a watermark
"""
if event_types is None:
event_types = SubscribeToPush.EVENT_TYPES
return SubscribeToPush(account=self).get(
folders=None,
event_types=event_types,
watermark=watermark,
status_frequency=status_frequency,
url=callback_url,
)

def subscribe_to_streaming(self, event_types=None):
"""Create a streaming subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES
:return: The subscription ID
"""
if event_types is None:
event_types = SubscribeToStreaming.EVENT_TYPES
return SubscribeToStreaming(account=self).get(folders=None, event_types=event_types)

def pull_subscription(self, **kwargs):
return PullSubscription(target=self, **kwargs)

def push_subscription(self, **kwargs):
return PushSubscription(target=self, **kwargs)

def streaming_subscription(self, **kwargs):
return StreamingSubscription(target=self, **kwargs)

def unsubscribe(self, subscription_id):
"""Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming]()
:return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other
sync methods.
"""
return Unsubscribe(account=self).get(subscription_id=subscription_id)

def __getstate__(self):
# The lock cannot be pickled
state = self.__dict__.copy()
del state["_version_lock"]
return state

def __setstate__(self, state):
# Restore the lock
self.__dict__.update(state)
self._version_lock = Lock()

def __str__(self):
if self.fullname:
return f"{self.primary_smtp_address} ({self.fullname})"
return self.primary_smtp_address
```

Models an Exchange server user account.

:param primary_smtp_address: The primary email address associated with the account on the Exchange server :param fullname: The full name of the account. Optional. (Default value = None) :param access_type: The access type granted to 'credentials' for this account. Valid options are 'delegate' and 'impersonation'. 'delegate' is default if 'credentials' is set. Otherwise, 'impersonation' is default. :param autodiscover: Whether to look up the EWS endpoint automatically using the autodiscover protocol. (Default value = False) :param credentials: A Credentials object containing valid credentials for this account. (Default value = None) :param config: A Configuration object containing EWS endpoint information. Required if autodiscover is disabled (Default value = None) :param locale: The locale of the user, e.g. 'en_US'. Defaults to the locale of the host, if available. :param default_timezone: EWS may return some datetime values without timezone information. In this case, we will assume values to be in the provided timezone. Defaults to the timezone of the host. :return:

### Instance variables

`var admin_audit_logs`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_deleted_items`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_inbox`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_msg_folder_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_recoverable_items_deletions`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_recoverable_items_purges`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_recoverable_items_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_recoverable_items_versions`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var archive_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var calendar`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var conflicts`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var contacts`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var conversation_history`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop delegates`

Expand source code
```
@property
def delegates(self):
"""Return a list of DelegateUser objects representing the delegates that are set on this account."""
return list(GetDelegate(account=self).call(user_ids=None, include_permissions=True))
```

Return a list of DelegateUser objects representing the delegates that are set on this account.

`var directory`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop domain`

Expand source code
```
@property
def domain(self):
return get_domain(self.primary_smtp_address)
```

`var drafts`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var favorites`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var im_contact_list`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var inbox`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var journal`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var junk`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var local_failures`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop mail_tips`

Expand source code
```
@property
def mail_tips(self):
"""See self.oof_settings about caching considerations."""
return GetMailTips(protocol=self.protocol).get(
sending_as=SendingAs(email_address=self.primary_smtp_address),
recipients=[Mailbox(email_address=self.primary_smtp_address)],
mail_tips_requested="All",
)
```

See self.oof_settings about caching considerations.

`var msg_folder_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var my_contacts`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var notes`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop oof_settings`

Expand source code
```
@property
def oof_settings(self):
# We don't want to cache this property because then we can't easily get updates. 'threaded_cached_property'
# supports the 'del self.oof_settings' syntax to invalidate the cache, but does not support custom setter
# methods. Having a non-cached service call here goes against the assumption that properties are cheap, but the
# alternative is to create get_oof_settings() and set_oof_settings(), and that's just too Java-ish for my taste.
return GetUserOofSettings(account=self).get(
mailbox=Mailbox(email_address=self.primary_smtp_address),
)
```

`var outbox`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var people_connect`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop primary_smtp_address`

Expand source code
```
@property
def primary_smtp_address(self):
return self.identity.primary_smtp_address
```

`var public_folders_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var quick_contacts`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var recipient_cache`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var recoverable_items_deletions`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var recoverable_items_purges`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var recoverable_items_root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var recoverable_items_versions`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var root`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop rules`

Expand source code
```
@property
def rules(self):
"""Return a list of Rule objects representing the rules that are set on this account."""
return list(GetInboxRules(account=self).call())
```

Return a list of Rule objects representing the rules that are set on this account.

`var search_folders`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var sent`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var server_failures`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var sync_issues`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var tasks`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var todo_search`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`var trash`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop version`

Expand source code
```
@property
def version(self):
# We may need to override the default server version on a per-account basis because Microsoft may report one
# server version up-front but delegate account requests to an older backend server. Create a new instance to
# avoid changing the protocol version instance.
if self._version:
return self._version
with self._version_lock:
if self._version:
return self._version
self._version = self.protocol.version.copy()
return self._version
```

`var voice_mail`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

### Methods

```
def bulk_archive(self, ids, to_folder, chunk_size=None)
```

Expand source code
```
def bulk_archive(self, ids, to_folder, chunk_size=None):
"""Archive items to a folder in the archive mailbox. An archive mailbox must be enabled in order for this
to work.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the archive operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing True or an exception instance in stable order of the requested items
"""
return list(
self._consume_item_service(
service_cls=ArchiveItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)
```

Archive items to a folder in the archive mailbox. An archive mailbox must be enabled in order for this to work.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param to_folder: The destination folder of the archive operation :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing True or an exception instance in stable order of the requested items

```
def bulk_copy(self, ids, to_folder, chunk_size=None)
```

Expand source code
```
def bulk_copy(self, ids, to_folder, chunk_size=None):
"""Copy items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the copy operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input
"""
return list(
self._consume_item_service(
service_cls=CopyItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)
```

Copy items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param to_folder: The destination folder of the copy operation :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input

```
def bulk_create(self,folder,items,message_disposition='SaveOnly',send_meeting_invitations='SendToNone',chunk_size=None)
```

Expand source code
```
def bulk_create(
self, folder, items, message_disposition=SAVE_ONLY, send_meeting_invitations=SEND_TO_NONE, chunk_size=None
):
"""Create new items in 'folder'.

:param folder: the folder to create the items in
:param items: an iterable of Item objects
:param message_disposition: only applicable to Message items. Possible values are specified in
MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY)
:param send_meeting_invitations: only applicable to CalendarItem items. Possible values are specified in
SEND_MEETING_INVITATIONS_CHOICES (Default value = SEND_TO_NONE)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either BulkCreateResult or exception instances in the same order as the input. The returned
BulkCreateResult objects are normal Item objects except they only contain the 'id' and 'changekey'
of the created item, and the 'id' of any attachments that were also created.
"""
if isinstance(items, QuerySet):
# bulk_create() on a queryset does not make sense because it returns items that have already been created
raise ValueError("Cannot bulk create items from a QuerySet")
log.debug(
"Adding items for %s (folder %s, message_disposition: %s, send_meeting_invitations: %s)",
self,
folder,
message_disposition,
send_meeting_invitations,
)
return list(
self._consume_item_service(
service_cls=CreateItem,
items=items,
chunk_size=chunk_size,
kwargs=dict(
folder=folder,
message_disposition=message_disposition,
send_meeting_invitations=send_meeting_invitations,
),
)
)
```

Create new items in 'folder'.

:param folder: the folder to create the items in :param items: an iterable of Item objects :param message_disposition: only applicable to Message items. Possible values are specified in MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY) :param send_meeting_invitations: only applicable to CalendarItem items. Possible values are specified in SEND_MEETING_INVITATIONS_CHOICES (Default value = SEND_TO_NONE) :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either BulkCreateResult or exception instances in the same order as the input. The returned BulkCreateResult objects are normal Item objects except they only contain the 'id' and 'changekey' of the created item, and the 'id' of any attachments that were also created.

```
def bulk_delete(self,ids,delete_type='HardDelete',send_meeting_cancellations='SendToNone',affected_task_occurrences='AllOccurrences',suppress_read_receipts=True,chunk_size=None)
```

Expand source code
```
def bulk_delete(
self,
ids,
delete_type=HARD_DELETE,
send_meeting_cancellations=SEND_TO_NONE,
affected_task_occurrences=ALL_OCCURRENCES,
suppress_read_receipts=True,
chunk_size=None,
):
"""Bulk delete items.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param delete_type: the type of delete to perform. Possible values are specified in DELETE_TYPE_CHOICES
(Default value = HARD_DELETE)
:param send_meeting_cancellations: only applicable to CalendarItem. Possible values are specified in
SEND_MEETING_CANCELLATIONS_CHOICES. (Default value = SEND_TO_NONE)
:param affected_task_occurrences: only applicable for recurring Task items. Possible values are specified in
AFFECTED_TASK_OCCURRENCES_CHOICES. (Default value = ALL_OCCURRENCES)
:param suppress_read_receipts: only supported from Exchange 2013. True or False. (Default value = True)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either True or exception instances, in the same order as the input
"""
log.debug(
"Deleting items for %s (delete_type: %s, send_meeting_invitations: %s, affected_task_occurrences: %s)",
self,
delete_type,
send_meeting_cancellations,
affected_task_occurrences,
)
return list(
self._consume_item_service(
service_cls=DeleteItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
delete_type=delete_type,
send_meeting_cancellations=send_meeting_cancellations,
affected_task_occurrences=affected_task_occurrences,
suppress_read_receipts=suppress_read_receipts,
),
)
)
```

Bulk delete items.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param delete_type: the type of delete to perform. Possible values are specified in DELETE_TYPE_CHOICES (Default value = HARD_DELETE) :param send_meeting_cancellations: only applicable to CalendarItem. Possible values are specified in SEND_MEETING_CANCELLATIONS_CHOICES. (Default value = SEND_TO_NONE) :param affected_task_occurrences: only applicable for recurring Task items. Possible values are specified in AFFECTED_TASK_OCCURRENCES_CHOICES. (Default value = ALL_OCCURRENCES) :param suppress_read_receipts: only supported from Exchange 2013. True or False. (Default value = True) :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either True or exception instances, in the same order as the input

```
def bulk_mark_as_junk(self, ids, is_junk, move_item, chunk_size=None)
```

Expand source code
```
def bulk_mark_as_junk(self, ids, is_junk, move_item, chunk_size=None):
"""Mark or un-mark message items as junk email and add or remove the sender from the blocked sender list.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param is_junk: Whether the messages are junk or not
:param move_item: Whether to move the messages to the junk folder or not
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing the new IDs of the moved items, if items were moved, or True, or an exception
instance, in stable order of the requested items.
"""
return list(
self._consume_item_service(
service_cls=MarkAsJunk,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
is_junk=is_junk,
move_item=move_item,
),
)
)
```

Mark or un-mark message items as junk email and add or remove the sender from the blocked sender list.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param is_junk: Whether the messages are junk or not :param move_item: Whether to move the messages to the junk folder or not :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list containing the new IDs of the moved items, if items were moved, or True, or an exception instance, in stable order of the requested items.

```
def bulk_move(self, ids, to_folder, chunk_size=None)
```

Expand source code
```
def bulk_move(self, ids, to_folder, chunk_size=None):
"""Move items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param to_folder: The destination folder of the copy operation
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: The new IDs of the moved items, in the same order as the input. If 'to_folder' is a public folder or a
folder in a different mailbox, an empty list is returned.
"""
return list(
self._consume_item_service(
service_cls=MoveItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
to_folder=to_folder,
),
)
)
```

Move items to another folder.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param to_folder: The destination folder of the copy operation :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: The new IDs of the moved items, in the same order as the input. If 'to_folder' is a public folder or a folder in a different mailbox, an empty list is returned.

```
def bulk_send(self, ids, save_copy=True, copy_to_folder=None, chunk_size=None)
```

Expand source code
```
def bulk_send(self, ids, save_copy=True, copy_to_folder=None, chunk_size=None):
"""Send existing draft messages. If requested, save a copy in 'copy_to_folder'.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param save_copy: If true, saves a copy of the message (Default value = True)
:param copy_to_folder: If requested, save a copy of the message in this folder. Default is the Sent folder
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input
"""
if copy_to_folder and not save_copy:
raise AttributeError("'save_copy' must be True when 'copy_to_folder' is set")
if save_copy and not copy_to_folder:
copy_to_folder = self.sent # 'Sent' is default EWS behaviour
return list(
self._consume_item_service(
service_cls=SendItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
saved_item_folder=copy_to_folder,
),
)
)
```

Send existing draft messages. If requested, save a copy in 'copy_to_folder'.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param save_copy: If true, saves a copy of the message (Default value = True) :param copy_to_folder: If requested, save a copy of the message in this folder. Default is the Sent folder :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: Status for each send operation, in the same order as the input

```
def bulk_update(self,items,conflict_resolution='AutoResolve',message_disposition='SaveOnly',send_meeting_invitations_or_cancellations='SendToNone',suppress_read_receipts=True,chunk_size=None)
```

Expand source code
```
def bulk_update(
self,
items,
conflict_resolution=AUTO_RESOLVE,
message_disposition=SAVE_ONLY,
send_meeting_invitations_or_cancellations=SEND_TO_NONE,
suppress_read_receipts=True,
chunk_size=None,
):
"""Bulk update existing items.

:param items: a list of (Item, fieldnames) tuples, where 'Item' is an Item object, and 'fieldnames' is a list
containing the attributes on this Item object that we want to be updated.
:param conflict_resolution: Possible values are specified in CONFLICT_RESOLUTION_CHOICES
(Default value = AUTO_RESOLVE)
:param message_disposition: only applicable to Message items. Possible values are specified in
MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY)
:param send_meeting_invitations_or_cancellations: only applicable to CalendarItem items. Possible values are
specified in SEND_MEETING_INVITATIONS_AND_CANCELLATIONS_CHOICES (Default value = SEND_TO_NONE)
:param suppress_read_receipts: nly supported from Exchange 2013. True or False (Default value = True)
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either (id, changekey) tuples or exception instances, in the same order as the input
"""
# bulk_update() on a queryset does not make sense because there would be no opportunity to alter the items. In
# fact, it could be dangerous if the queryset contains an '.only()'. This would wipe out certain fields
# entirely.
if isinstance(items, QuerySet):
raise ValueError("Cannot bulk update on a queryset")
log.debug(
"Updating items for %s (conflict_resolution %s, message_disposition: %s, send_meeting_invitations: %s)",
self,
conflict_resolution,
message_disposition,
send_meeting_invitations_or_cancellations,
)
return list(
self._consume_item_service(
service_cls=UpdateItem,
items=items,
chunk_size=chunk_size,
kwargs=dict(
conflict_resolution=conflict_resolution,
message_disposition=message_disposition,
send_meeting_invitations_or_cancellations=send_meeting_invitations_or_cancellations,
suppress_read_receipts=suppress_read_receipts,
),
)
)
```

Bulk update existing items.

:param items: a list of (Item, fieldnames) tuples, where 'Item' is an Item object, and 'fieldnames' is a list containing the attributes on this Item object that we want to be updated. :param conflict_resolution: Possible values are specified in CONFLICT_RESOLUTION_CHOICES (Default value = AUTO_RESOLVE) :param message_disposition: only applicable to Message items. Possible values are specified in MESSAGE_DISPOSITION_CHOICES (Default value = SAVE_ONLY) :param send_meeting_invitations_or_cancellations: only applicable to CalendarItem items. Possible values are specified in SEND_MEETING_INVITATIONS_AND_CANCELLATIONS_CHOICES (Default value = SEND_TO_NONE) :param suppress_read_receipts: nly supported from Exchange 2013. True or False (Default value = True) :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: a list of either (id, changekey) tuples or exception instances, in the same order as the input

```
def create_rule(self,rule: Rule)
```

Expand source code
```
def create_rule(self, rule: Rule):
"""Create an Inbox rule.

:param rule: The rule to create. Must have at least 'display_name' set.
:return: None if success, else raises an error.
"""
CreateInboxRule(account=self).get(rule=rule, remove_outlook_rule_blob=True)
# After creating the rule, query all rules,
# find the rule that was just created, and return its ID.
try:
rule.id = {i.display_name: i for i in GetInboxRules(account=self).call()}[rule.display_name].id
except KeyError:
raise ResponseMessageError(f"Failed to create rule ({rule.display_name})!")
```

Create an Inbox rule.

:param rule: The rule to create. Must have at least 'display_name' set. :return: None if success, else raises an error.

```
def delete_rule(self,rule: Rule)
```

Expand source code
```
def delete_rule(self, rule: Rule):
"""Delete an Inbox rule.

:param rule: The rule to delete. Must have an ID.
:return: None if success, else raises an error.
"""
if not rule.id:
raise ValueError("Rule must have an ID")
DeleteInboxRule(account=self).get(rule=rule)
rule.id = None
```

Delete an Inbox rule.

:param rule: The rule to delete. Must have an ID. :return: None if success, else raises an error.

```
def export(self, items, chunk_size=None)
```

Expand source code
```
def export(self, items, chunk_size=None):
"""Return export strings of the given items.

:param items: An iterable containing the Items we want to export
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of strings, the exported representation of the object
"""
return list(self._consume_item_service(service_cls=ExportItems, items=items, chunk_size=chunk_size, kwargs={}))
```

Return export strings of the given items.

:param items: An iterable containing the Items we want to export :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of strings, the exported representation of the object

```
def fetch(self, ids, folder=None, only_fields=None, chunk_size=None)
```

Expand source code
```
def fetch(self, ids, folder=None, only_fields=None, chunk_size=None):
"""Fetch items by ID.

:param ids: an iterable of either (id, changekey) tuples or Item objects.
:param folder: used for validating 'only_fields' (Default value = None)
:param only_fields: A list of string or FieldPath items specifying the fields to fetch. Default to all fields
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A generator of Item objects, in the same order as the input
"""
validation_folder = folder or Folder(root=self.root) # Default to a folder type that supports all item types
# 'ids' could be an unevaluated QuerySet, e.g. if we ended up here via `fetch(ids=some_folder.filter(...))`. In
# that case, we want to use its iterator. Otherwise, peek() will start a count() which is wasteful because we
# need the item IDs immediately afterwards. iterator() will only do the bare minimum.
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {
FieldPath(field=f) for f in validation_folder.allowed_item_fields(version=self.version)
}
else:
for field in only_fields:
validation_folder.validate_item_field(field=field, version=self.version)
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields = {
f for f in validation_folder.normalize_fields(fields=only_fields) if not f.field.is_attribute
}
# Always use IdOnly here, because AllProperties doesn't actually get *all* properties
yield from self._consume_item_service(
service_cls=GetItem,
items=ids,
chunk_size=chunk_size,
kwargs=dict(
additional_fields=additional_fields,
shape=ID_ONLY,
),
)
```

Fetch items by ID.

:param ids: an iterable of either (id, changekey) tuples or Item objects. :param folder: used for validating 'only_fields' (Default value = None) :param only_fields: A list of string or FieldPath items specifying the fields to fetch. Default to all fields :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A generator of Item objects, in the same order as the input

```
def fetch_personas(self, ids)
```

Expand source code
```
def fetch_personas(self, ids):
"""Fetch personas by ID.

:param ids: an iterable of either (id, changekey) tuples or Persona objects.
:return: A generator of Persona objects, in the same order as the input
"""
if isinstance(ids, QuerySet):
# We just want an iterator over the results
ids = iter(ids)
is_empty, ids = peek(ids)
if is_empty:
# We accept generators, so it's not always convenient for caller to know up-front if 'ids' is empty. Allow
# empty 'ids' and return early.
return
yield from GetPersona(account=self).call(personas=ids)
```

Fetch personas by ID.

:param ids: an iterable of either (id, changekey) tuples or Persona objects. :return: A generator of Persona objects, in the same order as the input

```
def pull_subscription(self, **kwargs)
```

Expand source code
```
def pull_subscription(self, **kwargs):
return PullSubscription(target=self, **kwargs)
```

```
def push_subscription(self, **kwargs)
```

Expand source code
```
def push_subscription(self, **kwargs):
return PushSubscription(target=self, **kwargs)
```

```
def set_rule(self,rule: Rule)
```

Expand source code
```
def set_rule(self, rule: Rule):
"""Modify an Inbox rule.

:param rule: The rule to set. Must have an ID.
:return: None if success, else raises an error.
"""
SetInboxRule(account=self).get(rule=rule)
```

Modify an Inbox rule.

:param rule: The rule to set. Must have an ID. :return: None if success, else raises an error.

```
def streaming_subscription(self, **kwargs)
```

Expand source code
```
def streaming_subscription(self, **kwargs):
return StreamingSubscription(target=self, **kwargs)
```

```
def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60)
```

Expand source code
```
def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60):
"""Create a pull subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPull.EVENT_TYPES
:param watermark: An event bookmark as returned by some sync services
:param timeout: Timeout of the subscription, in minutes. Timeout is reset when the server receives a
GetEvents request for this subscription.
:return: The subscription ID and a watermark
"""
if event_types is None:
event_types = SubscribeToPull.EVENT_TYPES
return SubscribeToPull(account=self).get(
folders=None,
event_types=event_types,
watermark=watermark,
timeout=timeout,
)
```

Create a pull subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPull.EVENT_TYPES :param watermark: An event bookmark as returned by some sync services :param timeout: Timeout of the subscription, in minutes. Timeout is reset when the server receives a GetEvents request for this subscription. :return: The subscription ID and a watermark

```
def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1)
```

Expand source code
```
def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1):
"""Create a push subscription.

:param callback_url: A client-defined URL that the server will call
:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES
:param watermark: An event bookmark as returned by some sync services
:param status_frequency: The frequency, in minutes, that the callback URL will be called with.
:return: The subscription ID and a watermark
"""
if event_types is None:
event_types = SubscribeToPush.EVENT_TYPES
return SubscribeToPush(account=self).get(
folders=None,
event_types=event_types,
watermark=watermark,
status_frequency=status_frequency,
url=callback_url,
)
```

Create a push subscription.

:param callback_url: A client-defined URL that the server will call :param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES :param watermark: An event bookmark as returned by some sync services :param status_frequency: The frequency, in minutes, that the callback URL will be called with. :return: The subscription ID and a watermark

```
def subscribe_to_streaming(self, event_types=None)
```

Expand source code
```
def subscribe_to_streaming(self, event_types=None):
"""Create a streaming subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES
:return: The subscription ID
"""
if event_types is None:
event_types = SubscribeToStreaming.EVENT_TYPES
return SubscribeToStreaming(account=self).get(folders=None, event_types=event_types)
```

Create a streaming subscription.

:param event_types: List of event types to subscribe to. Possible values defined in SubscribeToPush.EVENT_TYPES :return: The subscription ID

```
def unsubscribe(self, subscription_id)
```

Expand source code
```
def unsubscribe(self, subscription_id):
"""Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming]()
:return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other
sync methods.
"""
return Unsubscribe(account=self).get(subscription_id=subscription_id)
```

Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming](https://ecederstrand.github.io/exchangelib/exchangelib/) :return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other sync methods.

```
def upload(self, data, chunk_size=None)
```

Expand source code
```
def upload(self, data, chunk_size=None):
"""Upload objects retrieved from an export to the given folders.

:param data: An iterable of tuples containing the folder we want to upload the data to and the string outputs of
exports. If you want to update items instead of create, the data must be a tuple of
(ItemId, is_associated, data) values.
:param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of tuples with the new ids and changekeys

Example:
account.upload([
(account.inbox, "AABBCC..."),
(account.inbox, (ItemId('AA', 'BB'), False, "XXYYZZ...")),
(account.inbox, (('CC', 'DD'), None, "XXYYZZ...")),
(account.calendar, "ABCXYZ..."),
])
-> [("idA", "changekey"), ("idB", "changekey"), ("idC", "changekey")]
"""
items = ((f, (None, False, d) if isinstance(d, str) else d) for f, d in data)
return list(self._consume_item_service(service_cls=UploadItems, items=items, chunk_size=chunk_size, kwargs={}))
```

Upload objects retrieved from an export to the given folders.

:param data: An iterable of tuples containing the folder we want to upload the data to and the string outputs of exports. If you want to update items instead of create, the data must be a tuple of (ItemId, is_associated, data) values. :param chunk_size: The number of items to send to the server in a single request (Default value = None)

:return: A list of tuples with the new ids and changekeys

Example: account.upload([ (account.inbox, "AABBCC…"), (account.inbox, (ItemId('AA', 'BB'), False, "XXYYZZ…")), (account.inbox, (('CC', 'DD'), None, "XXYYZZ…")), (account.calendar, "ABCXYZ…"), ]) -> [("idA", "changekey"), ("idB", "changekey"), ("idC", "changekey")]

```
class Attendee
(**kwargs)
```

Expand source code
```
class Attendee(EWSElement):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/attendee"""

ELEMENT_NAME = "Attendee"
RESPONSE_TYPES = {"Unknown", "Organizer", "Tentative", "Accept", "Decline", "NoResponseReceived"}

mailbox = MailboxField(is_required=True)
response_type = ChoiceField(
field_uri="ResponseType", choices={Choice(c) for c in RESPONSE_TYPES}, default="Unknown"
)
last_response_time = DateTimeField(field_uri="LastResponseTime")
proposed_start = DateTimeField(field_uri="ProposedStart")
proposed_end = DateTimeField(field_uri="ProposedEnd")

def __hash__(self):
return hash(self.mailbox)
```

### Ancestors

* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var RESPONSE_TYPES`
The type of the None singleton.

### Instance variables

`var last_response_time`
The type of the None singleton.

`var mailbox`
The type of the None singleton.

`var proposed_end`
The type of the None singleton.

`var proposed_start`
The type of the None singleton.

`var response_type`
The type of the None singleton.

### Inherited members

* `EWSElement`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class BaseProtocol
(config)
```

Expand source code
```
class BaseProtocol:
"""Base class for Protocol which implements the bare essentials."""

# The maximum number of sessions (== TCP connections, see below) we will open to this service endpoint. Keep this
# low unless you have an agreement with the Exchange admin on the receiving end to hammer the server and
# rate-limiting policies have been disabled for the connecting user. Changing this setting only makes sense if
# you are using threads to run multiple concurrent workers in this process.
SESSION_POOLSIZE = 1
# We want only 1 TCP connection per Session object. We may have lots of different credentials hitting the server and
# each credential needs its own session (NTLM auth will only send credentials once and then secure the connection,
# so a connection can only handle requests for one credential). Having multiple connections per Session could
# quickly exhaust the maximum number of concurrent connections the Exchange server allows from one client.
CONNECTIONS_PER_SESSION = 1
# The number of times a session may be reused before creating a new session object. 'None' means "infinite".
# Discarding sessions after a certain number of usages may limit memory leaks in the Session object.
MAX_SESSION_USAGE_COUNT = None
# Timeout for HTTP requests
TIMEOUT = 120
RETRY_WAIT = 10 # Seconds to wait before retry on connection errors

# The adapter class to use for HTTP requests. Override this if you need e.g. proxy support or specific TLS versions
HTTP_ADAPTER_CLS = requests.adapters.HTTPAdapter

# The User-Agent header to use for HTTP requests. Override this to set an app-specific one
USERAGENT = None

def __init__(self, config):
self.config = config

self._session_pool_size = 0
self._session_pool_maxsize = config.max_connections or self.SESSION_POOLSIZE

# Try to behave nicely with the remote server. We want to keep the connection open between requests.
# We also want to re-use sessions, to avoid the NTLM auth handshake on every request. We must know the
# authentication method to create sessions.
self._session_pool = LifoQueue()
self._session_pool_lock = Lock()

@property
def service_endpoint(self):
return self.config.service_endpoint

@abc.abstractmethod
def get_auth_type(self):
"""Autodetect authentication type"""

@property
def auth_type(self):
# Autodetect authentication type if necessary
if self.config.auth_type is None:
self.config.auth_type = self.get_auth_type()
return self.config.auth_type

@property
def credentials(self):
return self.config.credentials

@credentials.setter
def credentials(self, value):
# We are updating credentials, but that doesn't automatically propagate to the session objects. The simplest
# solution is to just kill the sessions in the pool.
with self._session_pool_lock:
self.config._credentials = value
self.close()

@property
def max_connections(self):
return self._session_pool_maxsize

@max_connections.setter
def max_connections(self, value):
with self._session_pool_lock:
self._session_pool_maxsize = value or self.SESSION_POOLSIZE

@property
def retry_policy(self):
return self.config.retry_policy

@property
def server(self):
return self.config.server

def __getstate__(self):
# The session pool and lock cannot be pickled
state = self.__dict__.copy()
del state["_session_pool"]
del state["_session_pool_lock"]
return state

def __setstate__(self, state):
# Restore the session pool and lock
self.__dict__.update(state)
self._session_pool = LifoQueue()
self._session_pool_lock = Lock()

def __del__(self):
# pylint: disable=bare-except
try:
self.close()
except Exception: # nosec
# __del__ should never fail
pass

def close(self):
log.debug("Server %s: Closing sessions", self.server)
while True:
try:
session = self._session_pool.get(block=False)
self.close_session(session)
self._session_pool_size -= 1
except Empty:
break

@classmethod
def get_adapter(cls):
# We want just one connection per session. No retries, since we wrap all requests in our own retry handler
return cls.HTTP_ADAPTER_CLS(
pool_block=True,
pool_connections=cls.CONNECTIONS_PER_SESSION,
pool_maxsize=cls.CONNECTIONS_PER_SESSION,
max_retries=0,
)

@property
def session_pool_size(self):
return self._session_pool_size

def increase_poolsize(self):
"""Increases the session pool size. We increase by one session per call."""
# Create a single session and insert it into the pool. We need to protect this with a lock while we are changing
# the pool size variable, to avoid race conditions. We must not exceed the pool size limit.
if self._session_pool_size >= self._session_pool_maxsize:
raise SessionPoolMaxSizeReached("Session pool size cannot be increased further")
with self._session_pool_lock:
if self._session_pool_size >= self._session_pool_maxsize:
log.debug("Session pool size was increased in another thread")
return
log.debug(
"Server %s: Increasing session pool size from %s to %s",
self.server,
self._session_pool_size,
self._session_pool_size + 1,
)
self._session_pool.put(self.create_session(), block=False)
self._session_pool_size += 1

def decrease_poolsize(self):
"""Decreases the session pool size in response to error messages from the server requesting to rate-limit
requests. We decrease by one session per call.
"""
# Take a single session from the pool and discard it. We need to protect this with a lock while we are changing
# the pool size variable, to avoid race conditions. We must keep at least one session in the pool.
if self._session_pool_size <= 1:
raise SessionPoolMinSizeReached("Session pool size cannot be decreased further")
with self._session_pool_lock:
if self._session_pool_size <= 1:
log.debug("Session pool size was decreased in another thread")
return
log.warning(
"Server %s: Decreasing session pool size from %s to %s",
self.server,
self._session_pool_size,
self._session_pool_size - 1,
)
session = self.get_session()
self.close_session(session)
self._session_pool_size -= 1

def get_session(self):
# Try to get a session from the queue. If the queue is empty, try to add one more session to the queue. If the
# queue is already at its max, wait until a session becomes available.
_timeout = 60 # Rate-limit messages about session starvation
try:
session = self._session_pool.get(block=False)
log.debug("Server %s: Got session immediately", self.server)
except Empty:
with suppress(SessionPoolMaxSizeReached):
self.increase_poolsize()
while True:
try:
log.debug("Server %s: Waiting for session", self.server)
session = self._session_pool.get(timeout=_timeout)
break
except Empty:
# This is normal when we have many worker threads starving for available sessions
log.debug("Server %s: No sessions available for %s seconds", self.server, _timeout)
log.debug("Server %s: Got session %s", self.server, session.session_id)
session.usage_count += 1
return session

def release_session(self, session):
# This should never fail, as we don't have more sessions than the queue contains
log.debug("Server %s: Releasing session %s", self.server, session.session_id)
if self.MAX_SESSION_USAGE_COUNT and session.usage_count >= self.MAX_SESSION_USAGE_COUNT:
log.debug("Server %s: session %s usage exceeded limit. Discarding", self.server, session.session_id)
session = self.renew_session(session)
self._session_pool.put(session, block=False)

def close_session(self, session):
if isinstance(self.credentials, BaseOAuth2Credentials) and isinstance(
self.credentials.client, BackendApplicationClient
):
# Reset access token
with self.credentials.lock:
self.credentials.access_token = None
session.close()
del session

def retire_session(self, session):
# The session is useless. Close it completely and place a fresh session in the pool
log.debug("Server %s: Retiring session %s", self.server, session.session_id)
self.close_session(session)
self.release_session(self.create_session())

def renew_session(self, session):
# The session is useless. Close it completely and place a fresh session in the pool
log.debug("Server %s: Renewing session %s", self.server, session.session_id)
self.close_session(session)
return self.create_session()

def refresh_credentials(self, session):
# Credentials need to be refreshed, probably due to an OAuth
# access token expiring. If we've gotten here, it's because the
# application didn't provide an OAuth client secret, so we can't
# handle token refreshing for it.
with self.credentials.lock:
if self.credentials.sig() == session.credentials_sig:
# Credentials have not been refreshed by another thread:
# they're the same as the session was created with. If
# this isn't the case, we can just go ahead with a new
# session using the already-updated credentials.
self.credentials.refresh(session=session)
return self.renew_session(session)

def create_session(self):
if self.credentials is None:
if self.auth_type in CREDENTIALS_REQUIRED:
raise ValueError(f"Auth type {self.auth_type!r} requires credentials")
session = self.raw_session(self.service_endpoint)
session.auth = get_auth_instance(auth_type=self.auth_type)
else:
if isinstance(self.credentials, BaseOAuth2Credentials):
with self.credentials.lock:
session = self.create_oauth2_session()
# Keep track of the credentials used to create this session. If and when we need to renew
# credentials (for example, refreshing an OAuth access token), this lets us easily determine whether
# the credentials have already been refreshed in another thread by the time this session tries.
session.credentials_sig = self.credentials.sig()
else:
if self.auth_type == NTLM and self.credentials.type == self.credentials.EMAIL:
username = "\\" + self.credentials.username
else:
username = self.credentials.username
session = self.raw_session(self.service_endpoint)
session.auth = get_auth_instance(
auth_type=self.auth_type, username=username, password=self.credentials.password
)

# Add some extra info
session.session_id = random.randint(10000, 99999) # Used for debugging messages in services
session.usage_count = 0
log.debug("Server %s: Created session %s", self.server, session.session_id)
return session

def create_oauth2_session(self):
session = self.raw_session(
self.service_endpoint,
oauth2_client=self.credentials.client,
oauth2_session_params=self.credentials.session_params(),
oauth2_token_endpoint=self.credentials.token_url,
)
if not session.token:
# Fetch the token explicitly -- it doesn't occur implicitly
token = session.fetch_token(
token_url=self.credentials.token_url,
client_id=self.credentials.client_id,
client_secret=self.credentials.client_secret,
scope=self.credentials.scope,
timeout=self.TIMEOUT,
**self.credentials.token_params(),
)
# Allow the credentials object to update its copy of the new token, and give the application an opportunity
# to cache it.
self.credentials.on_token_auto_refreshed(token)
session.auth = get_auth_instance(auth_type=OAUTH2, client=self.credentials.client)

return session

@classmethod
def raw_session(cls, prefix, oauth2_client=None, oauth2_session_params=None, oauth2_token_endpoint=None):
if oauth2_client:
session = OAuth2Session(client=oauth2_client, **(oauth2_session_params or {}))
else:
session = requests.sessions.Session()
session.headers.update(DEFAULT_HEADERS)
session.headers["User-Agent"] = cls.USERAGENT
session.mount(prefix, adapter=cls.get_adapter())
if oauth2_token_endpoint:
session.mount(oauth2_token_endpoint, adapter=cls.get_adapter())
return session

def __repr__(self):
return self.__class__.__name__ + repr((self.service_endpoint, self.credentials, self.auth_type))
```

Base class for Protocol which implements the bare essentials.

### Subclasses

* [AutodiscoverProtocol](https://ecederstrand.github.io/exchangelib/exchangelib/autodiscover/protocol.html#exchangelib.autodiscover.protocol.AutodiscoverProtocol "exchangelib.autodiscover.protocol.AutodiscoverProtocol")
* [Protocol](https://ecederstrand.github.io/exchangelib/exchangelib/protocol.html#exchangelib.protocol.Protocol "exchangelib.protocol.Protocol")

### Class variables

`var CONNECTIONS_PER_SESSION`
The type of the None singleton.

`var HTTP_ADAPTER_CLS`

The built-in HTTP Adapter for urllib3.

Provides a general-case interface for Requests sessions to contact HTTP and HTTPS urls by implementing the Transport Adapter interface. This class will usually be created by the :class:`Session <Session>` class under the covers.

:param pool_connections: The number of urllib3 connection pools to cache. :param pool_maxsize: The maximum number of connections to save in the pool. :param max_retries: The maximum number of retries each connection should attempt. Note, this applies only to failed DNS lookups, socket connections and connection timeouts, never to requests where data has made it to the server. By default, Requests does not retry failed connections. If you need granular control over the conditions under which we retry a request, import urllib3's `Retry` class and pass that instead. :param pool_block: Whether the connection pool should block for connections.

Usage::

> > > import requests s = requests.Session() a = requests.adapters.HTTPAdapter(max_retries=3) s.mount('http://', a)

`var MAX_SESSION_USAGE_COUNT`
The type of the None singleton.

`var RETRY_WAIT`
The type of the None singleton.

`var SESSION_POOLSIZE`
The type of the None singleton.

`var TIMEOUT`
The type of the None singleton.

`var USERAGENT`
The type of the None singleton.

### Static methods

```
def get_adapter()
```

```
def raw_session(prefix,oauth2_client=None,oauth2_session_params=None,oauth2_token_endpoint=None)
```

### Instance variables

`prop auth_type`

Expand source code
```
@property
def auth_type(self):
# Autodetect authentication type if necessary
if self.config.auth_type is None:
self.config.auth_type = self.get_auth_type()
return self.config.auth_type
```

`prop credentials`

Expand source code
```
@property
def credentials(self):
return self.config.credentials
```

`prop max_connections`

Expand source code
```
@property
def max_connections(self):
return self._session_pool_maxsize
```

`prop retry_policy`

Expand source code
```
@property
def retry_policy(self):
return self.config.retry_policy
```

`prop server`

Expand source code
```
@property
def server(self):
return self.config.server
```

`prop service_endpoint`

Expand source code
```
@property
def service_endpoint(self):
return self.config.service_endpoint
```

`prop session_pool_size`

Expand source code
```
@property
def session_pool_size(self):
return self._session_pool_size
```

### Methods

```
def close(self)
```

Expand source code
```
def close(self):
log.debug("Server %s: Closing sessions", self.server)
while True:
try:
session = self._session_pool.get(block=False)
self.close_session(session)
self._session_pool_size -= 1
except Empty:
break
```

```
def close_session(self, session)
```

Expand source code
```
def close_session(self, session):
if isinstance(self.credentials, BaseOAuth2Credentials) and isinstance(
self.credentials.client, BackendApplicationClient
):
# Reset access token
with self.credentials.lock:
self.credentials.access_token = None
session.close()
del session
```

```
def create_oauth2_session(self)
```

Expand source code
```
def create_oauth2_session(self):
session = self.raw_session(
self.service_endpoint,
oauth2_client=self.credentials.client,
oauth2_session_params=self.credentials.session_params(),
oauth2_token_endpoint=self.credentials.token_url,
)
if not session.token:
# Fetch the token explicitly -- it doesn't occur implicitly
token = session.fetch_token(
token_url=self.credentials.token_url,
client_id=self.credentials.client_id,
client_secret=self.credentials.client_secret,
scope=self.credentials.scope,
timeout=self.TIMEOUT,
**self.credentials.token_params(),
)
# Allow the credentials object to update its copy of the new token, and give the application an opportunity
# to cache it.
self.credentials.on_token_auto_refreshed(token)
session.auth = get_auth_instance(auth_type=OAUTH2, client=self.credentials.client)

return session
```

```
def create_session(self)
```

Expand source code
```
def create_session(self):
if self.credentials is None:
if self.auth_type in CREDENTIALS_REQUIRED:
raise ValueError(f"Auth type {self.auth_type!r} requires credentials")
session = self.raw_session(self.service_endpoint)
session.auth = get_auth_instance(auth_type=self.auth_type)
else:
if isinstance(self.credentials, BaseOAuth2Credentials):
with self.credentials.lock:
session = self.create_oauth2_session()
# Keep track of the credentials used to create this session. If and when we need to renew
# credentials (for example, refreshing an OAuth access token), this lets us easily determine whether
# the credentials have already been refreshed in another thread by the time this session tries.
session.credentials_sig = self.credentials.sig()
else:
if self.auth_type == NTLM and self.credentials.type == self.credentials.EMAIL:
username = "\\" + self.credentials.username
else:
username = self.credentials.username
session = self.raw_session(self.service_endpoint)
session.auth = get_auth_instance(
auth_type=self.auth_type, username=username, password=self.credentials.password
)

# Add some extra info
session.session_id = random.randint(10000, 99999) # Used for debugging messages in services
session.usage_count = 0
log.debug("Server %s: Created session %s", self.server, session.session_id)
return session
```

```
def decrease_poolsize(self)
```

Expand source code
```
def decrease_poolsize(self):
"""Decreases the session pool size in response to error messages from the server requesting to rate-limit
requests. We decrease by one session per call.
"""
# Take a single session from the pool and discard it. We need to protect this with a lock while we are changing
# the pool size variable, to avoid race conditions. We must keep at least one session in the pool.
if self._session_pool_size <= 1:
raise SessionPoolMinSizeReached("Session pool size cannot be decreased further")
with self._session_pool_lock:
if self._session_pool_size <= 1:
log.debug("Session pool size was decreased in another thread")
return
log.warning(
"Server %s: Decreasing session pool size from %s to %s",
self.server,
self._session_pool_size,
self._session_pool_size - 1,
)
session = self.get_session()
self.close_session(session)
self._session_pool_size -= 1
```

Decreases the session pool size in response to error messages from the server requesting to rate-limit requests. We decrease by one session per call.

```
def get_auth_type(self)
```

Expand source code
```
@abc.abstractmethod
def get_auth_type(self):
"""Autodetect authentication type"""
```

Autodetect authentication type

```
def get_session(self)
```

Expand source code
```
def get_session(self):
# Try to get a session from the queue. If the queue is empty, try to add one more session to the queue. If the
# queue is already at its max, wait until a session becomes available.
_timeout = 60 # Rate-limit messages about session starvation
try:
session = self._session_pool.get(block=False)
log.debug("Server %s: Got session immediately", self.server)
except Empty:
with suppress(SessionPoolMaxSizeReached):
self.increase_poolsize()
while True:
try:
log.debug("Server %s: Waiting for session", self.server)
session = self._session_pool.get(timeout=_timeout)
break
except Empty:
# This is normal when we have many worker threads starving for available sessions
log.debug("Server %s: No sessions available for %s seconds", self.server, _timeout)
log.debug("Server %s: Got session %s", self.server, session.session_id)
session.usage_count += 1
return session
```

```
def increase_poolsize(self)
```

Expand source code
```
def increase_poolsize(self):
"""Increases the session pool size. We increase by one session per call."""
# Create a single session and insert it into the pool. We need to protect this with a lock while we are changing
# the pool size variable, to avoid race conditions. We must not exceed the pool size limit.
if self._session_pool_size >= self._session_pool_maxsize:
raise SessionPoolMaxSizeReached("Session pool size cannot be increased further")
with self._session_pool_lock:
if self._session_pool_size >= self._session_pool_maxsize:
log.debug("Session pool size was increased in another thread")
return
log.debug(
"Server %s: Increasing session pool size from %s to %s",
self.server,
self._session_pool_size,
self._session_pool_size + 1,
)
self._session_pool.put(self.create_session(), block=False)
self._session_pool_size += 1
```

Increases the session pool size. We increase by one session per call.

```
def refresh_credentials(self, session)
```

Expand source code
```
def refresh_credentials(self, session):
# Credentials need to be refreshed, probably due to an OAuth
# access token expiring. If we've gotten here, it's because the
# application didn't provide an OAuth client secret, so we can't
# handle token refreshing for it.
with self.credentials.lock:
if self.credentials.sig() == session.credentials_sig:
# Credentials have not been refreshed by another thread:
# they're the same as the session was created with. If
# this isn't the case, we can just go ahead with a new
# session using the already-updated credentials.
self.credentials.refresh(session=session)
return self.renew_session(session)
```

```
def release_session(self, session)
```

Expand source code
```
def release_session(self, session):
# This should never fail, as we don't have more sessions than the queue contains
log.debug("Server %s: Releasing session %s", self.server, session.session_id)
if self.MAX_SESSION_USAGE_COUNT and session.usage_count >= self.MAX_SESSION_USAGE_COUNT:
log.debug("Server %s: session %s usage exceeded limit. Discarding", self.server, session.session_id)
session = self.renew_session(session)
self._session_pool.put(session, block=False)
```

```
def renew_session(self, session)
```

Expand source code
```
def renew_session(self, session):
# The session is useless. Close it completely and place a fresh session in the pool
log.debug("Server %s: Renewing session %s", self.server, session.session_id)
self.close_session(session)
return self.create_session()
```

```
def retire_session(self, session)
```

Expand source code
```
def retire_session(self, session):
# The session is useless. Close it completely and place a fresh session in the pool
log.debug("Server %s: Retiring session %s", self.server, session.session_id)
self.close_session(session)
self.release_session(self.create_session())
```

```
class Body
(...)
```

Expand source code
```
class Body(str):
"""Helper to mark the 'body' field as a complex attribute.

MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/body
"""

body_type = "Text"

def __add__(self, other):
# Make sure Body('') + 'foo' returns a Body type
return self.__class__(super().__add__(other))

def __mod__(self, other):
# Make sure Body('%s') % 'foo' returns a Body type
return self.__class__(super().__mod__(other))

def format(self, *args, **kwargs):
# Make sure Body('{}').format('foo') returns a Body type
return self.__class__(super().format(*args, **kwargs))
```

### Ancestors

* builtins.str

### Subclasses

* [HTMLBody](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.HTMLBody "exchangelib.properties.HTMLBody")

### Class variables

`var body_type`
The type of the None singleton.

### Methods

```
def format(self, *args, **kwargs)
```

Expand source code
```
def format(self, *args, **kwargs):
# Make sure Body('{}').format('foo') returns a Body type
return self.__class__(super().format(*args, **kwargs))
```

Return a formatted version of the string, using substitutions from args and kwargs. The substitutions are identified by braces ('{' and '}').

```
class Build
(major_version, minor_version, major_build=0, minor_build=0)
```

Expand source code
```
class Build:
"""Holds methods for working with build numbers."""

__slots__ = "major_version", "minor_version", "major_build", "minor_build"

def __init__(self, major_version, minor_version, major_build=0, minor_build=0):
if not isinstance(major_version, int):
raise InvalidTypeError("major_version", major_version, int)
if not isinstance(minor_version, int):
raise InvalidTypeError("minor_version", minor_version, int)
if not isinstance(major_build, int):
raise InvalidTypeError("major_build", major_build, int)
if not isinstance(minor_build, int):
raise InvalidTypeError("minor_build", minor_build, int)
self.major_version = major_version
self.minor_version = minor_version
self.major_build = major_build
self.minor_build = minor_build

@classmethod
def from_xml(cls, elem):
xml_elems_map = {
"major_version": "MajorVersion",
"minor_version": "MinorVersion",
"major_build": "MajorBuildNumber",
"minor_build": "MinorBuildNumber",
}
kwargs = {}
for k, xml_elem in xml_elems_map.items():
v = elem.get(xml_elem)
if v is None:
v = get_xml_attr(elem, f"{{{ANS}}}{xml_elem}")
if v is None:
raise ValueError()
kwargs[k] = int(v) # Also raises ValueError
return cls(**kwargs)

def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")

def __cmp__(self, other):
# __cmp__ is not a magic method in Python3. We'll just use it here to implement comparison operators
c = (self.major_version > other.major_version) - (self.major_version < other.major_version)
if c != 0:
return c
c = (self.minor_version > other.minor_version) - (self.minor_version < other.minor_version)
if c != 0:
return c
c = (self.major_build > other.major_build) - (self.major_build < other.major_build)
if c != 0:
return c
return (self.minor_build > other.minor_build) - (self.minor_build < other.minor_build)

def __eq__(self, other):
return self.__cmp__(other) == 0

def __hash__(self):
return hash(repr(self))

def __ne__(self, other):
return self.__cmp__(other) != 0

def __lt__(self, other):
return self.__cmp__(other) < 0

def __le__(self, other):
return self.__cmp__(other) <= 0

def __gt__(self, other):
return self.__cmp__(other) > 0

def __ge__(self, other):
return self.__cmp__(other) >= 0

def __str__(self):
return f"{self.major_version}.{self.minor_version}.{self.major_build}.{self.minor_build}"

def __repr__(self):
return self.__class__.__name__ + repr(
(self.major_version, self.minor_version, self.major_build, self.minor_build)
)
```

Holds methods for working with build numbers.

### Static methods

```
def from_xml(elem)
```

### Instance variables

`var major_build`

Expand source code
```
class Build:
"""Holds methods for working with build numbers."""

__slots__ = "major_version", "minor_version", "major_build", "minor_build"

def __init__(self, major_version, minor_version, major_build=0, minor_build=0):
if not isinstance(major_version, int):
raise InvalidTypeError("major_version", major_version, int)
if not isinstance(minor_version, int):
raise InvalidTypeError("minor_version", minor_version, int)
if not isinstance(major_build, int):
raise InvalidTypeError("major_build", major_build, int)
if not isinstance(minor_build, int):
raise InvalidTypeError("minor_build", minor_build, int)
self.major_version = major_version
self.minor_version = minor_version
self.major_build = major_build
self.minor_build = minor_build

@classmethod
def from_xml(cls, elem):
xml_elems_map = {
"major_version": "MajorVersion",
"minor_version": "MinorVersion",
"major_build": "MajorBuildNumber",
"minor_build": "MinorBuildNumber",
}
kwargs = {}
for k, xml_elem in xml_elems_map.items():
v = elem.get(xml_elem)
if v is None:
v = get_xml_attr(elem, f"{{{ANS}}}{xml_elem}")
if v is None:
raise ValueError()
kwargs[k] = int(v) # Also raises ValueError
return cls(**kwargs)

def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")

def __cmp__(self, other):
# __cmp__ is not a magic method in Python3. We'll just use it here to implement comparison operators
c = (self.major_version > other.major_version) - (self.major_version < other.major_version)
if c != 0:
return c
c = (self.minor_version > other.minor_version) - (self.minor_version < other.minor_version)
if c != 0:
return c
c = (self.major_build > other.major_build) - (self.major_build < other.major_build)
if c != 0:
return c
return (self.minor_build > other.minor_build) - (self.minor_build < other.minor_build)

def __eq__(self, other):
return self.__cmp__(other) == 0

def __hash__(self):
return hash(repr(self))

def __ne__(self, other):
return self.__cmp__(other) != 0

def __lt__(self, other):
return self.__cmp__(other) < 0

def __le__(self, other):
return self.__cmp__(other) <= 0

def __gt__(self, other):
return self.__cmp__(other) > 0

def __ge__(self, other):
return self.__cmp__(other) >= 0

def __str__(self):
return f"{self.major_version}.{self.minor_version}.{self.major_build}.{self.minor_build}"

def __repr__(self):
return self.__class__.__name__ + repr(
(self.major_version, self.minor_version, self.major_build, self.minor_build)
)
```

`var major_version`

Expand source code
```
class Build:
"""Holds methods for working with build numbers."""

__slots__ = "major_version", "minor_version", "major_build", "minor_build"

def __init__(self, major_version, minor_version, major_build=0, minor_build=0):
if not isinstance(major_version, int):
raise InvalidTypeError("major_version", major_version, int)
if not isinstance(minor_version, int):
raise InvalidTypeError("minor_version", minor_version, int)
if not isinstance(major_build, int):
raise InvalidTypeError("major_build", major_build, int)
if not isinstance(minor_build, int):
raise InvalidTypeError("minor_build", minor_build, int)
self.major_version = major_version
self.minor_version = minor_version
self.major_build = major_build
self.minor_build = minor_build

@classmethod
def from_xml(cls, elem):
xml_elems_map = {
"major_version": "MajorVersion",
"minor_version": "MinorVersion",
"major_build": "MajorBuildNumber",
"minor_build": "MinorBuildNumber",
}
kwargs = {}
for k, xml_elem in xml_elems_map.items():
v = elem.get(xml_elem)
if v is None:
v = get_xml_attr(elem, f"{{{ANS}}}{xml_elem}")
if v is None:
raise ValueError()
kwargs[k] = int(v) # Also raises ValueError
return cls(**kwargs)

def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")

def __cmp__(self, other):
# __cmp__ is not a magic method in Python3. We'll just use it here to implement comparison operators
c = (self.major_version > other.major_version) - (self.major_version < other.major_version)
if c != 0:
return c
c = (self.minor_version > other.minor_version) - (self.minor_version < other.minor_version)
if c != 0:
return c
c = (self.major_build > other.major_build) - (self.major_build < other.major_build)
if c != 0:
return c
return (self.minor_build > other.minor_build) - (self.minor_build < other.minor_build)

def __eq__(self, other):
return self.__cmp__(other) == 0

def __hash__(self):
return hash(repr(self))

def __ne__(self, other):
return self.__cmp__(other) != 0

def __lt__(self, other):
return self.__cmp__(other) < 0

def __le__(self, other):
return self.__cmp__(other) <= 0

def __gt__(self, other):
return self.__cmp__(other) > 0

def __ge__(self, other):
return self.__cmp__(other) >= 0

def __str__(self):
return f"{self.major_version}.{self.minor_version}.{self.major_build}.{self.minor_build}"

def __repr__(self):
return self.__class__.__name__ + repr(
(self.major_version, self.minor_version, self.major_build, self.minor_build)
)
```

`var minor_build`

Expand source code
```
class Build:
"""Holds methods for working with build numbers."""

__slots__ = "major_version", "minor_version", "major_build", "minor_build"

def __init__(self, major_version, minor_version, major_build=0, minor_build=0):
if not isinstance(major_version, int):
raise InvalidTypeError("major_version", major_version, int)
if not isinstance(minor_version, int):
raise InvalidTypeError("minor_version", minor_version, int)
if not isinstance(major_build, int):
raise InvalidTypeError("major_build", major_build, int)
if not isinstance(minor_build, int):
raise InvalidTypeError("minor_build", minor_build, int)
self.major_version = major_version
self.minor_version = minor_version
self.major_build = major_build
self.minor_build = minor_build

@classmethod
def from_xml(cls, elem):
xml_elems_map = {
"major_version": "MajorVersion",
"minor_version": "MinorVersion",
"major_build": "MajorBuildNumber",
"minor_build": "MinorBuildNumber",
}
kwargs = {}
for k, xml_elem in xml_elems_map.items():
v = elem.get(xml_elem)
if v is None:
v = get_xml_attr(elem, f"{{{ANS}}}{xml_elem}")
if v is None:
raise ValueError()
kwargs[k] = int(v) # Also raises ValueError
return cls(**kwargs)

def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")

def __cmp__(self, other):
# __cmp__ is not a magic method in Python3. We'll just use it here to implement comparison operators
c = (self.major_version > other.major_version) - (self.major_version < other.major_version)
if c != 0:
return c
c = (self.minor_version > other.minor_version) - (self.minor_version < other.minor_version)
if c != 0:
return c
c = (self.major_build > other.major_build) - (self.major_build < other.major_build)
if c != 0:
return c
return (self.minor_build > other.minor_build) - (self.minor_build < other.minor_build)

def __eq__(self, other):
return self.__cmp__(other) == 0

def __hash__(self):
return hash(repr(self))

def __ne__(self, other):
return self.__cmp__(other) != 0

def __lt__(self, other):
return self.__cmp__(other) < 0

def __le__(self, other):
return self.__cmp__(other) <= 0

def __gt__(self, other):
return self.__cmp__(other) > 0

def __ge__(self, other):
return self.__cmp__(other) >= 0

def __str__(self):
return f"{self.major_version}.{self.minor_version}.{self.major_build}.{self.minor_build}"

def __repr__(self):
return self.__class__.__name__ + repr(
(self.major_version, self.minor_version, self.major_build, self.minor_build)
)
```

`var minor_version`

Expand source code
```
class Build:
"""Holds methods for working with build numbers."""

__slots__ = "major_version", "minor_version", "major_build", "minor_build"

def __init__(self, major_version, minor_version, major_build=0, minor_build=0):
if not isinstance(major_version, int):
raise InvalidTypeError("major_version", major_version, int)
if not isinstance(minor_version, int):
raise InvalidTypeError("minor_version", minor_version, int)
if not isinstance(major_build, int):
raise InvalidTypeError("major_build", major_build, int)
if not isinstance(minor_build, int):
raise InvalidTypeError("minor_build", minor_build, int)
self.major_version = major_version
self.minor_version = minor_version
self.major_build = major_build
self.minor_build = minor_build

@classmethod
def from_xml(cls, elem):
xml_elems_map = {
"major_version": "MajorVersion",
"minor_version": "MinorVersion",
"major_build": "MajorBuildNumber",
"minor_build": "MinorBuildNumber",
}
kwargs = {}
for k, xml_elem in xml_elems_map.items():
v = elem.get(xml_elem)
if v is None:
v = get_xml_attr(elem, f"{{{ANS}}}{xml_elem}")
if v is None:
raise ValueError()
kwargs[k] = int(v) # Also raises ValueError
return cls(**kwargs)

def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")

def __cmp__(self, other):
# __cmp__ is not a magic method in Python3. We'll just use it here to implement comparison operators
c = (self.major_version > other.major_version) - (self.major_version < other.major_version)
if c != 0:
return c
c = (self.minor_version > other.minor_version) - (self.minor_version < other.minor_version)
if c != 0:
return c
c = (self.major_build > other.major_build) - (self.major_build < other.major_build)
if c != 0:
return c
return (self.minor_build > other.minor_build) - (self.minor_build < other.minor_build)

def __eq__(self, other):
return self.__cmp__(other) == 0

def __hash__(self):
return hash(repr(self))

def __ne__(self, other):
return self.__cmp__(other) != 0

def __lt__(self, other):
return self.__cmp__(other) < 0

def __le__(self, other):
return self.__cmp__(other) <= 0

def __gt__(self, other):
return self.__cmp__(other) > 0

def __ge__(self, other):
return self.__cmp__(other) >= 0

def __str__(self):
return f"{self.major_version}.{self.minor_version}.{self.major_build}.{self.minor_build}"

def __repr__(self):
return self.__class__.__name__ + repr(
(self.major_version, self.minor_version, self.major_build, self.minor_build)
)
```

### Methods

```
def api_version(self)
```

Expand source code
```
def api_version(self):
for build, api_version, _ in VERSIONS:
if self.major_version != build.major_version or self.minor_version != build.minor_version:
continue
if self >= build:
return api_version
raise ValueError(f"API version for build {self} is unknown")
```

```
class CalendarItem
(**kwargs)
```

Expand source code
```
class CalendarItem(Item, AcceptDeclineMixIn):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/calendaritem"""

ELEMENT_NAME = "CalendarItem"

uid = TextField(field_uri="calendar:UID", is_required_after_save=True, is_searchable=False)
recurrence_id = DateTimeField(field_uri="calendar:RecurrenceId", is_read_only=True)
start = DateOrDateTimeField(field_uri="calendar:Start", is_required=True)
end = DateOrDateTimeField(field_uri="calendar:End", is_required=True)
original_start = DateTimeField(field_uri="calendar:OriginalStart", is_read_only=True)
is_all_day = BooleanField(field_uri="calendar:IsAllDayEvent", is_required=True, default=False)
legacy_free_busy_status = FreeBusyStatusField(
field_uri="calendar:LegacyFreeBusyStatus", is_required=True, default="Busy"
)
location = TextField(field_uri="calendar:Location")
when = TextField(field_uri="calendar:When")
is_meeting = BooleanField(field_uri="calendar:IsMeeting", is_read_only=True)
is_cancelled = BooleanField(field_uri="calendar:IsCancelled", is_read_only=True)
is_recurring = BooleanField(field_uri="calendar:IsRecurring", is_read_only=True)
meeting_request_was_sent = BooleanField(field_uri="calendar:MeetingRequestWasSent", is_read_only=True)
is_response_requested = BooleanField(
field_uri="calendar:IsResponseRequested", default=None, is_required_after_save=True, is_searchable=False
)
type = ChoiceField(
field_uri="calendar:CalendarItemType", choices={Choice(c) for c in CALENDAR_ITEM_CHOICES}, is_read_only=True
)
my_response_type = ChoiceField(
field_uri="calendar:MyResponseType", choices={Choice(c) for c in Attendee.RESPONSE_TYPES}, is_read_only=True
)
organizer = MailboxField(field_uri="calendar:Organizer", is_read_only=True)
required_attendees = AttendeesField(field_uri="calendar:RequiredAttendees", is_searchable=False)
optional_attendees = AttendeesField(field_uri="calendar:OptionalAttendees", is_searchable=False)
resources = AttendeesField(field_uri="calendar:Resources", is_searchable=False)
conflicting_meeting_count = IntegerField(field_uri="calendar:ConflictingMeetingCount", is_read_only=True)
adjacent_meeting_count = IntegerField(field_uri="calendar:AdjacentMeetingCount", is_read_only=True)
conflicting_meetings = EWSElementListField(
field_uri="calendar:ConflictingMeetings", value_cls="CalendarItem", namespace=Item.NAMESPACE, is_read_only=True
)
adjacent_meetings = EWSElementListField(
field_uri="calendar:AdjacentMeetings", value_cls="CalendarItem", namespace=Item.NAMESPACE, is_read_only=True
)
duration = CharField(field_uri="calendar:Duration", is_read_only=True)
appointment_reply_time = DateTimeField(field_uri="calendar:AppointmentReplyTime", is_read_only=True)
appointment_sequence_number = IntegerField(field_uri="calendar:AppointmentSequenceNumber", is_read_only=True)
appointment_state = AppointmentStateField(field_uri="calendar:AppointmentState", is_read_only=True)
recurrence = RecurrenceField(field_uri="calendar:Recurrence", is_searchable=False)
first_occurrence = OccurrenceField(
field_uri="calendar:FirstOccurrence", value_cls=FirstOccurrence, is_read_only=True
)
last_occurrence = OccurrenceField(field_uri="calendar:LastOccurrence", value_cls=LastOccurrence, is_read_only=True)
modified_occurrences = OccurrenceListField(
field_uri="calendar:ModifiedOccurrences", value_cls=Occurrence, is_read_only=True
)
deleted_occurrences = OccurrenceListField(
field_uri="calendar:DeletedOccurrences", value_cls=DeletedOccurrence, is_read_only=True
)
_meeting_timezone = TimeZoneField(
field_uri="calendar:MeetingTimeZone", deprecated_from=EXCHANGE_2010, is_searchable=False
)
_start_timezone = TimeZoneField(
field_uri="calendar:StartTimeZone", supported_from=EXCHANGE_2010, is_searchable=False
)
_end_timezone = TimeZoneField(field_uri="calendar:EndTimeZone", supported_from=EXCHANGE_2010, is_searchable=False)
conference_type = EnumAsIntField(
field_uri="calendar:ConferenceType", enum=CONFERENCE_TYPES, min=0, default=None, is_required_after_save=True
)
allow_new_time_proposal = BooleanField(
field_uri="calendar:AllowNewTimeProposal", default=None, is_required_after_save=True, is_searchable=False
)
is_online_meeting = BooleanField(field_uri="calendar:IsOnlineMeeting", default=None, is_read_only=True)
meeting_workspace_url = URIField(field_uri="calendar:MeetingWorkspaceUrl")
net_show_url = URIField(field_uri="calendar:NetShowUrl")

def occurrence(self, index):
"""Get an occurrence of a recurring master by index. No query is sent to the server to actually fetch the item.
Call refresh() on the item to do so.

Only call this method on a recurring master.

:param index: The index, which is 1-based

:return The occurrence
"""
return self.__class__(
account=self.account,
folder=self.folder,
_id=OccurrenceItemId(id=self.id, changekey=self.changekey, instance_index=index),
)

def recurring_master(self):
"""Get the recurring master of an occurrence. No query is sent to the server to actually fetch the item.
Call refresh() on the item to do so.

Only call this method on an occurrence of a recurring master.

:return: The master occurrence
"""
return self.__class__(
account=self.account,
folder=self.folder,
_id=RecurringMasterItemId(id=self.id, changekey=self.changekey),
)

@classmethod
def timezone_fields(cls):
return tuple(f for f in cls.FIELDS if isinstance(f, TimeZoneField))

def clean_timezone_fields(self, version):
# Sets proper values on the timezone fields if they are not already set
if self.start is None:
start_tz = None
elif type(self.start) in (EWSDate, datetime.date):
start_tz = self.account.default_timezone
else:
start_tz = self.start.tzinfo
if self.end is None:
end_tz = None
elif type(self.end) in (EWSDate, datetime.date):
end_tz = self.account.default_timezone
else:
end_tz = self.end.tzinfo
if version.build < EXCHANGE_2010:
if self._meeting_timezone is None:
self._meeting_timezone = start_tz
self._start_timezone = None
self._end_timezone = None
else:
self._meeting_timezone = None
if self._start_timezone is None:
self._start_timezone = start_tz
if self._end_timezone is None:
self._end_timezone = end_tz

def clean(self, version=None):
super().clean(version=version)
if self.start and self.end and self.end < self.start:
raise ValueError(f"'end' must be greater than 'start' ({self.start} -> {self.end})")
if version:
self.clean_timezone_fields(version=version)

def cancel(self, **kwargs):
return CancelCalendarItem(
account=self.account, reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey), **kwargs
).send()

def _update_fieldnames(self):
update_fields = super()._update_fieldnames()
if self.type == OCCURRENCE:
# Some CalendarItem fields cannot be updated when the item is an occurrence. The values are empty when we
# receive them so would have been updated because they are set to None.
update_fields.remove("recurrence")
update_fields.remove("uid")
return update_fields

@classmethod
def from_xml(cls, elem, account):
item = super().from_xml(elem=elem, account=account)
# EWS returns the start and end values as a datetime regardless of the is_all_day status. Convert to date if
# applicable.
if not item.is_all_day:
return item
for field_name in ("start", "end"):
val = getattr(item, field_name)
if val is None:
continue
# Return just the date part of the value. Subtract 1 day from the date if this is the end field. This is
# the inverse of what we do in .to_xml(). Convert to the local timezone before getting the date.
if field_name == "end":
val -= datetime.timedelta(days=1)
tz = getattr(item, f"_{field_name}_timezone")
setattr(item, field_name, val.astimezone(tz).date())
return item

def tz_field_for_field_name(self, field_name):
meeting_tz_field, start_tz_field, end_tz_field = CalendarItem.timezone_fields()
if self.account.version.build < EXCHANGE_2010:
return meeting_tz_field
if field_name == "start":
return start_tz_field
if field_name == "end":
return end_tz_field
raise ValueError("Unsupported field_name")

def date_to_datetime(self, field_name):
# EWS always expects a datetime. If we have a date value, then convert it to datetime in the local
# timezone. Additionally, if this the end field, add 1 day to the date. We could add 12 hours to both
# start and end values and let EWS apply its logic, but that seems hacky.
value = getattr(self, field_name)
tz = getattr(self, self.tz_field_for_field_name(field_name).name)
value = EWSDateTime.combine(value, datetime.time(0, 0)).replace(tzinfo=tz)
if field_name == "end":
value += datetime.timedelta(days=1)
return value

def to_xml(self, version):
# EWS has some special logic related to all-day start and end values. Non-midnight start values are pushed to
# the previous midnight. Non-midnight end values are pushed to the following midnight. Midnight in this context
# refers to midnight in the local timezone. See
#
# https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/how-to-create-all-day-events-by-using-ews-in-exchange
#
elem = super().to_xml(version=version)
if not self.is_all_day:
return elem
for field_name in ("start", "end"):
value = getattr(self, field_name)
if value is None:
continue
if type(value) in (EWSDate, datetime.date):
# EWS always expects a datetime
value = self.date_to_datetime(field_name=field_name)
# We already generated an XML element for this field, but it contains a plain date at this point, which
# is invalid. Replace the value.
field = self.get_field_by_fieldname(field_name)
set_xml_value(elem.find(field.response_tag()), value)
return elem
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")
* [AcceptDeclineMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/calendar_item.html#exchangelib.items.calendar_item.AcceptDeclineMixIn "exchangelib.items.calendar_item.AcceptDeclineMixIn")

### Static methods

```
def from_xml(elem, account)
```

```
def timezone_fields()
```

### Instance variables

`var adjacent_meeting_count`
The type of the None singleton.

`var adjacent_meetings`
The type of the None singleton.

`var allow_new_time_proposal`
The type of the None singleton.

`var appointment_reply_time`
The type of the None singleton.

`var appointment_sequence_number`
The type of the None singleton.

`var appointment_state`
The type of the None singleton.

`var conference_type`
The type of the None singleton.

`var conflicting_meeting_count`
The type of the None singleton.

`var conflicting_meetings`
The type of the None singleton.

`var deleted_occurrences`
The type of the None singleton.

`var duration`
The type of the None singleton.

`var end`
The type of the None singleton.

`var first_occurrence`
The type of the None singleton.

`var is_all_day`
The type of the None singleton.

`var is_cancelled`
The type of the None singleton.

`var is_meeting`
The type of the None singleton.

`var is_online_meeting`
The type of the None singleton.

`var is_recurring`
The type of the None singleton.

`var is_response_requested`
The type of the None singleton.

`var last_occurrence`
The type of the None singleton.

`var legacy_free_busy_status`
The type of the None singleton.

`var location`
The type of the None singleton.

`var meeting_request_was_sent`
The type of the None singleton.

`var meeting_workspace_url`
The type of the None singleton.

`var modified_occurrences`
The type of the None singleton.

`var my_response_type`
The type of the None singleton.

`var net_show_url`
The type of the None singleton.

`var optional_attendees`
The type of the None singleton.

`var organizer`
The type of the None singleton.

`var original_start`
The type of the None singleton.

`var recurrence`
The type of the None singleton.

`var recurrence_id`
The type of the None singleton.

`var required_attendees`
The type of the None singleton.

`var resources`
The type of the None singleton.

`var start`
The type of the None singleton.

`var type`
The type of the None singleton.

`var uid`
The type of the None singleton.

`var when`
The type of the None singleton.

### Methods

```
def cancel(self, **kwargs)
```

Expand source code
```
def cancel(self, **kwargs):
return CancelCalendarItem(
account=self.account, reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey), **kwargs
).send()
```

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
super().clean(version=version)
if self.start and self.end and self.end < self.start:
raise ValueError(f"'end' must be greater than 'start' ({self.start} -> {self.end})")
if version:
self.clean_timezone_fields(version=version)
```

```
def clean_timezone_fields(self, version)
```

Expand source code
```
def clean_timezone_fields(self, version):
# Sets proper values on the timezone fields if they are not already set
if self.start is None:
start_tz = None
elif type(self.start) in (EWSDate, datetime.date):
start_tz = self.account.default_timezone
else:
start_tz = self.start.tzinfo
if self.end is None:
end_tz = None
elif type(self.end) in (EWSDate, datetime.date):
end_tz = self.account.default_timezone
else:
end_tz = self.end.tzinfo
if version.build < EXCHANGE_2010:
if self._meeting_timezone is None:
self._meeting_timezone = start_tz
self._start_timezone = None
self._end_timezone = None
else:
self._meeting_timezone = None
if self._start_timezone is None:
self._start_timezone = start_tz
if self._end_timezone is None:
self._end_timezone = end_tz
```

```
def date_to_datetime(self, field_name)
```

Expand source code
```
def date_to_datetime(self, field_name):
# EWS always expects a datetime. If we have a date value, then convert it to datetime in the local
# timezone. Additionally, if this the end field, add 1 day to the date. We could add 12 hours to both
# start and end values and let EWS apply its logic, but that seems hacky.
value = getattr(self, field_name)
tz = getattr(self, self.tz_field_for_field_name(field_name).name)
value = EWSDateTime.combine(value, datetime.time(0, 0)).replace(tzinfo=tz)
if field_name == "end":
value += datetime.timedelta(days=1)
return value
```

```
def occurrence(self, index)
```

Expand source code
```
def occurrence(self, index):
"""Get an occurrence of a recurring master by index. No query is sent to the server to actually fetch the item.
Call refresh() on the item to do so.

Only call this method on a recurring master.

:param index: The index, which is 1-based

:return The occurrence
"""
return self.__class__(
account=self.account,
folder=self.folder,
_id=OccurrenceItemId(id=self.id, changekey=self.changekey, instance_index=index),
)
```

Get an occurrence of a recurring master by index. No query is sent to the server to actually fetch the item. Call refresh() on the item to do so.

Only call this method on a recurring master.

:param index: The index, which is 1-based

:return The occurrence

```
def recurring_master(self)
```

Expand source code
```
def recurring_master(self):
"""Get the recurring master of an occurrence. No query is sent to the server to actually fetch the item.
Call refresh() on the item to do so.

Only call this method on an occurrence of a recurring master.

:return: The master occurrence
"""
return self.__class__(
account=self.account,
folder=self.folder,
_id=RecurringMasterItemId(id=self.id, changekey=self.changekey),
)
```

Get the recurring master of an occurrence. No query is sent to the server to actually fetch the item. Call refresh() on the item to do so.

Only call this method on an occurrence of a recurring master.

:return: The master occurrence

```
def to_xml(self, version)
```

Expand source code
```
def to_xml(self, version):
# EWS has some special logic related to all-day start and end values. Non-midnight start values are pushed to
# the previous midnight. Non-midnight end values are pushed to the following midnight. Midnight in this context
# refers to midnight in the local timezone. See
#
# https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/how-to-create-all-day-events-by-using-ews-in-exchange
#
elem = super().to_xml(version=version)
if not self.is_all_day:
return elem
for field_name in ("start", "end"):
value = getattr(self, field_name)
if value is None:
continue
if type(value) in (EWSDate, datetime.date):
# EWS always expects a datetime
value = self.date_to_datetime(field_name=field_name)
# We already generated an XML element for this field, but it contains a plain date at this point, which
# is invalid. Replace the value.
field = self.get_field_by_fieldname(field_name)
set_xml_value(elem.find(field.response_tag()), value)
return elem
```

```
def tz_field_for_field_name(self, field_name)
```

Expand source code
```
def tz_field_for_field_name(self, field_name):
meeting_tz_field, start_tz_field, end_tz_field = CalendarItem.timezone_fields()
if self.account.version.build < EXCHANGE_2010:
return meeting_tz_field
if field_name == "start":
return start_tz_field
if field_name == "end":
return end_tz_field
raise ValueError("Unsupported field_name")
```

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class CancelCalendarItem
(**kwargs)
```

Expand source code
```
class CancelCalendarItem(BaseReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/cancelcalendaritem"""

ELEMENT_NAME = "CancelCalendarItem"
author_idx = BaseReplyItem.FIELDS.index_by_name("author")
FIELDS = BaseReplyItem.FIELDS[:author_idx] + BaseReplyItem.FIELDS[author_idx + 1 :]
```

### Ancestors

* [BaseReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseReplyItem "exchangelib.items.base.BaseReplyItem")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

The type of the None singleton.

### Inherited members

* `BaseReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `author`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `new_body`
* `received_by`
* `received_representing`
* `reference_item_id`
* `remove_field`
* `save`
* `subject`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class Configuration
(credentials=None,server=None,service_endpoint=None,auth_type=None,version=None,retry_policy=None,max_connections=None)
```

Expand source code
```
class Configuration:
"""Contains information needed to create an authenticated connection to an EWS endpoint.

The 'credentials' argument contains the credentials needed to authenticate with the server. Multiple credentials
implementations are available in 'exchangelib.credentials'.

config = Configuration(credentials=Credentials('john@example.com', 'MY_SECRET'), ...)

The 'server' and 'service_endpoint' arguments are mutually exclusive. The former must contain only a domain name,
the latter a full URL:

config = Configuration(server='example.com', ...)
config = Configuration(service_endpoint='https://mail.example.com/EWS/Exchange.asmx', ...)

If you know which authentication type the server uses, you add that as a hint in 'auth_type'. Likewise, you can
add the server version as a hint. This allows to skip the auth type and version guessing routines:

config = Configuration(auth_type=NTLM, ...)
config = Configuration(version=Version(build=Build(15, 1, 2, 3)), ...)

You can use 'retry_policy' to define a custom retry policy for handling server connection failures:

config = Configuration(retry_policy=FaultTolerance(max_wait=3600), ...)

'max_connections' defines the max number of connections allowed for this server. This may be restricted by
policies on the Exchange server.
"""

def __init__(
self,
credentials=None,
server=None,
service_endpoint=None,
auth_type=None,
version=None,
retry_policy=None,
max_connections=None,
):
if not isinstance(credentials, (BaseCredentials, type(None))):
raise InvalidTypeError("credentials", credentials, BaseCredentials)
if auth_type is None and isinstance(credentials, BaseOAuth2Credentials):
# Set a default auth type for the credentials where this makes sense
auth_type = OAUTH2
if auth_type is not None and auth_type not in AUTH_TYPE_MAP:
raise InvalidEnumValue("auth_type", auth_type, AUTH_TYPE_MAP)
if credentials is None and auth_type in CREDENTIALS_REQUIRED:
raise ValueError(f"Auth type {auth_type!r} was detected but no credentials were provided")
if server and service_endpoint:
raise AttributeError("Only one of 'server' or 'service_endpoint' must be provided")
if not retry_policy:
retry_policy = FailFast()
if not isinstance(version, (Version, type(None))):
raise InvalidTypeError("version", version, Version)
if not isinstance(retry_policy, RetryPolicy):
raise InvalidTypeError("retry_policy", retry_policy, RetryPolicy)
if not isinstance(max_connections, (int, type(None))):
raise InvalidTypeError("max_connections", max_connections, int)
self._credentials = credentials
if server:
self.service_endpoint = f"https://{server}/EWS/Exchange.asmx"
else:
self.service_endpoint = service_endpoint
self.auth_type = auth_type
self.version = version
self.retry_policy = retry_policy
self.max_connections = max_connections

@property
def credentials(self):
# Do not update credentials from this class. Instead, do it from Protocol
return self._credentials

@threaded_cached_property
def server(self):
if not self.service_endpoint:
return None
return split_url(self.service_endpoint)[1]

def __repr__(self):
args_str = ", ".join(
f"{k}={getattr(self, k)!r}"
for k in ("credentials", "service_endpoint", "auth_type", "version", "retry_policy")
)
return f"{self.__class__.__name__}({args_str})"
```

Contains information needed to create an authenticated connection to an EWS endpoint.

The 'credentials' argument contains the credentials needed to authenticate with the server. Multiple credentials implementations are available in 'exchangelib.credentials'.

config = Configuration(credentials=Credentials('john@example.com', 'MY_SECRET'), …)

The 'server' and 'service_endpoint' arguments are mutually exclusive. The former must contain only a domain name, the latter a full URL:

```
config = Configuration(server='example.com', ...)
config = Configuration(service_endpoint='https://mail.example.com/EWS/Exchange.asmx', ...)
```

If you know which authentication type the server uses, you add that as a hint in 'auth_type'. Likewise, you can add the server version as a hint. This allows to skip the auth type and version guessing routines:

```
config = Configuration(auth_type=NTLM, ...)
config = Configuration(version=Version(build=Build(15, 1, 2, 3)), ...)
```

You can use 'retry_policy' to define a custom retry policy for handling server connection failures:

```
config = Configuration(retry_policy=FaultTolerance(max_wait=3600), ...)
```

'max_connections' defines the max number of connections allowed for this server. This may be restricted by policies on the Exchange server.

### Subclasses

* [O365InteractiveConfiguration](https://ecederstrand.github.io/exchangelib/exchangelib/configuration.html#exchangelib.configuration.O365InteractiveConfiguration "exchangelib.configuration.O365InteractiveConfiguration")

### Instance variables

`prop credentials`

Expand source code
```
@property
def credentials(self):
# Do not update credentials from this class. Instead, do it from Protocol
return self._credentials
```

`var server`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

```
class Contact
(**kwargs)
```

Expand source code
```
class Contact(Item):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contact"""

ELEMENT_NAME = "Contact"

file_as = TextField(field_uri="contacts:FileAs")
file_as_mapping = ChoiceField(
field_uri="contacts:FileAsMapping",
choices={
Choice("None"),
Choice("LastCommaFirst"),
Choice("FirstSpaceLast"),
Choice("Company"),
Choice("LastCommaFirstCompany"),
Choice("CompanyLastFirst"),
Choice("LastFirst"),
Choice("LastFirstCompany"),
Choice("CompanyLastCommaFirst"),
Choice("LastFirstSuffix"),
Choice("LastSpaceFirstCompany"),
Choice("CompanyLastSpaceFirst"),
Choice("LastSpaceFirst"),
Choice("DisplayName"),
Choice("FirstName"),
Choice("LastFirstMiddleSuffix"),
Choice("LastName"),
Choice("Empty"),
},
)
display_name = TextField(field_uri="contacts:DisplayName", is_required=True)
given_name = CharField(field_uri="contacts:GivenName")
initials = TextField(field_uri="contacts:Initials")
middle_name = CharField(field_uri="contacts:MiddleName")
nickname = TextField(field_uri="contacts:Nickname")
complete_name = EWSElementField(field_uri="contacts:CompleteName", value_cls=CompleteName, is_read_only=True)
company_name = TextField(field_uri="contacts:CompanyName")
email_addresses = EmailAddressesField(field_uri="contacts:EmailAddress")
physical_addresses = PhysicalAddressField(field_uri="contacts:PhysicalAddress")
phone_numbers = PhoneNumberField(field_uri="contacts:PhoneNumber")
assistant_name = TextField(field_uri="contacts:AssistantName")
birthday = DateTimeBackedDateField(field_uri="contacts:Birthday", default_time=datetime.time(11, 59))
business_homepage = URIField(field_uri="contacts:BusinessHomePage")
children = TextListField(field_uri="contacts:Children")
companies = TextListField(field_uri="contacts:Companies", is_searchable=False)
contact_source = ChoiceField(
field_uri="contacts:ContactSource", choices={Choice("Store"), Choice("ActiveDirectory")}, is_read_only=True
)
department = TextField(field_uri="contacts:Department")
generation = TextField(field_uri="contacts:Generation")
im_addresses = ImAddressField(field_uri="contacts:ImAddress")
job_title = TextField(field_uri="contacts:JobTitle")
manager = TextField(field_uri="contacts:Manager")
mileage = TextField(field_uri="contacts:Mileage")
office = TextField(field_uri="contacts:OfficeLocation")
postal_address_index = ChoiceField(
field_uri="contacts:PostalAddressIndex",
choices={Choice("Business"), Choice("Home"), Choice("Other"), Choice("None")},
default="None",
is_required_after_save=True,
)
profession = TextField(field_uri="contacts:Profession")
spouse_name = TextField(field_uri="contacts:SpouseName")
surname = CharField(field_uri="contacts:Surname")
wedding_anniversary = DateTimeBackedDateField(
field_uri="contacts:WeddingAnniversary", default_time=datetime.time(11, 59)
)
has_picture = BooleanField(field_uri="contacts:HasPicture", supported_from=EXCHANGE_2010, is_read_only=True)
phonetic_full_name = TextField(
field_uri="contacts:PhoneticFullName", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
phonetic_first_name = TextField(
field_uri="contacts:PhoneticFirstName", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
phonetic_last_name = TextField(
field_uri="contacts:PhoneticLastName", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
email_alias = EmailAddressField(field_uri="contacts:Alias", is_read_only=True, supported_from=EXCHANGE_2010_SP2)
# 'notes' is documented in MSDN but apparently unused. Writing to it raises ErrorInvalidPropertyRequest. OWA
# put entries into the 'notes' form field into the 'body' field.
notes = CharField(field_uri="contacts:Notes", supported_from=EXCHANGE_2010_SP2, is_read_only=True)
# 'photo' is documented in MSDN but apparently unused. Writing to it raises ErrorInvalidPropertyRequest. OWA
# adds photos as FileAttachments on the contact item (with 'is_contact_photo=True'), which automatically flips
# the 'has_picture' field.
photo = Base64Field(field_uri="contacts:Photo", supported_from=EXCHANGE_2010_SP2, is_read_only=True)
user_smime_certificate = Base64Field(
field_uri="contacts:UserSMIMECertificate", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
ms_exchange_certificate = Base64Field(
field_uri="contacts:MSExchangeCertificate", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
directory_id = TextField(field_uri="contacts:DirectoryId", supported_from=EXCHANGE_2010_SP2, is_read_only=True)
manager_mailbox = MailboxField(
field_uri="contacts:ManagerMailbox", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
direct_reports = MailboxListField(
field_uri="contacts:DirectReports", supported_from=EXCHANGE_2010_SP2, is_read_only=True
)
# O365 throws ErrorInternalServerError "[0x004f0102] MapiReplyToBlob" if UniqueBody is requested
unique_body_idx = Item.FIELDS.index_by_name("unique_body")
FIELDS = Item.FIELDS[:unique_body_idx] + Item.FIELDS[unique_body_idx + 1 :]
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var unique_body_idx`
The type of the None singleton.

### Instance variables

`var assistant_name`
The type of the None singleton.

`var birthday`
The type of the None singleton.

`var business_homepage`
The type of the None singleton.

`var children`
The type of the None singleton.

`var companies`
The type of the None singleton.

`var company_name`
The type of the None singleton.

`var complete_name`
The type of the None singleton.

`var contact_source`
The type of the None singleton.

`var department`
The type of the None singleton.

`var direct_reports`
The type of the None singleton.

`var directory_id`
The type of the None singleton.

`var display_name`
The type of the None singleton.

`var email_addresses`
The type of the None singleton.

`var email_alias`
The type of the None singleton.

`var file_as`
The type of the None singleton.

`var file_as_mapping`
The type of the None singleton.

`var generation`
The type of the None singleton.

`var given_name`
The type of the None singleton.

`var has_picture`
The type of the None singleton.

`var im_addresses`
The type of the None singleton.

`var initials`
The type of the None singleton.

`var job_title`
The type of the None singleton.

`var manager`
The type of the None singleton.

`var manager_mailbox`
The type of the None singleton.

`var middle_name`
The type of the None singleton.

`var mileage`
The type of the None singleton.

`var ms_exchange_certificate`
The type of the None singleton.

`var nickname`
The type of the None singleton.

`var notes`
The type of the None singleton.

`var office`
The type of the None singleton.

`var phone_numbers`
The type of the None singleton.

`var phonetic_first_name`
The type of the None singleton.

`var phonetic_full_name`
The type of the None singleton.

`var phonetic_last_name`
The type of the None singleton.

`var photo`
The type of the None singleton.

`var physical_addresses`
The type of the None singleton.

`var postal_address_index`
The type of the None singleton.

`var profession`
The type of the None singleton.

`var spouse_name`
The type of the None singleton.

`var surname`
The type of the None singleton.

`var user_smime_certificate`
The type of the None singleton.

`var wedding_anniversary`
The type of the None singleton.

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class Credentials
(username, password)
```

Expand source code
```
class Credentials(BaseCredentials):
r"""Keeps login info the way Exchange likes it.

Usernames for authentication are of one of these forms:
* PrimarySMTPAddress
* WINDOMAIN\username
* User Principal Name (UPN)
password: Clear-text password
"""

EMAIL = "email"
DOMAIN = "domain"
UPN = "upn"

def __init__(self, username, password):
super().__init__()
if username.count("@") == 1:
self.type = self.EMAIL
elif username.count("\\") == 1:
self.type = self.DOMAIN
else:
self.type = self.UPN
self.username = username
self.password = password

def __repr__(self):
return self.__class__.__name__ + repr((self.username, "********"))

def __str__(self):
return self.username
```

Keeps login info the way Exchange likes it.

Usernames for authentication are of one of these forms: * PrimarySMTPAddress * WINDOMAIN\username * User Principal Name (UPN) password: Clear-text password

### Ancestors

* [BaseCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseCredentials "exchangelib.credentials.BaseCredentials")

### Class variables

`var DOMAIN`
The type of the None singleton.

`var EMAIL`
The type of the None singleton.

`var UPN`
The type of the None singleton.

```
class DLMailbox
(**kwargs)
```

Expand source code
```
class DLMailbox(Mailbox):
"""Like Mailbox, but creates elements in the 'messages' namespace when sending requests."""

NAMESPACE = MNS
```

Like Mailbox, but creates elements in the 'messages' namespace when sending requests.

### Ancestors

* [Mailbox](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Mailbox "exchangelib.properties.Mailbox")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `Mailbox`:
* `ELEMENT_NAME`
* `FIELDS`
* `MAILBOX`
* `MAILBOX_TYPE_CHOICES`
* `NAMESPACE`
* `ONE_OFF`
* `add_field`
* `email_address`
* `item_id`
* `mailbox_type`
* `name`
* `remove_field`
* `routing_type`
* `supported_fields`
* `validate_field`

```
class DeclineItem
(**kwargs)
```

Expand source code
```
class DeclineItem(BaseMeetingReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/declineitem"""

ELEMENT_NAME = "DeclineItem"
```

### Ancestors

* [BaseMeetingReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/calendar_item.html#exchangelib.items.calendar_item.BaseMeetingReplyItem "exchangelib.items.calendar_item.BaseMeetingReplyItem")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseMeetingReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attachments`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `deregister`
* `headers`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `item_class`
* `proposed_end`
* `proposed_start`
* `received_by`
* `received_representing`
* `reference_item_id`
* `register`
* `remove_field`
* `sender`
* `sensitivity`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class DistributionList
(**kwargs)
```

Expand source code
```
class DistributionList(Item):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/distributionlist"""

ELEMENT_NAME = "DistributionList"

display_name = CharField(field_uri="contacts:DisplayName", is_required=True)
file_as = CharField(field_uri="contacts:FileAs", is_read_only=True)
contact_source = ChoiceField(
field_uri="contacts:ContactSource", choices={Choice("Store"), Choice("ActiveDirectory")}, is_read_only=True
)
members = MemberListField(field_uri="distributionlist:Members")

# O365 throws ErrorInternalServerError "[0x004f0102] MapiReplyToBlob" if UniqueBody is requested
unique_body_idx = Item.FIELDS.index_by_name("unique_body")
FIELDS = Item.FIELDS[:unique_body_idx] + Item.FIELDS[unique_body_idx + 1 :]
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var unique_body_idx`
The type of the None singleton.

### Instance variables

`var contact_source`
The type of the None singleton.

`var display_name`
The type of the None singleton.

`var file_as`
The type of the None singleton.

`var members`
The type of the None singleton.

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class EWSDate
(...)
```

Expand source code
```
class EWSDate(datetime.date):
"""Extends the normal date implementation to satisfy EWS."""

__slots__ = "_year", "_month", "_day", "_hashcode"

def ewsformat(self):
"""ISO 8601 format to satisfy xs:date as interpreted by EWS. Example: 2009-01-15."""
return self.isoformat()

def __add__(self, other):
dt = super().__add__(other)
if isinstance(dt, self.__class__):
return dt
return self.from_date(dt) # We want to return EWSDate objects

def __iadd__(self, other):
return self + other

def __sub__(self, other):
dt = super().__sub__(other)
if isinstance(dt, datetime.timedelta):
return dt
if isinstance(dt, self.__class__):
return dt
return self.from_date(dt) # We want to return EWSDate objects

def __isub__(self, other):
return self - other

@classmethod
def fromordinal(cls, n):
dt = super().fromordinal(n)
if isinstance(dt, cls):
return dt
return cls.from_date(dt) # We want to return EWSDate objects

@classmethod
def from_date(cls, d):
if type(d) is not datetime.date:
raise InvalidTypeError("d", d, datetime.date)
return cls(d.year, d.month, d.day)

@classmethod
def from_string(cls, date_string):
# Sometimes, we'll receive a date string with time zone information. Not very useful.
if date_string.endswith("Z"):
date_fmt = "%Y-%m-%dZ"
elif ":" in date_string:
if "+" in date_string:
date_fmt = "%Y-%m-%d+%H:%M"
else:
date_fmt = "%Y-%m-%d-%H:%M"
else:
date_fmt = "%Y-%m-%d"
d = datetime.datetime.strptime(date_string, date_fmt).date()
if isinstance(d, cls):
return d
return cls.from_date(d) # We want to return EWSDate objects
```

Extends the normal date implementation to satisfy EWS.

### Ancestors

* datetime.date

### Static methods

```
def from_date(d)
```

```
def from_string(date_string)
```

```
def fromordinal(n)
```

int -> date corresponding to a proleptic Gregorian ordinal.

### Methods

```
def ewsformat(self)
```

Expand source code
```
def ewsformat(self):
"""ISO 8601 format to satisfy xs:date as interpreted by EWS. Example: 2009-01-15."""
return self.isoformat()
```

ISO 8601 format to satisfy xs:date as interpreted by EWS. Example: 2009-01-15.

```
class EWSDateTime
(*args, **kwargs)
```

Expand source code
```
class EWSDateTime(datetime.datetime):
"""Extends the normal datetime implementation to satisfy EWS."""

__slots__ = "_year", "_month", "_day", "_hour", "_minute", "_second", "_microsecond", "_tzinfo", "_hashcode"

def __new__(cls, *args, **kwargs):
# pylint: disable=arguments-differ

if len(args) == 8:
tzinfo = args[7]
else:
tzinfo = kwargs.get("tzinfo")
if isinstance(tzinfo, zoneinfo.ZoneInfo):
# Don't allow pytz or dateutil timezones here. They are not safe to use as direct input for datetime()
tzinfo = EWSTimeZone.from_timezone(tzinfo)
if not isinstance(tzinfo, (EWSTimeZone, type(None))):
raise InvalidTypeError("tzinfo", tzinfo, EWSTimeZone)
if len(args) == 8:
args = args[:7] + (tzinfo,)
else:
kwargs["tzinfo"] = tzinfo
return super().__new__(cls, *args, **kwargs)

def ewsformat(self):
"""ISO 8601 format to satisfy xs:datetime as interpreted by EWS. Examples:
* 2009-01-15T13:45:56Z
* 2009-01-15T13:45:56+01:00
"""
if not self.tzinfo:
raise ValueError(f"{self!r} must be timezone-aware")
if self.tzinfo.key == "UTC":
if self.microsecond:
return self.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
return self.strftime("%Y-%m-%dT%H:%M:%SZ")
return self.isoformat()

@classmethod
def from_datetime(cls, d):
if type(d) is not datetime.datetime:
raise InvalidTypeError("d", d, datetime.datetime)
if d.tzinfo is None:
tz = None
elif isinstance(d.tzinfo, EWSTimeZone):
tz = d.tzinfo
else:
tz = EWSTimeZone.from_timezone(d.tzinfo)
return cls(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, tzinfo=tz)

def astimezone(self, tz=None):
if tz is None:
tz = EWSTimeZone.localzone()
t = super().astimezone(tz=tz).replace(tzinfo=tz)
if isinstance(t, self.__class__):
return t
return self.from_datetime(t) # We want to return EWSDateTime objects

@classmethod
def fromisoformat(cls, date_string):
return cls.from_string(date_string)

def __add__(self, other):
t = super().__add__(other)
if isinstance(t, self.__class__):
return t
return self.from_datetime(t) # We want to return EWSDateTime objects

def __iadd__(self, other):
return self + other

def __sub__(self, other):
t = super().__sub__(other)
if isinstance(t, datetime.timedelta):
return t
if isinstance(t, self.__class__):
return t
return self.from_datetime(t) # We want to return EWSDateTime objects

def __isub__(self, other):
return self - other

@classmethod
def from_string(cls, date_string):
# Parses several common datetime formats and returns time zone aware EWSDateTime objects
if date_string.endswith("Z"):
# UTC datetime
return super().strptime(date_string, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
if len(date_string) == 19:
# This is probably a naive datetime. Don't allow this, but signal caller with an appropriate error
local_dt = super().strptime(date_string, "%Y-%m-%dT%H:%M:%S")
raise NaiveDateTimeNotAllowed(local_dt)
# This is probably a datetime value with time zone information. This comes in the form '+/-HH:MM'.
aware_dt = datetime.datetime.fromisoformat(date_string).astimezone(UTC).replace(tzinfo=UTC)
if isinstance(aware_dt, cls):
return aware_dt
return cls.from_datetime(aware_dt)

@classmethod
def fromtimestamp(cls, t, tz=None):
dt = super().fromtimestamp(t, tz=tz)
if isinstance(dt, cls):
return dt
return cls.from_datetime(dt) # We want to return EWSDateTime objects

@classmethod
def utcfromtimestamp(cls, t):
dt = super().utcfromtimestamp(t)
if isinstance(dt, cls):
return dt
return cls.from_datetime(dt) # We want to return EWSDateTime objects

@classmethod
def now(cls, tz=None):
t = super().now(tz=tz)
if isinstance(t, cls):
return t
return cls.from_datetime(t) # We want to return EWSDateTime objects

@classmethod
def utcnow(cls):
t = super().utcnow()
if isinstance(t, cls):
return t
return cls.from_datetime(t) # We want to return EWSDateTime objects

def date(self):
d = super().date()
if isinstance(d, EWSDate):
return d
return EWSDate.from_date(d) # We want to return EWSDate objects
```

Extends the normal datetime implementation to satisfy EWS.

### Ancestors

* datetime.datetime
* datetime.date

### Static methods

```
def from_datetime(d)
```

```
def from_string(date_string)
```

```
def fromisoformat(date_string)
```

string -> datetime from a string in most ISO 8601 formats

```
def fromtimestamp(t, tz=None)
```

timestamp[, tz] -> tz's local time from POSIX timestamp.

```
def now(tz=None)
```

Returns new datetime object representing current time local to tz.

tz Timezone object.

If no tz is specified, uses local timezone.

```
def utcfromtimestamp(t)
```

Construct a naive UTC datetime from a POSIX timestamp.

```
def utcnow()
```

Return a new datetime representing UTC day and time.

### Methods

```
def astimezone(self, tz=None)
```

Expand source code
```
def astimezone(self, tz=None):
if tz is None:
tz = EWSTimeZone.localzone()
t = super().astimezone(tz=tz).replace(tzinfo=tz)
if isinstance(t, self.__class__):
return t
return self.from_datetime(t) # We want to return EWSDateTime objects
```

tz -> convert to local time in new timezone tz

```
def date(self)
```

Expand source code
```
def date(self):
d = super().date()
if isinstance(d, EWSDate):
return d
return EWSDate.from_date(d) # We want to return EWSDate objects
```

Return date object with same year, month and day.

```
def ewsformat(self)
```

Expand source code
```
def ewsformat(self):
"""ISO 8601 format to satisfy xs:datetime as interpreted by EWS. Examples:
* 2009-01-15T13:45:56Z
* 2009-01-15T13:45:56+01:00
"""
if not self.tzinfo:
raise ValueError(f"{self!r} must be timezone-aware")
if self.tzinfo.key == "UTC":
if self.microsecond:
return self.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
return self.strftime("%Y-%m-%dT%H:%M:%SZ")
return self.isoformat()
```

ISO 8601 format to satisfy xs:datetime as interpreted by EWS. Examples: * 2009-01-15T13:45:56Z * 2009-01-15T13:45:56+01:00

```
class EWSTimeZone
(*args, **kwargs)
```

Expand source code
```
class EWSTimeZone(zoneinfo.ZoneInfo):
"""Represents a time zone as expected by the EWS TimezoneContext / TimezoneDefinition XML element, and returned by
services.GetServerTimeZones.
"""

IANA_TO_MS_MAP = IANA_TO_MS_TIMEZONE_MAP
MS_TO_IANA_MAP = MS_TIMEZONE_TO_IANA_MAP

def __new__(cls, *args, **kwargs):
try:
instance = super().__new__(cls, *args, **kwargs)
except zoneinfo.ZoneInfoNotFoundError as e:
raise UnknownTimeZone(e.args[0])
try:
instance.ms_id = cls.IANA_TO_MS_MAP[instance.key][0]
except KeyError:
raise UnknownTimeZone(f"No Windows timezone name found for timezone {instance.key!r}")

# We don't need the Windows long-format time zone name in long format. It's used in time zone XML elements, but
# EWS happily accepts empty strings. For a full list of time zones supported by the target server, including
# long-format names, see output of services.GetServerTimeZones(account.protocol).call()
instance.ms_name = ""
return instance

def __hash__(self):
return hash(self.key)

def __eq__(self, other):
# Microsoft time zones are less granular than IANA, so an EWSTimeZone created from 'Europe/Copenhagen' may
# return from the server as 'Europe/Copenhagen'. We're catering for Microsoft here, so base equality on the
# Microsoft time zone ID.
if not isinstance(other, self.__class__):
return NotImplemented
return self.ms_id == other.ms_id

@classmethod
def from_ms_id(cls, ms_id):
# Create a time zone instance from a Microsoft time zone ID. This is lossy because there is not a 1:1
# translation from MS time zone ID to IANA time zone.
try:
return cls(cls.MS_TO_IANA_MAP[ms_id])
except KeyError:
if "/" in ms_id:
# EWS sometimes returns an ID that has a region/location format, e.g. 'Europe/Copenhagen'. Try the
# string unaltered.
return cls(ms_id)
raise UnknownTimeZone(f"Windows timezone ID {ms_id!r} is unknown by CLDR")

@classmethod
def from_pytz(cls, tz):
return cls(tz.zone)

@classmethod
def from_datetime(cls, tz):
"""Convert from a standard library `datetime.timezone` instance."""
return cls(tz.tzname(None))

@classmethod
def from_dateutil(cls, tz):
# Objects returned by dateutil.tz.tzlocal() and dateutil.tz.gettz() are not supported. They
# don't contain enough information to reliably match them with a CLDR time zone.
if hasattr(tz, "_filename"):
key = "/".join(tz._filename.split("/")[-2:])
return cls(key)
return cls(tz.tzname(datetime.datetime.now()))

@classmethod
def from_zoneinfo(cls, tz):
return cls(tz.key)

@classmethod
def from_timezone(cls, tz):
# Support multiple tzinfo implementations. We could use isinstance(), but then we'd have to have pytz
# and dateutil as dependencies for this package.
tz_module = tz.__class__.__module__.split(".")[0]
try:
return {
cls.__module__.split(".")[0]: lambda z: z,
"datetime": cls.from_datetime,
"dateutil": cls.from_dateutil,
"pytz": cls.from_pytz,
"zoneinfo": cls.from_zoneinfo,
"pytz_deprecation_shim": lambda z: cls.from_timezone(z.unwrap_shim()),
}[tz_module](tz)
except KeyError:
raise TypeError(f"Unsupported tzinfo type: {tz!r}")

@classmethod
def localzone(cls):
try:
tz = tzlocal.get_localzone()
except zoneinfo.ZoneInfoNotFoundError:
# Older versions of tzlocal will raise a pytz exception. Let's not depend on pytz just for that.
raise UnknownTimeZone("Failed to guess local timezone")
# Handle both old and new versions of tzlocal that may return pytz or zoneinfo objects, respectively
return cls.from_timezone(tz)

def fromutc(self, dt):
t = super().fromutc(dt)
if isinstance(t, EWSDateTime):
return t
return EWSDateTime.from_datetime(t) # We want to return EWSDateTime objects
```

Represents a time zone as expected by the EWS TimezoneContext / TimezoneDefinition XML element, and returned by services.GetServerTimeZones.

### Ancestors

* zoneinfo.ZoneInfo
* datetime.tzinfo

### Class variables

`var IANA_TO_MS_MAP`
The type of the None singleton.

`var MS_TO_IANA_MAP`
The type of the None singleton.

### Static methods

```
def from_datetime(tz)
```

Convert from a standard library `datetime.timezone` instance.

```
def from_dateutil(tz)
```

```
def from_ms_id(ms_id)
```

```
def from_pytz(tz)
```

```
def from_timezone(tz)
```

```
def from_zoneinfo(tz)
```

```
def localzone()
```

### Methods

```
def fromutc(self, dt)
```

Expand source code
```
def fromutc(self, dt):
t = super().fromutc(dt)
if isinstance(t, EWSDateTime):
return t
return EWSDateTime.from_datetime(t) # We want to return EWSDateTime objects
```

Given a datetime with local time in UTC, retrieve an adjusted datetime in local time.

```
class ExtendedProperty
(*args, **kwargs)
```

Expand source code
```
class ExtendedProperty(EWSElement):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/extendedproperty"""

ELEMENT_NAME = "ExtendedProperty"

# Enum values: https://docs.microsoft.com/en-us/dotnet/api/exchangewebservices.distinguishedpropertysettype
DISTINGUISHED_SETS = {
"Address",
"Appointment",
"CalendarAssistant",
"Common",
"InternetHeaders",
"Meeting",
"PublicStrings",
"Sharing",
"Task",
"UnifiedMessaging",
}
# Enum values: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/extendedfielduri
# The following types cannot be used for setting or getting (see docs) and are thus not very useful here:
# 'Error'
# 'Null'
# 'Object'
# 'ObjectArray'
PROPERTY_TYPES = {
"ApplicationTime",
"Binary",
"BinaryArray",
"Boolean",
"CLSID",
"CLSIDArray",
"Currency",
"CurrencyArray",
"Double",
"DoubleArray",
"Float",
"FloatArray",
"Integer",
"IntegerArray",
"Long",
"LongArray",
"Short",
"ShortArray",
"SystemTime",
"SystemTimeArray",
"String",
"StringArray",
}

# Translation table between common distinguished_property_set_id and property_set_id values. See
# https://docs.microsoft.com/en-us/office/client-developer/outlook/mapi/commonly-used-property-sets
# ID values must be lowercase.
DISTINGUISHED_SET_NAME_TO_ID_MAP = {
"Address": "00062004-0000-0000-c000-000000000046",
"AirSync": "71035549-0739-4dcb-9163-00f0580dbbdf",
"Appointment": "00062002-0000-0000-c000-000000000046",
"Common": "00062008-0000-0000-c000-000000000046",
"InternetHeaders": "00020386-0000-0000-c000-000000000046",
"Log": "0006200a-0000-0000-c000-000000000046",
"Mapi": "00020328-0000-0000-c000-000000000046",
"Meeting": "6ed8da90-450b-101b-98da-00aa003f1305",
"Messaging": "41f28f13-83f4-4114-a584-eedb5a6b0bff",
"Note": "0006200e-0000-0000-c000-000000000046",
"PostRss": "00062041-0000-0000-c000-000000000046",
"PublicStrings": "00020329-0000-0000-c000-000000000046",
"Remote": "00062014-0000-0000-c000-000000000046",
"Report": "00062013-0000-0000-c000-000000000046",
"Sharing": "00062040-0000-0000-c000-000000000046",
"Task": "00062003-0000-0000-c000-000000000046",
"UnifiedMessaging": "4442858e-a9e3-4e80-b900-317a210cc15b",
}
DISTINGUISHED_SET_ID_TO_NAME_MAP = {v: k for k, v in DISTINGUISHED_SET_NAME_TO_ID_MAP.items()}

distinguished_property_set_id = None
property_set_id = None
property_tag = None # hex integer (e.g. 0x8000) or string ('0x8000')
property_name = None
property_id = None # integer as hex-formatted int (e.g. 0x8000) or normal int (32768)
property_type = ""

__slots__ = ("value",)

def __init__(self, *args, **kwargs):
if not kwargs:
# Allow to set attributes without keyword
kwargs = dict(zip(self._slots_keys, args))
self.value = kwargs.pop("value")
super().__init__(**kwargs)

@classmethod
def validate_cls(cls):
# Validate values of class attributes and their interdependencies
cls._validate_distinguished_property_set_id()
cls._validate_property_set_id()
cls._validate_property_tag()
cls._validate_property_name()
cls._validate_property_id()
cls._validate_property_type()

@classmethod
def _validate_distinguished_property_set_id(cls):
if cls.distinguished_property_set_id:
if any([cls.property_set_id, cls.property_tag]):
raise ValueError(
"When 'distinguished_property_set_id' is set, 'property_set_id' and 'property_tag' must be None"
)
if not any([cls.property_id, cls.property_name]):
raise ValueError(
"When 'distinguished_property_set_id' is set, 'property_id' or 'property_name' must also be set"
)
if cls.distinguished_property_set_id not in cls.DISTINGUISHED_SETS:
raise InvalidEnumValue(
"distinguished_property_set_id", cls.distinguished_property_set_id, cls.DISTINGUISHED_SETS
)

@classmethod
def _validate_property_set_id(cls):
if cls.property_set_id:
if any([cls.distinguished_property_set_id, cls.property_tag]):
raise ValueError(
"When 'property_set_id' is set, 'distinguished_property_set_id' and 'property_tag' must be None"
)
if not any([cls.property_id, cls.property_name]):
raise ValueError("When 'property_set_id' is set, 'property_id' or 'property_name' must also be set")

@classmethod
def _validate_property_tag(cls):
if cls.property_tag:
if any([cls.distinguished_property_set_id, cls.property_set_id, cls.property_name, cls.property_id]):
raise ValueError("When 'property_tag' is set, only 'property_type' must be set")
if 0x8000 <= cls.property_tag_as_int() <= 0xFFFE:
raise ValueError(
f"'property_tag' value {cls.property_tag_as_hex()!r} is reserved for custom properties"
)

@classmethod
def _validate_property_name(cls):
if cls.property_name:
if any([cls.property_id, cls.property_tag]):
raise ValueError("When 'property_name' is set, 'property_id' and 'property_tag' must be None")
if not any([cls.distinguished_property_set_id, cls.property_set_id]):
raise ValueError(
"When 'property_name' is set, 'distinguished_property_set_id' or 'property_set_id' must also be set"
)

@classmethod
def _validate_property_id(cls):
if cls.property_id:
if any([cls.property_name, cls.property_tag]):
raise ValueError("When 'property_id' is set, 'property_name' and 'property_tag' must be None")
if not any([cls.distinguished_property_set_id, cls.property_set_id]):
raise ValueError(
"When 'property_id' is set, 'distinguished_property_set_id' or 'property_set_id' must also be set"
)

@classmethod
def _validate_property_type(cls):
if cls.property_type not in cls.PROPERTY_TYPES:
raise InvalidEnumValue("property_type", cls.property_type, cls.PROPERTY_TYPES)

def clean(self, version=None):
self.validate_cls()
python_type = self.python_type()
if self.is_array_type():
if not is_iterable(self.value):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {list}")
for v in self.value:
if not isinstance(v, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} list value {v!r} must be of type {python_type}")
else:
if not isinstance(self.value, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {python_type}")

@classmethod
def _normalize_obj(cls, obj):
# Sometimes, EWS will helpfully translate a 'distinguished_property_set_id' value to a 'property_set_id' value
# and vice versa. Align these values on an ExtendedFieldURI instance.
try:
obj.property_set_id = cls.DISTINGUISHED_SET_NAME_TO_ID_MAP[obj.distinguished_property_set_id]
except KeyError:
with suppress(KeyError):
obj.distinguished_property_set_id = cls.DISTINGUISHED_SET_ID_TO_NAME_MAP[obj.property_set_id]
return obj

@classmethod
def is_property_instance(cls, elem):
"""Return whether an 'ExtendedProperty' element matches the definition for this class. Extended property fields
do not have a name, so we must match on the cls.property_* attributes to match a field in the request with a
field in the response.
"""
# We can't use ExtendedFieldURI.from_xml(). It clears the XML element, but we may not want to consume it here.
kwargs = {
f.name: f.from_xml(elem=elem.find(ExtendedFieldURI.response_tag()), account=None)
for f in ExtendedFieldURI.FIELDS
}
xml_obj = ExtendedFieldURI(**kwargs)
cls_obj = cls.as_object()
return cls._normalize_obj(cls_obj) == cls._normalize_obj(xml_obj)

@classmethod
def from_xml(cls, elem, account):
# Gets value of this specific ExtendedProperty from a list of 'ExtendedProperty' XML elements
python_type = cls.python_type()
if cls.is_array_type():
values = elem.find(f"{{{TNS}}}Values")
return [
xml_text_to_value(value=val, value_type=python_type) for val in get_xml_attrs(values, f"{{{TNS}}}Value")
]
extended_field_value = xml_text_to_value(value=get_xml_attr(elem, f"{{{TNS}}}Value"), value_type=python_type)
if python_type == str and not extended_field_value:
# For string types, we want to return the empty string instead of None if the element was
# actually found, but there was no XML value. For other types, it would be more problematic
# to make that distinction, e.g. return False for bool, 0 for int, etc.
return ""
return extended_field_value

def to_xml(self, version):
if self.is_array_type():
values = create_element("t:Values")
for v in self.value:
add_xml_child(values, "t:Value", v)
return values
return set_xml_value(create_element("t:Value"), self.value, version=version)

@classmethod
def is_array_type(cls):
return cls.property_type.endswith("Array")

@classmethod
def property_tag_as_int(cls):
if isinstance(cls.property_tag, str):
return int(cls.property_tag, base=16)
return cls.property_tag

@classmethod
def property_tag_as_hex(cls):
return hex(cls.property_tag) if isinstance(cls.property_tag, int) else cls.property_tag

@classmethod
def python_type(cls):
# Return the best equivalent for a Python type for the property type of this class
base_type = cls.property_type[:-5] if cls.is_array_type() else cls.property_type
return {
"ApplicationTime": Decimal,
"Binary": bytes,
"Boolean": bool,
"CLSID": str,
"Currency": int,
"Double": Decimal,
"Float": Decimal,
"Integer": int,
"Long": int,
"Short": int,
"SystemTime": EWSDateTime,
"String": str,
}[base_type]

@classmethod
def as_object(cls):
# Return an object we can use to match with the incoming object from XML
return ExtendedFieldURI(
distinguished_property_set_id=cls.distinguished_property_set_id,
property_set_id=cls.property_set_id.lower() if cls.property_set_id else None,
property_tag=cls.property_tag_as_hex(),
property_name=cls.property_name,
property_id=value_to_xml_text(cls.property_id) if cls.property_id else None,
property_type=cls.property_type,
)
```

### Ancestors

* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Subclasses

* [ExternId](https://ecederstrand.github.io/exchangelib/exchangelib/extended_properties.html#exchangelib.extended_properties.ExternId "exchangelib.extended_properties.ExternId")
* [Flag](https://ecederstrand.github.io/exchangelib/exchangelib/extended_properties.html#exchangelib.extended_properties.Flag "exchangelib.extended_properties.Flag")

### Class variables

`var DISTINGUISHED_SETS`
The type of the None singleton.

`var DISTINGUISHED_SET_ID_TO_NAME_MAP`
The type of the None singleton.

`var DISTINGUISHED_SET_NAME_TO_ID_MAP`
The type of the None singleton.

`var PROPERTY_TYPES`
The type of the None singleton.

`var distinguished_property_set_id`
The type of the None singleton.

`var property_id`
The type of the None singleton.

`var property_name`
The type of the None singleton.

`var property_set_id`
The type of the None singleton.

`var property_tag`
The type of the None singleton.

`var property_type`
The type of the None singleton.

### Static methods

```
def as_object()
```

```
def from_xml(elem, account)
```

```
def is_array_type()
```

```
def is_property_instance(elem)
```

Return whether an 'ExtendedProperty' element matches the definition for this class. Extended property fields do not have a name, so we must match on the cls.property_* attributes to match a field in the request with a field in the response.

```
def property_tag_as_hex()
```

```
def property_tag_as_int()
```

```
def python_type()
```

```
def validate_cls()
```

### Instance variables

`var value`

Expand source code
```
class ExtendedProperty(EWSElement):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/extendedproperty"""

ELEMENT_NAME = "ExtendedProperty"

# Enum values: https://docs.microsoft.com/en-us/dotnet/api/exchangewebservices.distinguishedpropertysettype
DISTINGUISHED_SETS = {
"Address",
"Appointment",
"CalendarAssistant",
"Common",
"InternetHeaders",
"Meeting",
"PublicStrings",
"Sharing",
"Task",
"UnifiedMessaging",
}
# Enum values: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/extendedfielduri
# The following types cannot be used for setting or getting (see docs) and are thus not very useful here:
# 'Error'
# 'Null'
# 'Object'
# 'ObjectArray'
PROPERTY_TYPES = {
"ApplicationTime",
"Binary",
"BinaryArray",
"Boolean",
"CLSID",
"CLSIDArray",
"Currency",
"CurrencyArray",
"Double",
"DoubleArray",
"Float",
"FloatArray",
"Integer",
"IntegerArray",
"Long",
"LongArray",
"Short",
"ShortArray",
"SystemTime",
"SystemTimeArray",
"String",
"StringArray",
}

# Translation table between common distinguished_property_set_id and property_set_id values. See
# https://docs.microsoft.com/en-us/office/client-developer/outlook/mapi/commonly-used-property-sets
# ID values must be lowercase.
DISTINGUISHED_SET_NAME_TO_ID_MAP = {
"Address": "00062004-0000-0000-c000-000000000046",
"AirSync": "71035549-0739-4dcb-9163-00f0580dbbdf",
"Appointment": "00062002-0000-0000-c000-000000000046",
"Common": "00062008-0000-0000-c000-000000000046",
"InternetHeaders": "00020386-0000-0000-c000-000000000046",
"Log": "0006200a-0000-0000-c000-000000000046",
"Mapi": "00020328-0000-0000-c000-000000000046",
"Meeting": "6ed8da90-450b-101b-98da-00aa003f1305",
"Messaging": "41f28f13-83f4-4114-a584-eedb5a6b0bff",
"Note": "0006200e-0000-0000-c000-000000000046",
"PostRss": "00062041-0000-0000-c000-000000000046",
"PublicStrings": "00020329-0000-0000-c000-000000000046",
"Remote": "00062014-0000-0000-c000-000000000046",
"Report": "00062013-0000-0000-c000-000000000046",
"Sharing": "00062040-0000-0000-c000-000000000046",
"Task": "00062003-0000-0000-c000-000000000046",
"UnifiedMessaging": "4442858e-a9e3-4e80-b900-317a210cc15b",
}
DISTINGUISHED_SET_ID_TO_NAME_MAP = {v: k for k, v in DISTINGUISHED_SET_NAME_TO_ID_MAP.items()}

distinguished_property_set_id = None
property_set_id = None
property_tag = None # hex integer (e.g. 0x8000) or string ('0x8000')
property_name = None
property_id = None # integer as hex-formatted int (e.g. 0x8000) or normal int (32768)
property_type = ""

__slots__ = ("value",)

def __init__(self, *args, **kwargs):
if not kwargs:
# Allow to set attributes without keyword
kwargs = dict(zip(self._slots_keys, args))
self.value = kwargs.pop("value")
super().__init__(**kwargs)

@classmethod
def validate_cls(cls):
# Validate values of class attributes and their interdependencies
cls._validate_distinguished_property_set_id()
cls._validate_property_set_id()
cls._validate_property_tag()
cls._validate_property_name()
cls._validate_property_id()
cls._validate_property_type()

@classmethod
def _validate_distinguished_property_set_id(cls):
if cls.distinguished_property_set_id:
if any([cls.property_set_id, cls.property_tag]):
raise ValueError(
"When 'distinguished_property_set_id' is set, 'property_set_id' and 'property_tag' must be None"
)
if not any([cls.property_id, cls.property_name]):
raise ValueError(
"When 'distinguished_property_set_id' is set, 'property_id' or 'property_name' must also be set"
)
if cls.distinguished_property_set_id not in cls.DISTINGUISHED_SETS:
raise InvalidEnumValue(
"distinguished_property_set_id", cls.distinguished_property_set_id, cls.DISTINGUISHED_SETS
)

@classmethod
def _validate_property_set_id(cls):
if cls.property_set_id:
if any([cls.distinguished_property_set_id, cls.property_tag]):
raise ValueError(
"When 'property_set_id' is set, 'distinguished_property_set_id' and 'property_tag' must be None"
)
if not any([cls.property_id, cls.property_name]):
raise ValueError("When 'property_set_id' is set, 'property_id' or 'property_name' must also be set")

@classmethod
def _validate_property_tag(cls):
if cls.property_tag:
if any([cls.distinguished_property_set_id, cls.property_set_id, cls.property_name, cls.property_id]):
raise ValueError("When 'property_tag' is set, only 'property_type' must be set")
if 0x8000 <= cls.property_tag_as_int() <= 0xFFFE:
raise ValueError(
f"'property_tag' value {cls.property_tag_as_hex()!r} is reserved for custom properties"
)

@classmethod
def _validate_property_name(cls):
if cls.property_name:
if any([cls.property_id, cls.property_tag]):
raise ValueError("When 'property_name' is set, 'property_id' and 'property_tag' must be None")
if not any([cls.distinguished_property_set_id, cls.property_set_id]):
raise ValueError(
"When 'property_name' is set, 'distinguished_property_set_id' or 'property_set_id' must also be set"
)

@classmethod
def _validate_property_id(cls):
if cls.property_id:
if any([cls.property_name, cls.property_tag]):
raise ValueError("When 'property_id' is set, 'property_name' and 'property_tag' must be None")
if not any([cls.distinguished_property_set_id, cls.property_set_id]):
raise ValueError(
"When 'property_id' is set, 'distinguished_property_set_id' or 'property_set_id' must also be set"
)

@classmethod
def _validate_property_type(cls):
if cls.property_type not in cls.PROPERTY_TYPES:
raise InvalidEnumValue("property_type", cls.property_type, cls.PROPERTY_TYPES)

def clean(self, version=None):
self.validate_cls()
python_type = self.python_type()
if self.is_array_type():
if not is_iterable(self.value):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {list}")
for v in self.value:
if not isinstance(v, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} list value {v!r} must be of type {python_type}")
else:
if not isinstance(self.value, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {python_type}")

@classmethod
def _normalize_obj(cls, obj):
# Sometimes, EWS will helpfully translate a 'distinguished_property_set_id' value to a 'property_set_id' value
# and vice versa. Align these values on an ExtendedFieldURI instance.
try:
obj.property_set_id = cls.DISTINGUISHED_SET_NAME_TO_ID_MAP[obj.distinguished_property_set_id]
except KeyError:
with suppress(KeyError):
obj.distinguished_property_set_id = cls.DISTINGUISHED_SET_ID_TO_NAME_MAP[obj.property_set_id]
return obj

@classmethod
def is_property_instance(cls, elem):
"""Return whether an 'ExtendedProperty' element matches the definition for this class. Extended property fields
do not have a name, so we must match on the cls.property_* attributes to match a field in the request with a
field in the response.
"""
# We can't use ExtendedFieldURI.from_xml(). It clears the XML element, but we may not want to consume it here.
kwargs = {
f.name: f.from_xml(elem=elem.find(ExtendedFieldURI.response_tag()), account=None)
for f in ExtendedFieldURI.FIELDS
}
xml_obj = ExtendedFieldURI(**kwargs)
cls_obj = cls.as_object()
return cls._normalize_obj(cls_obj) == cls._normalize_obj(xml_obj)

@classmethod
def from_xml(cls, elem, account):
# Gets value of this specific ExtendedProperty from a list of 'ExtendedProperty' XML elements
python_type = cls.python_type()
if cls.is_array_type():
values = elem.find(f"{{{TNS}}}Values")
return [
xml_text_to_value(value=val, value_type=python_type) for val in get_xml_attrs(values, f"{{{TNS}}}Value")
]
extended_field_value = xml_text_to_value(value=get_xml_attr(elem, f"{{{TNS}}}Value"), value_type=python_type)
if python_type == str and not extended_field_value:
# For string types, we want to return the empty string instead of None if the element was
# actually found, but there was no XML value. For other types, it would be more problematic
# to make that distinction, e.g. return False for bool, 0 for int, etc.
return ""
return extended_field_value

def to_xml(self, version):
if self.is_array_type():
values = create_element("t:Values")
for v in self.value:
add_xml_child(values, "t:Value", v)
return values
return set_xml_value(create_element("t:Value"), self.value, version=version)

@classmethod
def is_array_type(cls):
return cls.property_type.endswith("Array")

@classmethod
def property_tag_as_int(cls):
if isinstance(cls.property_tag, str):
return int(cls.property_tag, base=16)
return cls.property_tag

@classmethod
def property_tag_as_hex(cls):
return hex(cls.property_tag) if isinstance(cls.property_tag, int) else cls.property_tag

@classmethod
def python_type(cls):
# Return the best equivalent for a Python type for the property type of this class
base_type = cls.property_type[:-5] if cls.is_array_type() else cls.property_type
return {
"ApplicationTime": Decimal,
"Binary": bytes,
"Boolean": bool,
"CLSID": str,
"Currency": int,
"Double": Decimal,
"Float": Decimal,
"Integer": int,
"Long": int,
"Short": int,
"SystemTime": EWSDateTime,
"String": str,
}[base_type]

@classmethod
def as_object(cls):
# Return an object we can use to match with the incoming object from XML
return ExtendedFieldURI(
distinguished_property_set_id=cls.distinguished_property_set_id,
property_set_id=cls.property_set_id.lower() if cls.property_set_id else None,
property_tag=cls.property_tag_as_hex(),
property_name=cls.property_name,
property_id=value_to_xml_text(cls.property_id) if cls.property_id else None,
property_type=cls.property_type,
)
```

### Methods

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
self.validate_cls()
python_type = self.python_type()
if self.is_array_type():
if not is_iterable(self.value):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {list}")
for v in self.value:
if not isinstance(v, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} list value {v!r} must be of type {python_type}")
else:
if not isinstance(self.value, python_type):
raise TypeError(f"Field {self.__class__.__name__!r} value {self.value!r} must be of type {python_type}")
```

```
def to_xml(self, version)
```

Expand source code
```
def to_xml(self, version):
if self.is_array_type():
values = create_element("t:Values")
for v in self.value:
add_xml_child(values, "t:Value", v)
return values
return set_xml_value(create_element("t:Value"), self.value, version=version)
```

### Inherited members

* `EWSElement`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class FailFast
```

Expand source code
```
class FailFast(RetryPolicy):
"""Fail immediately on server errors."""

@property
def fail_fast(self):
return True

@property
def back_off_until(self):
return None

def back_off(self, seconds):
raise ValueError("Cannot back off with fail-fast policy")
```

Fail immediately on server errors.

### Ancestors

* [RetryPolicy](https://ecederstrand.github.io/exchangelib/exchangelib/protocol.html#exchangelib.protocol.RetryPolicy "exchangelib.protocol.RetryPolicy")

### Inherited members

* `RetryPolicy`:
* `back_off`
* `back_off_until`
* `fail_fast`

```
class FaultTolerance
(max_wait=3600)
```

Expand source code
```
class FaultTolerance(RetryPolicy):
"""Enables fault-tolerant error handling. Tells internal methods to do an exponential back off when requests start
failing, and wait up to max_wait seconds before failing.
"""

# Back off 60 seconds if we didn't get an explicit suggested value
DEFAULT_BACKOFF = 60

def __init__(self, max_wait=3600):
self.max_wait = max_wait
self._back_off_until = None
self._back_off_lock = Lock()

def __getstate__(self):
# Locks cannot be pickled
state = self.__dict__.copy()
del state["_back_off_lock"]
return state

def __setstate__(self, state):
# Restore the lock
self.__dict__.update(state)
self._back_off_lock = Lock()

@property
def fail_fast(self):
return False

@property
def back_off_until(self):
"""Return the back off value as a datetime. Reset the current back off value if it has expired."""
if self._back_off_until is None:
return None
with self._back_off_lock:
if self._back_off_until is None:
return None
if self._back_off_until < datetime.datetime.now():
self._back_off_until = None # The back off value has expired. Reset
return None
return self._back_off_until

@back_off_until.setter
def back_off_until(self, value):
with self._back_off_lock:
self._back_off_until = value

def back_off(self, seconds):
if seconds is None:
seconds = self.DEFAULT_BACKOFF
if seconds > self.max_wait:
# We lost patience. Session is cleaned up in outer loop
raise RateLimitError("Max timeout reached", wait=seconds)
value = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
with self._back_off_lock:
self._back_off_until = value

def raise_response_errors(self, response):
try:
return super().raise_response_errors(response)
except (ErrorInternalServerTransientError, ErrorServerBusy) as e:
# Pass on the retry header value
retry_after = _get_retry_after(response)
if retry_after:
raise ErrorServerBusy(e.args[0], back_off=retry_after)
raise
```

Enables fault-tolerant error handling. Tells internal methods to do an exponential back off when requests start failing, and wait up to max_wait seconds before failing.

### Ancestors

* [RetryPolicy](https://ecederstrand.github.io/exchangelib/exchangelib/protocol.html#exchangelib.protocol.RetryPolicy "exchangelib.protocol.RetryPolicy")

### Class variables

`var DEFAULT_BACKOFF`
The type of the None singleton.

### Instance variables

`prop back_off_until`

Expand source code
```
@property
def back_off_until(self):
"""Return the back off value as a datetime. Reset the current back off value if it has expired."""
if self._back_off_until is None:
return None
with self._back_off_lock:
if self._back_off_until is None:
return None
if self._back_off_until < datetime.datetime.now():
self._back_off_until = None # The back off value has expired. Reset
return None
return self._back_off_until
```

Return the back off value as a datetime. Reset the current back off value if it has expired.

### Methods

```
def raise_response_errors(self, response)
```

Expand source code
```
def raise_response_errors(self, response):
try:
return super().raise_response_errors(response)
except (ErrorInternalServerTransientError, ErrorServerBusy) as e:
# Pass on the retry header value
retry_after = _get_retry_after(response)
if retry_after:
raise ErrorServerBusy(e.args[0], back_off=retry_after)
raise
```

### Inherited members

* `RetryPolicy`:
* `back_off`
* `fail_fast`

```
class FileAttachment
(**kwargs)
```

Expand source code
```
class FileAttachment(Attachment):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/fileattachment"""

ELEMENT_NAME = "FileAttachment"

is_contact_photo = BooleanField(field_uri="IsContactPhoto")
_content = Base64Field(field_uri="Content")

__slots__ = ("_fp",)

def __init__(self, **kwargs):
kwargs["_content"] = kwargs.pop("content", None)
super().__init__(**kwargs)
self._fp = None

@property
def fp(self):
# Return a file-like object for the content. This avoids creating multiple in-memory copies of the content.
if self._fp is None:
self._init_fp()
return self._fp

def _init_fp(self):
# Create a file-like object for the attachment content. We try hard to reduce memory consumption, so we never
# store the full attachment content in-memory.
if not self.parent_item or not self.parent_item.account:
raise ValueError(f"{self.__class__.__name__} must have an account")
self._fp = FileAttachmentIO(attachment=self)

@property
def content(self):
"""Return the attachment content. Stores a local copy of the content in case you want to upload the attachment
again later.
"""
if self.attachment_id is None:
return self._content
if self._content is not None:
return self._content
# We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
with self.fp as fp:
self._content = fp.read()
return self._content

@content.setter
def content(self, value):
"""Replace the attachment content."""
if not isinstance(value, bytes):
raise InvalidTypeError("value", value, bytes)
self._content = value

@classmethod
def from_xml(cls, elem, account):
kwargs = {f.name: f.from_xml(elem=elem, account=account) for f in cls.FIELDS}
kwargs["content"] = kwargs.pop("_content")
cls._clear(elem)
return cls(**kwargs)

def to_xml(self, version):
self._content = self.content # Make sure content is available, to avoid ErrorRequiredPropertyMissing
return super().to_xml(version=version)

def __getstate__(self):
# The fp does not need to be pickled
state = {k: getattr(self, k) for k in self._slots_keys}
del state["_fp"]
return state

def __setstate__(self, state):
# Restore the fp
for k in self._slots_keys:
setattr(self, k, state.get(k))
self._fp = None
```

### Ancestors

* [Attachment](https://ecederstrand.github.io/exchangelib/exchangelib/attachments.html#exchangelib.attachments.Attachment "exchangelib.attachments.Attachment")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Static methods

```
def from_xml(elem, account)
```

### Instance variables

`prop content`

Expand source code
```
@property
def content(self):
"""Return the attachment content. Stores a local copy of the content in case you want to upload the attachment
again later.
"""
if self.attachment_id is None:
return self._content
if self._content is not None:
return self._content
# We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
with self.fp as fp:
self._content = fp.read()
return self._content
```

Return the attachment content. Stores a local copy of the content in case you want to upload the attachment again later.

`prop fp`

Expand source code
```
@property
def fp(self):
# Return a file-like object for the content. This avoids creating multiple in-memory copies of the content.
if self._fp is None:
self._init_fp()
return self._fp
```

`var is_contact_photo`
The type of the None singleton.

### Methods

```
def to_xml(self, version)
```

Expand source code
```
def to_xml(self, version):
self._content = self.content # Make sure content is available, to avoid ErrorRequiredPropertyMissing
return super().to_xml(version=version)
```

### Inherited members

* `Attachment`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `attachment_id`
* `content_id`
* `content_location`
* `content_type`
* `is_inline`
* `last_modified_time`
* `name`
* `remove_field`
* `size`
* `supported_fields`
* `validate_field`

```
class Folder
(**kwargs)
```

Expand source code
```
class Folder(BaseFolder):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/folder"""

permission_set = PermissionSetField(field_uri="folder:PermissionSet", supported_from=EXCHANGE_2007_SP1)
effective_rights = EffectiveRightsField(
field_uri="folder:EffectiveRights", is_read_only=True, supported_from=EXCHANGE_2007_SP1
)

__slots__ = ("_root",)

def __init__(self, **kwargs):
self._root = kwargs.pop("root", None) # This is a pointer to the root of the folder hierarchy
parent = kwargs.pop("parent", None)
if parent:
if self.root:
if parent.root != self.root:
raise ValueError("'parent.root' must match 'root'")
else:
self._root = parent.root
if "parent_folder_id" in kwargs and parent.id != kwargs["parent_folder_id"]:
raise ValueError("'parent_folder_id' must match 'parent' ID")
kwargs["parent_folder_id"] = ParentFolderId(id=parent.id, changekey=parent.changekey)
super().__init__(**kwargs)

@property
def account(self):
if self.root is None:
return None
return self.root.account

@property
def root(self):
return self._root

@classmethod
def register(cls, *args, **kwargs):
if cls is not Folder:
raise TypeError("For folders, custom fields must be registered on the Folder class")
return super().register(*args, **kwargs)

@classmethod
def deregister(cls, *args, **kwargs):
if cls is not Folder:
raise TypeError("For folders, custom fields must be registered on the Folder class")
return super().deregister(*args, **kwargs)

@property
def parent(self):
if not self.parent_folder_id:
return None
if self.parent_folder_id.id == self.id:
# Some folders have a parent that references itself. Avoid circular references here
return None
return self.root.get_folder(self.parent_folder_id)

@parent.setter
def parent(self, value):
if value is None:
self.parent_folder_id = None
else:
if not isinstance(value, BaseFolder):
raise InvalidTypeError("value", value, BaseFolder)
self._root = value.root
self.parent_folder_id = ParentFolderId(id=value.id, changekey=value.changekey)

def clean(self, version=None):
from .roots import RootOfHierarchy

super().clean(version=version)
if self.root and not isinstance(self.root, RootOfHierarchy):
raise InvalidTypeError("root", self.root, RootOfHierarchy)

@classmethod
def get_distinguished(cls, root):
"""Get the distinguished folder for this folder class.

:param root:
:return:
"""
return cls._get_distinguished(
folder=cls(
_distinguished_id=DistinguishedFolderId(
id=cls.DISTINGUISHED_FOLDER_ID,
mailbox=Mailbox(email_address=root.account.primary_smtp_address),
),
root=root,
)
)

@classmethod
def from_xml_with_root(cls, elem, root):
folder = cls.from_xml(elem=elem, account=root.account)
folder_cls = cls
if cls == Folder:
# We were called on the generic Folder class. Try to find a more specific class to return objects as.
#
# The "FolderClass" element value is the only indication we have in the FindFolder response of which
# folder class we should create the folder with. And many folders share the same 'FolderClass' value, e.g.
# Inbox and DeletedItems. We want to distinguish between these because otherwise we can't locate the right
# folders types for e.g. Account.inbox and Account.trash.
#
# We should be able to just use the name, but apparently default folder names can be renamed to a set of
# localized names using a PowerShell command:
# https://docs.microsoft.com/en-us/powershell/module/exchange/client-access/Set-MailboxRegionalConfiguration
#
# Instead, search for a folder class using the localized name. If none are found, fall back to getting the
# folder class by the "FolderClass" value.
#
# The returned XML may contain neither folder class nor name. In that case, we default to the generic
# Folder class.
if folder.name:
with suppress(KeyError):
# TODO: fld_class.LOCALIZED_NAMES is most definitely neither complete nor authoritative
folder_cls = root.folder_cls_from_folder_name(
folder_name=folder.name,
folder_class=folder.folder_class,
locale=root.account.locale,
)
log.debug("Folder class %s matches localized folder name %s", folder_cls, folder.name)
if folder.folder_class and folder_cls == Folder:
with suppress(KeyError):
folder_cls = cls.folder_cls_from_container_class(container_class=folder.folder_class)
log.debug(
"Folder class %s matches container class %s (%s)", folder_cls, folder.folder_class, folder.name
)
if folder_cls == Folder:
log.debug("Fallback to class Folder (folder_class %s, name %s)", folder.folder_class, folder.name)
# Some servers return folders in a FindFolder result that have a DistinguishedFolderId element that the same
# server cannot handle in a GetFolder request. Only set the DistinguishedFolderId field if we recognize the ID.
if folder._distinguished_id and not folder_cls.DISTINGUISHED_FOLDER_ID:
folder._distinguished_id = None
return folder_cls(root=root, **{f.name: getattr(folder, f.name) for f in folder.FIELDS})
```

### Ancestors

* [BaseFolder](https://ecederstrand.github.io/exchangelib/exchangelib/folders/base.html#exchangelib.folders.base.BaseFolder "exchangelib.folders.base.BaseFolder")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")
* [SearchableMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/queryset.html#exchangelib.queryset.SearchableMixIn "exchangelib.queryset.SearchableMixIn")
* [SupportedVersionClassMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/version.html#exchangelib.version.SupportedVersionClassMixIn "exchangelib.version.SupportedVersionClassMixIn")

### Subclasses

* [Birthdays](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.Birthdays "exchangelib.folders.known_folders.Birthdays")
* [CrawlerData](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.CrawlerData "exchangelib.folders.known_folders.CrawlerData")
* [EventCheckPoints](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.EventCheckPoints "exchangelib.folders.known_folders.EventCheckPoints")
* [FolderMemberships](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.FolderMemberships "exchangelib.folders.known_folders.FolderMemberships")
* [FreeBusyCache](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.FreeBusyCache "exchangelib.folders.known_folders.FreeBusyCache")
* [NonDeletableFolder](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.NonDeletableFolder "exchangelib.folders.known_folders.NonDeletableFolder")
* [RecoveryPoints](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.RecoveryPoints "exchangelib.folders.known_folders.RecoveryPoints")
* [SkypeTeamsMessages](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.SkypeTeamsMessages "exchangelib.folders.known_folders.SkypeTeamsMessages")
* [SwssItems](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.SwssItems "exchangelib.folders.known_folders.SwssItems")
* [WellknownFolder](https://ecederstrand.github.io/exchangelib/exchangelib/folders/known_folders.html#exchangelib.folders.known_folders.WellknownFolder "exchangelib.folders.known_folders.WellknownFolder")

### Static methods

```
def from_xml_with_root(elem, root)
```

```
def get_distinguished(root)
```

Get the distinguished folder for this folder class.

:param root: :return:

### Instance variables

`var effective_rights`
The type of the None singleton.

`var permission_set`
The type of the None singleton.

### Methods

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
from .roots import RootOfHierarchy

super().clean(version=version)
if self.root and not isinstance(self.root, RootOfHierarchy):
raise InvalidTypeError("root", self.root, RootOfHierarchy)
```

### Inherited members

* `BaseFolder`:
* `CONTAINER_CLASS`
* `DEFAULT_FOLDER_TRAVERSAL_DEPTH`
* `DEFAULT_ITEM_TRAVERSAL_DEPTH`
* `DISTINGUISHED_FOLDER_ID`
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `ITEM_MODEL_MAP`
* `LOCALIZED_NAMES`
* `NAMESPACE`
* `account`
* `add_field`
* `all`
* `child_folder_count`
* `deprecated_from`
* `deregister`
* `exclude`
* `filter`
* `folder_class`
* `folder_cls_from_container_class`
* `get`
* `get_events`
* `get_folder_allowed`
* `get_streaming_events`
* `name`
* `none`
* `parent`
* `parent_folder_id`
* `people`
* `register`
* `remove_field`
* `root`
* `subscribe_to_pull`
* `subscribe_to_push`
* `subscribe_to_streaming`
* `supported_fields`
* `supported_from`
* `supported_item_models`
* `sync_hierarchy`
* `sync_items`
* `test_access`
* `total_count`
* `tree`
* `unread_count`
* `unsubscribe`
* `validate_field`

```
class FolderCollection
(account, folders)
```

Expand source code
```
class FolderCollection(SearchableMixIn):
"""A class that implements an API for searching folders."""

# These fields are required in a FindFolder or GetFolder call to properly identify folder types
REQUIRED_FOLDER_FIELDS = ("name", "folder_class")

def __init__(self, account, folders):
"""Implement a search API on a collection of folders.

:param account: An Account object
:param folders: An iterable of folders, e.g. Folder.walk(), Folder.glob(), or [a.calendar, a.inbox]
"""
self.account = account
self._folders = folders

@threaded_cached_property
def folders(self):
# Resolve the list of folders, in case it's a generator
return tuple(self._folders)

def __len__(self):
return len(self.folders)

def __iter__(self):
yield from self.folders

def get(self, *args, **kwargs):
return QuerySet(self).get(*args, **kwargs)

def all(self):
return QuerySet(self).all()

def none(self):
return QuerySet(self).none()

def filter(self, *args, **kwargs):
"""Find items in the folder(s).

Non-keyword args may be a list of Q instances.

Optional extra keyword arguments follow a Django-like QuerySet filter syntax (see
https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups).

We don't support '__year' and other date-related lookups. We also don't support '__endswith' or '__iendswith'.

We support the additional '__not' lookup in place of Django's exclude() for simple cases. For more complicated
cases you need to create a Q object and use ~Q().

Examples:

my_account.inbox.filter(datetime_received__gt=EWSDateTime(2016, 1, 1))
my_account.calendar.filter(start__range=(EWSDateTime(2016, 1, 1), EWSDateTime(2017, 1, 1)))
my_account.tasks.filter(subject='Hi mom')
my_account.tasks.filter(subject__not='Hi mom')
my_account.tasks.filter(subject__contains='Foo')
my_account.tasks.filter(subject__icontains='foo')

'endswith' and 'iendswith' could be emulated by searching with 'contains' or 'icontains' and then
post-processing items. Fetch the field in question with additional_fields and remove items where the search
string is not a postfix.
"""
return QuerySet(self).filter(*args, **kwargs)

def exclude(self, *args, **kwargs):
return QuerySet(self).exclude(*args, **kwargs)

def people(self):
return QuerySet(self).people()

def view(self, start, end, max_items=None):
"""Implement the CalendarView option to FindItem. The difference between 'filter' and 'view' is that 'filter'
only returns the master CalendarItem for recurring items, while 'view' unfolds recurring items and returns all
CalendarItem occurrences as one would normally expect when presenting a calendar.

Supports the same semantics as filter, except for 'start' and 'end' keyword attributes which are both required
and behave differently than filter. Here, they denote the start and end of the timespan of the view. All items
the overlap the timespan are returned (items that end exactly on 'start' are also returned, for some reason).

EWS does not allow combining CalendarView with search restrictions (filter and exclude).

'max_items' defines the maximum number of items returned in this view. Optional.

:param start:
:param end:
:param max_items: (Default value = None)
:return:
"""
qs = QuerySet(self)
qs.calendar_view = CalendarView(start=start, end=end, max_items=max_items)
return qs

def allowed_item_fields(self):
# Return non-ID fields of all item classes allowed in this folder type
fields = set()
for item_model in self.supported_item_models:
fields.update(set(item_model.supported_fields(version=self.account.version)))
return fields

@property
def supported_item_models(self):
return tuple(item_model for folder in self.folders for item_model in folder.supported_item_models)

def validate_item_field(self, field, version):
# Takes a fieldname, Field or FieldPath object pointing to an item field, and checks that it is valid
# for the item types supported by this folder collection.
for item_model in self.supported_item_models:
try:
item_model.validate_field(field=field, version=version)
break
except InvalidField:
continue
else:
raise InvalidField(f"{field!r} is not a valid field on {self.supported_item_models}")

def _rinse_args(self, q, depth, additional_fields, field_validator):
if depth is None:
depth = self._get_default_item_traversal_depth()
if additional_fields:
for f in additional_fields:
field_validator(field=f, version=self.account.version)
if f.field.is_complex:
raise ValueError(f"Field {f.field.name!r} not supported for this service")

# Build up any restrictions
if q.is_empty():
restriction = None
query_string = None
elif q.query_string:
restriction = None
query_string = Restriction(q, folders=self.folders, applies_to=Restriction.ITEMS)
else:
restriction = Restriction(q, folders=self.folders, applies_to=Restriction.ITEMS)
query_string = None
return depth, restriction, query_string

def find_items(
self,
q,
shape=ID_ONLY,
depth=None,
additional_fields=None,
order_fields=None,
calendar_view=None,
page_size=None,
max_items=None,
offset=0,
):
"""Private method to call the FindItem service.

:param q: a Q instance containing any restrictions
:param shape: controls whether to return (id, changekey) tuples or Item objects. If additional_fields is
non-null, we always return Item objects. (Default value = ID_ONLY)
:param depth: controls the whether to return soft-deleted items or not. (Default value = None)
:param additional_fields: the extra properties we want on the return objects. Default is no properties. Be aware
that complex fields can only be fetched with fetch() (i.e. the GetItem service).
:param order_fields: the SortOrder fields, if any (Default value = None)
:param calendar_view: a CalendarView instance, if any (Default value = None)
:param page_size: the requested number of items per page (Default value = None)
:param max_items: the max number of items to return (Default value = None)
:param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned item IDs or items
"""
from ..services import FindItem

if not self.folders:
log.debug("Folder list is empty")
return
if q.is_never():
log.debug("Query will never return results")
return
depth, restriction, query_string = self._rinse_args(
q=q, depth=depth, additional_fields=additional_fields, field_validator=self.validate_item_field
)
if calendar_view is not None and not isinstance(calendar_view, CalendarView):
raise InvalidTypeError("calendar_view", calendar_view, CalendarView)

log.debug(
"Finding %s items in folders %s (shape: %s, depth: %s, additional_fields: %s, restriction: %s)",
self.account,
self.folders,
shape,
depth,
additional_fields,
restriction.q if restriction else None,
)
yield from FindItem(account=self.account, page_size=page_size).call(
folders=self.folders,
additional_fields=additional_fields,
restriction=restriction,
order_fields=order_fields,
shape=shape,
query_string=query_string,
depth=depth,
calendar_view=calendar_view,
max_items=calendar_view.max_items if calendar_view else max_items,
offset=offset,
)

def _get_single_folder(self):
if len(self.folders) > 1:
raise ValueError("Syncing folder hierarchy can only be done on a single folder")
if not self.folders:
log.debug("Folder list is empty")
return None
return self.folders[0]

def find_people(
self,
q,
shape=ID_ONLY,
depth=None,
additional_fields=None,
order_fields=None,
page_size=None,
max_items=None,
offset=0,
):
"""Private method to call the FindPeople service.

:param q: a Q instance containing any restrictions
:param shape: controls whether to return (id, changekey) tuples or Persona objects. If additional_fields is
non-null, we always return Persona objects. (Default value = ID_ONLY)
:param depth: controls the whether to return soft-deleted items or not. (Default value = None)
:param additional_fields: the extra properties we want on the return objects. Default is no properties.
:param order_fields: the SortOrder fields, if any (Default value = None)
:param page_size: the requested number of items per page (Default value = None)
:param max_items: the max number of items to return (Default value = None)
:param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned personas
"""
from ..services import FindPeople

folder = self._get_single_folder()
if q.is_never():
log.debug("Query will never return results")
return
depth, restriction, query_string = self._rinse_args(
q=q, depth=depth, additional_fields=additional_fields, field_validator=Persona.validate_field
)

yield from FindPeople(account=self.account, page_size=page_size).call(
folder=folder,
additional_fields=additional_fields,
restriction=restriction,
order_fields=order_fields,
shape=shape,
query_string=query_string,
depth=depth,
max_items=max_items,
offset=offset,
)

def get_folder_fields(self, target_cls, is_complex=None):
return {
FieldPath(field=f)
for f in target_cls.supported_fields(version=self.account.version)
if is_complex is None or f.is_complex is is_complex
}

def _get_target_cls(self):
# We may have root folders that don't support the same set of fields as normal folders. If there is a mix of
# both folder types in self.folders, raise an error, so we don't risk losing some fields in the query.
from .base import Folder
from .roots import RootOfHierarchy

has_roots = False
has_non_roots = False
for f in self.folders:
if isinstance(f, RootOfHierarchy):
if has_non_roots:
raise ValueError(f"Cannot call GetFolder on a mix of folder types: {self.folders}")
has_roots = True
else:
if has_roots:
raise ValueError(f"Cannot call GetFolder on a mix of folder types: {self.folders}")
has_non_roots = True
return RootOfHierarchy if has_roots else Folder

def _get_default_traversal_depth(self, traversal_attr):
unique_depths = {getattr(f, traversal_attr) for f in self.folders}
if len(unique_depths) == 1:
return unique_depths.pop()
raise ValueError(
f"Folders in this collection do not have a common {traversal_attr} value. You need to define an explicit "
f"traversal depth with QuerySet.depth() (values: {unique_depths})"
)

def _get_default_item_traversal_depth(self):
# When searching folders, some folders require 'Shallow' and others 'Associated' traversal depth.
return self._get_default_traversal_depth("DEFAULT_ITEM_TRAVERSAL_DEPTH")

def _get_default_folder_traversal_depth(self):
# When searching folders, some folders require 'Shallow' and others 'Deep' traversal depth.
return self._get_default_traversal_depth("DEFAULT_FOLDER_TRAVERSAL_DEPTH")

def resolve(self):
# Looks up the folders or folder IDs in the collection and returns full Folder instances with all fields set.
from .base import BaseFolder

resolveable_folders = []
for f in self.folders:
if isinstance(f, BaseFolder) and not f.get_folder_allowed:
log.debug("GetFolder not allowed on folder %s. Non-complex fields must be fetched with FindFolder", f)
yield f
else:
resolveable_folders.append(f)
# Fetch all properties for the remaining folders of folder IDs
additional_fields = self.get_folder_fields(target_cls=self._get_target_cls())
yield from self.__class__(account=self.account, folders=resolveable_folders).get_folders(
additional_fields=additional_fields
)

@require_account
def find_folders(
self, q=None, shape=ID_ONLY, depth=None, additional_fields=None, page_size=None, max_items=None, offset=0
):
from ..services import FindFolder

# 'depth' controls whether to return direct children or recurse into sub-folders
from .base import BaseFolder, Folder

if q is None:
q = Q()
if not self.folders:
log.debug("Folder list is empty")
return
if q.is_never():
log.debug("Query will never return results")
return
if q.is_empty():
restriction = None
else:
restriction = Restriction(q, folders=self.folders, applies_to=Restriction.FOLDERS)
if depth is None:
depth = self._get_default_folder_traversal_depth()
if additional_fields is None:
# Default to all non-complex properties. Sub-folders will always be of class Folder
additional_fields = self.get_folder_fields(target_cls=Folder, is_complex=False)
else:
for f in additional_fields:
if f.field.is_complex:
raise ValueError(f"find_folders() does not support field {f.field.name!r}. Use get_folders().")

# Add required fields
additional_fields.update(
(FieldPath(field=BaseFolder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

yield from FindFolder(account=self.account, page_size=page_size).call(
folders=self.folders,
additional_fields=additional_fields,
restriction=restriction,
shape=shape,
depth=depth,
max_items=max_items,
offset=offset,
)

def get_folders(self, additional_fields=None):
from ..services import GetFolder

# Expand folders with their full set of properties
from .base import BaseFolder

if not self.folders:
log.debug("Folder list is empty")
return
if additional_fields is None:
# Default to all complex properties
additional_fields = self.get_folder_fields(target_cls=self._get_target_cls(), is_complex=True)

# Add required fields
additional_fields.update(
(FieldPath(field=BaseFolder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

yield from GetFolder(account=self.account).call(
folders=self.folders,
additional_fields=additional_fields,
shape=ID_ONLY,
)

def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60):
from ..services import SubscribeToPull

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToPull.EVENT_TYPES
return SubscribeToPull(account=self.account).get(
folders=self.folders,
event_types=event_types,
watermark=watermark,
timeout=timeout,
)

def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1):
from ..services import SubscribeToPush

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToPush.EVENT_TYPES
return SubscribeToPush(account=self.account).get(
folders=self.folders,
event_types=event_types,
watermark=watermark,
status_frequency=status_frequency,
url=callback_url,
)

def subscribe_to_streaming(self, event_types=None):
from ..services import SubscribeToStreaming

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToStreaming.EVENT_TYPES
return SubscribeToStreaming(account=self.account).get(folders=self.folders, event_types=event_types)

def pull_subscription(self, **kwargs):
return PullSubscription(target=self, **kwargs)

def push_subscription(self, **kwargs):
return PushSubscription(target=self, **kwargs)

def streaming_subscription(self, **kwargs):
return StreamingSubscription(target=self, **kwargs)

def unsubscribe(self, subscription_id):
"""Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming]()
:return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other
sync methods.
"""
from ..services import Unsubscribe

return Unsubscribe(account=self.account).get(subscription_id=subscription_id)

def sync_items(self, sync_state=None, only_fields=None, ignore=None, max_changes_returned=None, sync_scope=None):
from ..services import SyncFolderItems

folder = self._get_single_folder()
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {FieldPath(field=f) for f in folder.allowed_item_fields(version=self.account.version)}
else:
for field in only_fields:
folder.validate_item_field(field=field, version=self.account.version)
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields = {f for f in folder.normalize_fields(fields=only_fields) if not f.field.is_attribute}

svc = SyncFolderItems(account=self.account)
while True:
yield from svc.call(
folder=folder,
shape=ID_ONLY,
additional_fields=additional_fields,
sync_state=sync_state,
ignore=ignore,
max_changes_returned=max_changes_returned,
sync_scope=sync_scope,
)
if svc.sync_state == sync_state:
# We sometimes get the same sync_state back, even though includes_last_item_in_range is False. Stop here
break
sync_state = svc.sync_state # Set the new sync state in the next call
if svc.includes_last_item_in_range: # Try again if there are more items
break
raise SyncCompleted(sync_state=svc.sync_state)

def sync_hierarchy(self, sync_state=None, only_fields=None):
from ..services import SyncFolderHierarchy

folder = self._get_single_folder()
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {FieldPath(field=f) for f in folder.supported_fields(version=self.account.version)}
else:
additional_fields = set()
for field_name in only_fields:
folder.validate_field(field=field_name, version=self.account.version)
f = folder.get_field_by_fieldname(fieldname=field_name)
if not f.is_attribute:
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields.add(FieldPath(field=f))

# Add required fields
additional_fields.update(
(FieldPath(field=folder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

svc = SyncFolderHierarchy(account=self.account)
while True:
yield from svc.call(
folder=folder,
shape=ID_ONLY,
additional_fields=additional_fields,
sync_state=sync_state,
)
if svc.sync_state == sync_state:
# We sometimes get the same sync_state back, even though includes_last_item_in_range is False. Stop here
break
sync_state = svc.sync_state # Set the new sync state in the next call
if svc.includes_last_item_in_range: # Try again if there are more items
break
raise SyncCompleted(sync_state=svc.sync_state)
```

A class that implements an API for searching folders.

Implement a search API on a collection of folders.

:param account: An Account object :param folders: An iterable of folders, e.g. Folder.walk(), Folder.glob(), or [a.calendar, a.inbox]

### Ancestors

* [SearchableMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/queryset.html#exchangelib.queryset.SearchableMixIn "exchangelib.queryset.SearchableMixIn")

### Class variables

`var REQUIRED_FOLDER_FIELDS`
The type of the None singleton.

### Instance variables

`var folders`

Expand source code
```
def __get__(self, obj, cls):
if obj is None:
return self

obj_dict = obj.__dict__
name = self.func.__name__
with self.lock:
try:
# check if the value was computed before the lock was acquired
return obj_dict[name]

except KeyError:
# if not, do the calculation and release the lock
return obj_dict.setdefault(name, self.func(obj))
```

`prop supported_item_models`

Expand source code
```
@property
def supported_item_models(self):
return tuple(item_model for folder in self.folders for item_model in folder.supported_item_models)
```

### Methods

```
def allowed_item_fields(self)
```

Expand source code
```
def allowed_item_fields(self):
# Return non-ID fields of all item classes allowed in this folder type
fields = set()
for item_model in self.supported_item_models:
fields.update(set(item_model.supported_fields(version=self.account.version)))
return fields
```

```
def filter(self, *args, **kwargs)
```

Expand source code
```
def filter(self, *args, **kwargs):
"""Find items in the folder(s).

Non-keyword args may be a list of Q instances.

Optional extra keyword arguments follow a Django-like QuerySet filter syntax (see
https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups).

We don't support '__year' and other date-related lookups. We also don't support '__endswith' or '__iendswith'.

We support the additional '__not' lookup in place of Django's exclude() for simple cases. For more complicated
cases you need to create a Q object and use ~Q().

Examples:

my_account.inbox.filter(datetime_received__gt=EWSDateTime(2016, 1, 1))
my_account.calendar.filter(start__range=(EWSDateTime(2016, 1, 1), EWSDateTime(2017, 1, 1)))
my_account.tasks.filter(subject='Hi mom')
my_account.tasks.filter(subject__not='Hi mom')
my_account.tasks.filter(subject__contains='Foo')
my_account.tasks.filter(subject__icontains='foo')

'endswith' and 'iendswith' could be emulated by searching with 'contains' or 'icontains' and then
post-processing items. Fetch the field in question with additional_fields and remove items where the search
string is not a postfix.
"""
return QuerySet(self).filter(*args, **kwargs)
```

Find items in the folder(s).

Non-keyword args may be a list of Q instances.

Optional extra keyword arguments follow a Django-like QuerySet filter syntax (see [https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups](https://docs.djangoproject.com/en/1.10/ref/models/querysets/#field-lookups)).

We don't support '__year' and other date-related lookups. We also don't support '__endswith' or '__iendswith'.

We support the additional '__not' lookup in place of Django's exclude() for simple cases. For more complicated cases you need to create a Q object and use ~Q().

Examples
------

my_account.inbox.filter(datetime_received__gt=EWSDateTime(2016, 1, 1)) my_account.calendar.filter(start__range=(EWSDateTime(2016, 1, 1), EWSDateTime(2017, 1, 1))) my_account.tasks.filter(subject='Hi mom') my_account.tasks.filter(subject__not='Hi mom') my_account.tasks.filter(subject__contains='Foo') my_account.tasks.filter(subject__icontains='foo')

'endswith' and 'iendswith' could be emulated by searching with 'contains' or 'icontains' and then post-processing items. Fetch the field in question with additional_fields and remove items where the search string is not a postfix.

```
def find_folders(self,q=None,shape='IdOnly',depth=None,additional_fields=None,page_size=None,max_items=None,offset=0)
```

Expand source code
```
@require_account
def find_folders(
self, q=None, shape=ID_ONLY, depth=None, additional_fields=None, page_size=None, max_items=None, offset=0
):
from ..services import FindFolder

# 'depth' controls whether to return direct children or recurse into sub-folders
from .base import BaseFolder, Folder

if q is None:
q = Q()
if not self.folders:
log.debug("Folder list is empty")
return
if q.is_never():
log.debug("Query will never return results")
return
if q.is_empty():
restriction = None
else:
restriction = Restriction(q, folders=self.folders, applies_to=Restriction.FOLDERS)
if depth is None:
depth = self._get_default_folder_traversal_depth()
if additional_fields is None:
# Default to all non-complex properties. Sub-folders will always be of class Folder
additional_fields = self.get_folder_fields(target_cls=Folder, is_complex=False)
else:
for f in additional_fields:
if f.field.is_complex:
raise ValueError(f"find_folders() does not support field {f.field.name!r}. Use get_folders().")

# Add required fields
additional_fields.update(
(FieldPath(field=BaseFolder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

yield from FindFolder(account=self.account, page_size=page_size).call(
folders=self.folders,
additional_fields=additional_fields,
restriction=restriction,
shape=shape,
depth=depth,
max_items=max_items,
offset=offset,
)
```

```
def find_items(self,q,shape='IdOnly',depth=None,additional_fields=None,order_fields=None,calendar_view=None,page_size=None,max_items=None,offset=0)
```

Expand source code
```
def find_items(
self,
q,
shape=ID_ONLY,
depth=None,
additional_fields=None,
order_fields=None,
calendar_view=None,
page_size=None,
max_items=None,
offset=0,
):
"""Private method to call the FindItem service.

:param q: a Q instance containing any restrictions
:param shape: controls whether to return (id, changekey) tuples or Item objects. If additional_fields is
non-null, we always return Item objects. (Default value = ID_ONLY)
:param depth: controls the whether to return soft-deleted items or not. (Default value = None)
:param additional_fields: the extra properties we want on the return objects. Default is no properties. Be aware
that complex fields can only be fetched with fetch() (i.e. the GetItem service).
:param order_fields: the SortOrder fields, if any (Default value = None)
:param calendar_view: a CalendarView instance, if any (Default value = None)
:param page_size: the requested number of items per page (Default value = None)
:param max_items: the max number of items to return (Default value = None)
:param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned item IDs or items
"""
from ..services import FindItem

if not self.folders:
log.debug("Folder list is empty")
return
if q.is_never():
log.debug("Query will never return results")
return
depth, restriction, query_string = self._rinse_args(
q=q, depth=depth, additional_fields=additional_fields, field_validator=self.validate_item_field
)
if calendar_view is not None and not isinstance(calendar_view, CalendarView):
raise InvalidTypeError("calendar_view", calendar_view, CalendarView)

log.debug(
"Finding %s items in folders %s (shape: %s, depth: %s, additional_fields: %s, restriction: %s)",
self.account,
self.folders,
shape,
depth,
additional_fields,
restriction.q if restriction else None,
)
yield from FindItem(account=self.account, page_size=page_size).call(
folders=self.folders,
additional_fields=additional_fields,
restriction=restriction,
order_fields=order_fields,
shape=shape,
query_string=query_string,
depth=depth,
calendar_view=calendar_view,
max_items=calendar_view.max_items if calendar_view else max_items,
offset=offset,
)
```

Private method to call the FindItem service.

:param q: a Q instance containing any restrictions :param shape: controls whether to return (id, changekey) tuples or Item objects. If additional_fields is non-null, we always return Item objects. (Default value = ID_ONLY) :param depth: controls the whether to return soft-deleted items or not. (Default value = None) :param additional_fields: the extra properties we want on the return objects. Default is no properties. Be aware that complex fields can only be fetched with fetch() (i.e. the GetItem service). :param order_fields: the SortOrder fields, if any (Default value = None) :param calendar_view: a CalendarView instance, if any (Default value = None) :param page_size: the requested number of items per page (Default value = None) :param max_items: the max number of items to return (Default value = None) :param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned item IDs or items

```
def find_people(self,q,shape='IdOnly',depth=None,additional_fields=None,order_fields=None,page_size=None,max_items=None,offset=0)
```

Expand source code
```
def find_people(
self,
q,
shape=ID_ONLY,
depth=None,
additional_fields=None,
order_fields=None,
page_size=None,
max_items=None,
offset=0,
):
"""Private method to call the FindPeople service.

:param q: a Q instance containing any restrictions
:param shape: controls whether to return (id, changekey) tuples or Persona objects. If additional_fields is
non-null, we always return Persona objects. (Default value = ID_ONLY)
:param depth: controls the whether to return soft-deleted items or not. (Default value = None)
:param additional_fields: the extra properties we want on the return objects. Default is no properties.
:param order_fields: the SortOrder fields, if any (Default value = None)
:param page_size: the requested number of items per page (Default value = None)
:param max_items: the max number of items to return (Default value = None)
:param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned personas
"""
from ..services import FindPeople

folder = self._get_single_folder()
if q.is_never():
log.debug("Query will never return results")
return
depth, restriction, query_string = self._rinse_args(
q=q, depth=depth, additional_fields=additional_fields, field_validator=Persona.validate_field
)

yield from FindPeople(account=self.account, page_size=page_size).call(
folder=folder,
additional_fields=additional_fields,
restriction=restriction,
order_fields=order_fields,
shape=shape,
query_string=query_string,
depth=depth,
max_items=max_items,
offset=offset,
)
```

Private method to call the FindPeople service.

:param q: a Q instance containing any restrictions :param shape: controls whether to return (id, changekey) tuples or Persona objects. If additional_fields is non-null, we always return Persona objects. (Default value = ID_ONLY) :param depth: controls the whether to return soft-deleted items or not. (Default value = None) :param additional_fields: the extra properties we want on the return objects. Default is no properties. :param order_fields: the SortOrder fields, if any (Default value = None) :param page_size: the requested number of items per page (Default value = None) :param max_items: the max number of items to return (Default value = None) :param offset: the offset relative to the first item in the item collection (Default value = 0)

:return: a generator for the returned personas

```
def get_folder_fields(self, target_cls, is_complex=None)
```

Expand source code
```
def get_folder_fields(self, target_cls, is_complex=None):
return {
FieldPath(field=f)
for f in target_cls.supported_fields(version=self.account.version)
if is_complex is None or f.is_complex is is_complex
}
```

```
def get_folders(self, additional_fields=None)
```

Expand source code
```
def get_folders(self, additional_fields=None):
from ..services import GetFolder

# Expand folders with their full set of properties
from .base import BaseFolder

if not self.folders:
log.debug("Folder list is empty")
return
if additional_fields is None:
# Default to all complex properties
additional_fields = self.get_folder_fields(target_cls=self._get_target_cls(), is_complex=True)

# Add required fields
additional_fields.update(
(FieldPath(field=BaseFolder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

yield from GetFolder(account=self.account).call(
folders=self.folders,
additional_fields=additional_fields,
shape=ID_ONLY,
)
```

```
def pull_subscription(self, **kwargs)
```

Expand source code
```
def pull_subscription(self, **kwargs):
return PullSubscription(target=self, **kwargs)
```

```
def push_subscription(self, **kwargs)
```

Expand source code
```
def push_subscription(self, **kwargs):
return PushSubscription(target=self, **kwargs)
```

```
def resolve(self)
```

Expand source code
```
def resolve(self):
# Looks up the folders or folder IDs in the collection and returns full Folder instances with all fields set.
from .base import BaseFolder

resolveable_folders = []
for f in self.folders:
if isinstance(f, BaseFolder) and not f.get_folder_allowed:
log.debug("GetFolder not allowed on folder %s. Non-complex fields must be fetched with FindFolder", f)
yield f
else:
resolveable_folders.append(f)
# Fetch all properties for the remaining folders of folder IDs
additional_fields = self.get_folder_fields(target_cls=self._get_target_cls())
yield from self.__class__(account=self.account, folders=resolveable_folders).get_folders(
additional_fields=additional_fields
)
```

```
def streaming_subscription(self, **kwargs)
```

Expand source code
```
def streaming_subscription(self, **kwargs):
return StreamingSubscription(target=self, **kwargs)
```

```
def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60)
```

Expand source code
```
def subscribe_to_pull(self, event_types=None, watermark=None, timeout=60):
from ..services import SubscribeToPull

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToPull.EVENT_TYPES
return SubscribeToPull(account=self.account).get(
folders=self.folders,
event_types=event_types,
watermark=watermark,
timeout=timeout,
)
```

```
def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1)
```

Expand source code
```
def subscribe_to_push(self, callback_url, event_types=None, watermark=None, status_frequency=1):
from ..services import SubscribeToPush

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToPush.EVENT_TYPES
return SubscribeToPush(account=self.account).get(
folders=self.folders,
event_types=event_types,
watermark=watermark,
status_frequency=status_frequency,
url=callback_url,
)
```

```
def subscribe_to_streaming(self, event_types=None)
```

Expand source code
```
def subscribe_to_streaming(self, event_types=None):
from ..services import SubscribeToStreaming

if not self.folders:
log.debug("Folder list is empty")
return None
if event_types is None:
event_types = SubscribeToStreaming.EVENT_TYPES
return SubscribeToStreaming(account=self.account).get(folders=self.folders, event_types=event_types)
```

```
def sync_hierarchy(self, sync_state=None, only_fields=None)
```

Expand source code
```
def sync_hierarchy(self, sync_state=None, only_fields=None):
from ..services import SyncFolderHierarchy

folder = self._get_single_folder()
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {FieldPath(field=f) for f in folder.supported_fields(version=self.account.version)}
else:
additional_fields = set()
for field_name in only_fields:
folder.validate_field(field=field_name, version=self.account.version)
f = folder.get_field_by_fieldname(fieldname=field_name)
if not f.is_attribute:
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields.add(FieldPath(field=f))

# Add required fields
additional_fields.update(
(FieldPath(field=folder.get_field_by_fieldname(f)) for f in self.REQUIRED_FOLDER_FIELDS)
)

svc = SyncFolderHierarchy(account=self.account)
while True:
yield from svc.call(
folder=folder,
shape=ID_ONLY,
additional_fields=additional_fields,
sync_state=sync_state,
)
if svc.sync_state == sync_state:
# We sometimes get the same sync_state back, even though includes_last_item_in_range is False. Stop here
break
sync_state = svc.sync_state # Set the new sync state in the next call
if svc.includes_last_item_in_range: # Try again if there are more items
break
raise SyncCompleted(sync_state=svc.sync_state)
```

```
def sync_items(self,sync_state=None,only_fields=None,ignore=None,max_changes_returned=None,sync_scope=None)
```

Expand source code
```
def sync_items(self, sync_state=None, only_fields=None, ignore=None, max_changes_returned=None, sync_scope=None):
from ..services import SyncFolderItems

folder = self._get_single_folder()
if only_fields is None:
# We didn't restrict list of field paths. Get all fields from the server, including extended properties.
additional_fields = {FieldPath(field=f) for f in folder.allowed_item_fields(version=self.account.version)}
else:
for field in only_fields:
folder.validate_item_field(field=field, version=self.account.version)
# Remove ItemId and ChangeKey. We get them unconditionally
additional_fields = {f for f in folder.normalize_fields(fields=only_fields) if not f.field.is_attribute}

svc = SyncFolderItems(account=self.account)
while True:
yield from svc.call(
folder=folder,
shape=ID_ONLY,
additional_fields=additional_fields,
sync_state=sync_state,
ignore=ignore,
max_changes_returned=max_changes_returned,
sync_scope=sync_scope,
)
if svc.sync_state == sync_state:
# We sometimes get the same sync_state back, even though includes_last_item_in_range is False. Stop here
break
sync_state = svc.sync_state # Set the new sync state in the next call
if svc.includes_last_item_in_range: # Try again if there are more items
break
raise SyncCompleted(sync_state=svc.sync_state)
```

```
def unsubscribe(self, subscription_id)
```

Expand source code
```
def unsubscribe(self, subscription_id):
"""Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming]()
:return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other
sync methods.
"""
from ..services import Unsubscribe

return Unsubscribe(account=self.account).get(subscription_id=subscription_id)
```

Unsubscribe. Only applies to pull and streaming notifications.

:param subscription_id: A subscription ID as acquired by .subscribe_to_[pull|streaming](https://ecederstrand.github.io/exchangelib/exchangelib/) :return: True

This method doesn't need the current collection instance, but it makes sense to keep the method along the other sync methods.

```
def validate_item_field(self, field, version)
```

Expand source code
```
def validate_item_field(self, field, version):
# Takes a fieldname, Field or FieldPath object pointing to an item field, and checks that it is valid
# for the item types supported by this folder collection.
for item_model in self.supported_item_models:
try:
item_model.validate_field(field=field, version=version)
break
except InvalidField:
continue
else:
raise InvalidField(f"{field!r} is not a valid field on {self.supported_item_models}")
```

```
def view(self, start, end, max_items=None)
```

Expand source code
```
def view(self, start, end, max_items=None):
"""Implement the CalendarView option to FindItem. The difference between 'filter' and 'view' is that 'filter'
only returns the master CalendarItem for recurring items, while 'view' unfolds recurring items and returns all
CalendarItem occurrences as one would normally expect when presenting a calendar.

Supports the same semantics as filter, except for 'start' and 'end' keyword attributes which are both required
and behave differently than filter. Here, they denote the start and end of the timespan of the view. All items
the overlap the timespan are returned (items that end exactly on 'start' are also returned, for some reason).

EWS does not allow combining CalendarView with search restrictions (filter and exclude).

'max_items' defines the maximum number of items returned in this view. Optional.

:param start:
:param end:
:param max_items: (Default value = None)
:return:
"""
qs = QuerySet(self)
qs.calendar_view = CalendarView(start=start, end=end, max_items=max_items)
return qs
```

Implement the CalendarView option to FindItem. The difference between 'filter' and 'view' is that 'filter' only returns the master CalendarItem for recurring items, while 'view' unfolds recurring items and returns all CalendarItem occurrences as one would normally expect when presenting a calendar.

Supports the same semantics as filter, except for 'start' and 'end' keyword attributes which are both required and behave differently than filter. Here, they denote the start and end of the timespan of the view. All items the overlap the timespan are returned (items that end exactly on 'start' are also returned, for some reason).

EWS does not allow combining CalendarView with search restrictions (filter and exclude).

'max_items' defines the maximum number of items returned in this view. Optional.

:param start: :param end: :param max_items: (Default value = None) :return:

### Inherited members

* `SearchableMixIn`:
* `all`
* `exclude`
* `get`
* `none`
* `people`

```
class ForwardItem
(**kwargs)
```

Expand source code
```
class ForwardItem(BaseReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/forwarditem"""

ELEMENT_NAME = "ForwardItem"
```

### Ancestors

* [BaseReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseReplyItem "exchangelib.items.base.BaseReplyItem")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `author`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `new_body`
* `received_by`
* `received_representing`
* `reference_item_id`
* `remove_field`
* `save`
* `subject`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class HTMLBody
(...)
```

Expand source code
```
class HTMLBody(Body):
"""Helper to mark the 'body' field as a complex attribute.

MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/body
"""

body_type = "HTML"
```

### Ancestors

* [Body](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Body "exchangelib.properties.Body")
* builtins.str

### Inherited members

* `Body`:
* `body_type`
* `format`

```
class Identity
(**kwargs)
```

Expand source code
```
class Identity(EWSElement):
"""Contains information that uniquely identifies an account. Currently only used for SOAP impersonation headers."""

ELEMENT_NAME = "ConnectingSID"

# We have multiple options for uniquely identifying the user. Here's a prioritized list in accordance with
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/connectingsid
sid = TextField(field_uri="SID")
upn = TextField(field_uri="PrincipalName")
smtp_address = TextField(field_uri="SmtpAddress") # The (non-)primary email address for the account
primary_smtp_address = TextField(field_uri="PrimarySmtpAddress") # The primary email address for the account
```

Contains information that uniquely identifies an account. Currently only used for SOAP impersonation headers.

### Ancestors

* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Instance variables

`var primary_smtp_address`
The type of the None singleton.

`var sid`
The type of the None singleton.

`var smtp_address`
The type of the None singleton.

`var upn`
The type of the None singleton.

### Inherited members

* `EWSElement`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class ItemAttachment
(**kwargs)
```

Expand source code
```
class ItemAttachment(Attachment):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/itemattachment"""

ELEMENT_NAME = "ItemAttachment"

_item = ItemField(field_uri="Item")

def __init__(self, **kwargs):
kwargs["_item"] = kwargs.pop("item", None)
super().__init__(**kwargs)

@property
def item(self):
from .folders import BaseFolder
from .services import GetAttachment

if self.attachment_id is None:
return self._item
if self._item is not None:
return self._item
# We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
if not self.parent_item or not self.parent_item.account:
raise ValueError(f"{self.__class__.__name__} must have an account")
additional_fields = {
FieldPath(field=f) for f in BaseFolder.allowed_item_fields(version=self.parent_item.account.version)
}
attachment = GetAttachment(account=self.parent_item.account).get(
items=[self.attachment_id],
include_mime_content=True,
body_type=None,
filter_html_content=None,
additional_fields=additional_fields,
)
self._item = attachment.item
return self._item

@item.setter
def item(self, value):
from .items import Item

if not isinstance(value, Item):
raise InvalidTypeError("value", value, Item)
self._item = value

@classmethod
def from_xml(cls, elem, account):
kwargs = {f.name: f.from_xml(elem=elem, account=account) for f in cls.FIELDS}
kwargs["item"] = kwargs.pop("_item")
cls._clear(elem)
return cls(**kwargs)
```

### Ancestors

* [Attachment](https://ecederstrand.github.io/exchangelib/exchangelib/attachments.html#exchangelib.attachments.Attachment "exchangelib.attachments.Attachment")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Static methods

```
def from_xml(elem, account)
```

### Instance variables

`prop item`

Expand source code
```
@property
def item(self):
from .folders import BaseFolder
from .services import GetAttachment

if self.attachment_id is None:
return self._item
if self._item is not None:
return self._item
# We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
if not self.parent_item or not self.parent_item.account:
raise ValueError(f"{self.__class__.__name__} must have an account")
additional_fields = {
FieldPath(field=f) for f in BaseFolder.allowed_item_fields(version=self.parent_item.account.version)
}
attachment = GetAttachment(account=self.parent_item.account).get(
items=[self.attachment_id],
include_mime_content=True,
body_type=None,
filter_html_content=None,
additional_fields=additional_fields,
)
self._item = attachment.item
return self._item
```

### Inherited members

* `Attachment`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `attachment_id`
* `content_id`
* `content_location`
* `content_type`
* `is_inline`
* `last_modified_time`
* `name`
* `remove_field`
* `size`
* `supported_fields`
* `validate_field`

```
class ItemId
(*args, **kwargs)
```

Expand source code
```
class ItemId(BaseItemId):
"""'id' and 'changekey' are UUIDs generated by Exchange.

MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/itemid
"""

ELEMENT_NAME = "ItemId"
ID_ATTR = "Id"
CHANGEKEY_ATTR = "ChangeKey"

id = IdField(field_uri=ID_ATTR, is_required=True)
changekey = IdField(field_uri=CHANGEKEY_ATTR, is_required=False)
```

### Ancestors

* [BaseItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.BaseItemId "exchangelib.properties.BaseItemId")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Subclasses

* [AssociatedCalendarItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.AssociatedCalendarItemId "exchangelib.properties.AssociatedCalendarItemId")
* [ConversationId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.ConversationId "exchangelib.properties.ConversationId")
* [FolderId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.FolderId "exchangelib.properties.FolderId")
* [MovedItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.MovedItemId "exchangelib.properties.MovedItemId")
* [OldItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.OldItemId "exchangelib.properties.OldItemId")
* [ParentFolderId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.ParentFolderId "exchangelib.properties.ParentFolderId")
* [ParentItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.ParentItemId "exchangelib.properties.ParentItemId")
* [PersonaId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.PersonaId "exchangelib.properties.PersonaId")
* [ReferenceItemId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.ReferenceItemId "exchangelib.properties.ReferenceItemId")
* [SourceId](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.SourceId "exchangelib.properties.SourceId")

### Instance variables

`var changekey`
The type of the None singleton.

`var id`
The type of the None singleton.

### Inherited members

* `BaseItemId`:
* `CHANGEKEY_ATTR`
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ATTR`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class Mailbox
(**kwargs)
```

Expand source code
```
class Mailbox(EWSElement):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/mailbox"""

ELEMENT_NAME = "Mailbox"
MAILBOX = "Mailbox"
ONE_OFF = "OneOff"
MAILBOX_TYPE_CHOICES = {
Choice(MAILBOX),
Choice("PublicDL"),
Choice("PrivateDL"),
Choice("Contact"),
Choice("PublicFolder"),
Choice("Unknown"),
Choice(ONE_OFF),
Choice("GroupMailbox", supported_from=EXCHANGE_2013),
}

name = TextField(field_uri="Name")
email_address = EmailAddressField(field_uri="EmailAddress")
# RoutingType values are not restricted:
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/routingtype-emailaddresstype
routing_type = TextField(field_uri="RoutingType", default="SMTP")
mailbox_type = ChoiceField(field_uri="MailboxType", choices=MAILBOX_TYPE_CHOICES, default=MAILBOX)
item_id = EWSElementField(value_cls=ItemId)

def clean(self, version=None):
super().clean(version=version)

if self.mailbox_type != self.ONE_OFF and not self.email_address and not self.item_id:
# A OneOff Mailbox (a one-off member of a personal distribution list) may lack these fields, but other
# Mailboxes require at least one. See also "Remarks" section of
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/mailbox
raise ValueError(f"Mailbox type {self.mailbox_type!r} must have either 'email_address' or 'item_id' set")

def __hash__(self):
# Exchange may add 'mailbox_type' and 'name' on insert. We're satisfied if the item_id or email address matches.
if self.item_id:
return hash(self.item_id)
if self.email_address:
return hash(self.email_address.lower())
return super().__hash__()
```

### Ancestors

* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Subclasses

* [Address](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Address "exchangelib.properties.Address")
* [DLMailbox](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.DLMailbox "exchangelib.properties.DLMailbox")
* [EmailAddress](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EmailAddress "exchangelib.properties.EmailAddress")
* [EmailAddressTypeValue](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EmailAddressTypeValue "exchangelib.properties.EmailAddressTypeValue")
* [PersonaPostalAddressTypeValue](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.PersonaPostalAddressTypeValue "exchangelib.properties.PersonaPostalAddressTypeValue")
* [RecipientAddress](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.RecipientAddress "exchangelib.properties.RecipientAddress")
* [Room](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Room "exchangelib.properties.Room")
* [RoomList](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.RoomList "exchangelib.properties.RoomList")
* [SendingAs](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.SendingAs "exchangelib.properties.SendingAs")

### Class variables

`var MAILBOX`
The type of the None singleton.

`var MAILBOX_TYPE_CHOICES`
The type of the None singleton.

`var ONE_OFF`
The type of the None singleton.

### Instance variables

`var email_address`
The type of the None singleton.

`var item_id`
The type of the None singleton.

`var mailbox_type`
The type of the None singleton.

`var name`
The type of the None singleton.

`var routing_type`
The type of the None singleton.

### Methods

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
super().clean(version=version)

if self.mailbox_type != self.ONE_OFF and not self.email_address and not self.item_id:
# A OneOff Mailbox (a one-off member of a personal distribution list) may lack these fields, but other
# Mailboxes require at least one. See also "Remarks" section of
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/mailbox
raise ValueError(f"Mailbox type {self.mailbox_type!r} must have either 'email_address' or 'item_id' set")
```

### Inherited members

* `EWSElement`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class Message
(**kwargs)
```

Expand source code
```
class Message(Item):
"""MSDN:
https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/message-ex15websvcsotherref
"""

ELEMENT_NAME = "Message"

sender = MailboxField(field_uri="message:Sender", is_read_only=True, is_read_only_after_send=True)
to_recipients = MailboxListField(
field_uri="message:ToRecipients", is_read_only_after_send=True, is_searchable=False
)
cc_recipients = MailboxListField(
field_uri="message:CcRecipients", is_read_only_after_send=True, is_searchable=False
)
bcc_recipients = MailboxListField(
field_uri="message:BccRecipients", is_read_only_after_send=True, is_searchable=False
)
is_read_receipt_requested = BooleanField(
field_uri="message:IsReadReceiptRequested", is_required=True, default=False, is_read_only_after_send=True
)
is_delivery_receipt_requested = BooleanField(
field_uri="message:IsDeliveryReceiptRequested", is_required=True, default=False, is_read_only_after_send=True
)
conversation_index = Base64Field(field_uri="message:ConversationIndex", is_read_only=True)
conversation_topic = CharField(field_uri="message:ConversationTopic", is_read_only=True)
# Rename 'From' to 'author'. We can't use field name 'from' since it's a Python keyword.
author = MailboxField(field_uri="message:From", is_read_only_after_send=True)
message_id = TextField(field_uri="message:InternetMessageId", is_read_only_after_send=True)
is_read = BooleanField(field_uri="message:IsRead", is_required=True, default=False)
is_response_requested = BooleanField(field_uri="message:IsResponseRequested", default=False, is_required=True)
references = TextField(field_uri="message:References")
reply_to = MailboxListField(field_uri="message:ReplyTo", is_read_only_after_send=True, is_searchable=False)
received_by = MailboxField(field_uri="message:ReceivedBy", is_read_only=True)
received_representing = MailboxField(field_uri="message:ReceivedRepresenting", is_read_only=True)
reminder_message_data = EWSElementField(
field_uri="message:ReminderMessageData",
value_cls=ReminderMessageData,
supported_from=EXCHANGE_2013_SP1,
is_read_only=True,
)

@require_account
def send(
self,
save_copy=True,
copy_to_folder=None,
conflict_resolution=AUTO_RESOLVE,
send_meeting_invitations=SEND_TO_NONE,
):
from ..services import SendItem

# Only sends a message. The message can either be an existing draft stored in EWS or a new message that does
# not yet exist in EWS.
if copy_to_folder and not save_copy:
raise AttributeError("'save_copy' must be True when 'copy_to_folder' is set")
if save_copy and not copy_to_folder:
copy_to_folder = self.account.sent # 'Sent' is default EWS behaviour
if self.id:
SendItem(account=self.account).get(items=[self], saved_item_folder=copy_to_folder)
# The item will be deleted from the original folder
self._id = None
self.folder = copy_to_folder
return None

# New message
if copy_to_folder:
# This would better be done via send_and_save() but let's just support it here
self.folder = copy_to_folder
return self.send_and_save(
conflict_resolution=conflict_resolution, send_meeting_invitations=send_meeting_invitations
)

if self.account.version.build < EXCHANGE_2013 and self.attachments:
# At least some versions prior to Exchange 2013 can't send attachments immediately. You need to first save,
# then attach, then send. This is done in send_and_save(). send() will delete the item again.
self.send_and_save(
conflict_resolution=conflict_resolution, send_meeting_invitations=send_meeting_invitations
)
return None

self._create(message_disposition=SEND_ONLY, send_meeting_invitations=send_meeting_invitations)
return None

def send_and_save(
self, update_fields=None, conflict_resolution=AUTO_RESOLVE, send_meeting_invitations=SEND_TO_NONE
):
# Sends Message and saves a copy in the parent folder. Does not return an ItemId.
if self.id:
return self._update(
update_fieldnames=update_fields,
message_disposition=SEND_AND_SAVE_COPY,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
if self.account.version.build < EXCHANGE_2013 and self.attachments:
# At least some versions prior to Exchange 2013 can't send-and-save attachments immediately. You need
# to first save, then attach, then send. This is done in save().
self.save(
update_fields=update_fields,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
return self.send(
save_copy=False,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
return self._create(message_disposition=SEND_AND_SAVE_COPY, send_meeting_invitations=send_meeting_invitations)

@require_id
def create_reply(self, subject, body, to_recipients=None, cc_recipients=None, bcc_recipients=None, author=None):
if not to_recipients:
if not self.author:
raise ValueError("'to_recipients' must be set when message has no 'author'")
to_recipients = [self.author]
return ReplyToItem(
account=self.account,
reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey),
subject=subject,
new_body=body,
to_recipients=to_recipients,
cc_recipients=cc_recipients,
bcc_recipients=bcc_recipients,
author=author,
)

def reply(self, subject, body, to_recipients=None, cc_recipients=None, bcc_recipients=None, author=None):
return self.create_reply(subject, body, to_recipients, cc_recipients, bcc_recipients, author).send()

@require_id
def create_reply_all(self, subject, body, author=None):
me = MailboxField().clean(self.account.primary_smtp_address.lower())
to_recipients = set(self.to_recipients or [])
to_recipients.discard(me)
cc_recipients = set(self.cc_recipients or [])
cc_recipients.discard(me)
bcc_recipients = set(self.bcc_recipients or [])
bcc_recipients.discard(me)
if self.author:
to_recipients.add(self.author)
return ReplyAllToItem(
account=self.account,
reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey),
subject=subject,
new_body=body,
to_recipients=list(to_recipients),
cc_recipients=list(cc_recipients),
bcc_recipients=list(bcc_recipients),
author=author,
)

def reply_all(self, subject, body, author=None):
return self.create_reply_all(subject, body, author).send()

def mark_as_junk(self, is_junk=True, move_item=True):
"""Mark or un-marks items as junk email.

:param is_junk: If True, the sender will be added from the blocked sender list. Otherwise, the sender will be
removed.
:param move_item: If true, the item will be moved to the junk folder.
:return:
"""
from ..services import MarkAsJunk

res = MarkAsJunk(account=self.account).get(
items=[self], is_junk=is_junk, move_item=move_item, expect_result=None
)
if res is None:
return
self.folder = self.account.junk if is_junk else self.account.inbox
self.id, self.changekey = res
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Instance variables

`var author`
The type of the None singleton.

`var bcc_recipients`
The type of the None singleton.

`var cc_recipients`
The type of the None singleton.

`var conversation_index`
The type of the None singleton.

`var conversation_topic`
The type of the None singleton.

`var is_delivery_receipt_requested`
The type of the None singleton.

`var is_read`
The type of the None singleton.

`var is_read_receipt_requested`
The type of the None singleton.

`var is_response_requested`
The type of the None singleton.

`var message_id`
The type of the None singleton.

`var received_by`
The type of the None singleton.

`var received_representing`
The type of the None singleton.

`var references`
The type of the None singleton.

`var reminder_message_data`
The type of the None singleton.

`var reply_to`
The type of the None singleton.

`var sender`
The type of the None singleton.

`var to_recipients`
The type of the None singleton.

### Methods

```
def create_reply(self,subject,body,to_recipients=None,cc_recipients=None,bcc_recipients=None,author=None)
```

Expand source code
```
@require_id
def create_reply(self, subject, body, to_recipients=None, cc_recipients=None, bcc_recipients=None, author=None):
if not to_recipients:
if not self.author:
raise ValueError("'to_recipients' must be set when message has no 'author'")
to_recipients = [self.author]
return ReplyToItem(
account=self.account,
reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey),
subject=subject,
new_body=body,
to_recipients=to_recipients,
cc_recipients=cc_recipients,
bcc_recipients=bcc_recipients,
author=author,
)
```

```
def create_reply_all(self, subject, body, author=None)
```

Expand source code
```
@require_id
def create_reply_all(self, subject, body, author=None):
me = MailboxField().clean(self.account.primary_smtp_address.lower())
to_recipients = set(self.to_recipients or [])
to_recipients.discard(me)
cc_recipients = set(self.cc_recipients or [])
cc_recipients.discard(me)
bcc_recipients = set(self.bcc_recipients or [])
bcc_recipients.discard(me)
if self.author:
to_recipients.add(self.author)
return ReplyAllToItem(
account=self.account,
reference_item_id=ReferenceItemId(id=self.id, changekey=self.changekey),
subject=subject,
new_body=body,
to_recipients=list(to_recipients),
cc_recipients=list(cc_recipients),
bcc_recipients=list(bcc_recipients),
author=author,
)
```

```
def mark_as_junk(self, is_junk=True, move_item=True)
```

Expand source code
```
def mark_as_junk(self, is_junk=True, move_item=True):
"""Mark or un-marks items as junk email.

:param is_junk: If True, the sender will be added from the blocked sender list. Otherwise, the sender will be
removed.
:param move_item: If true, the item will be moved to the junk folder.
:return:
"""
from ..services import MarkAsJunk

res = MarkAsJunk(account=self.account).get(
items=[self], is_junk=is_junk, move_item=move_item, expect_result=None
)
if res is None:
return
self.folder = self.account.junk if is_junk else self.account.inbox
self.id, self.changekey = res
```

Mark or un-marks items as junk email.

:param is_junk: If True, the sender will be added from the blocked sender list. Otherwise, the sender will be removed. :param move_item: If true, the item will be moved to the junk folder. :return:

```
def reply(self,subject,body,to_recipients=None,cc_recipients=None,bcc_recipients=None,author=None)
```

Expand source code
```
def reply(self, subject, body, to_recipients=None, cc_recipients=None, bcc_recipients=None, author=None):
return self.create_reply(subject, body, to_recipients, cc_recipients, bcc_recipients, author).send()
```

```
def reply_all(self, subject, body, author=None)
```

Expand source code
```
def reply_all(self, subject, body, author=None):
return self.create_reply_all(subject, body, author).send()
```

```
def send(self,save_copy=True,copy_to_folder=None,conflict_resolution='AutoResolve',send_meeting_invitations='SendToNone')
```

Expand source code
```
@require_account
def send(
self,
save_copy=True,
copy_to_folder=None,
conflict_resolution=AUTO_RESOLVE,
send_meeting_invitations=SEND_TO_NONE,
):
from ..services import SendItem

# Only sends a message. The message can either be an existing draft stored in EWS or a new message that does
# not yet exist in EWS.
if copy_to_folder and not save_copy:
raise AttributeError("'save_copy' must be True when 'copy_to_folder' is set")
if save_copy and not copy_to_folder:
copy_to_folder = self.account.sent # 'Sent' is default EWS behaviour
if self.id:
SendItem(account=self.account).get(items=[self], saved_item_folder=copy_to_folder)
# The item will be deleted from the original folder
self._id = None
self.folder = copy_to_folder
return None

# New message
if copy_to_folder:
# This would better be done via send_and_save() but let's just support it here
self.folder = copy_to_folder
return self.send_and_save(
conflict_resolution=conflict_resolution, send_meeting_invitations=send_meeting_invitations
)

if self.account.version.build < EXCHANGE_2013 and self.attachments:
# At least some versions prior to Exchange 2013 can't send attachments immediately. You need to first save,
# then attach, then send. This is done in send_and_save(). send() will delete the item again.
self.send_and_save(
conflict_resolution=conflict_resolution, send_meeting_invitations=send_meeting_invitations
)
return None

self._create(message_disposition=SEND_ONLY, send_meeting_invitations=send_meeting_invitations)
return None
```

```
def send_and_save(self,update_fields=None,conflict_resolution='AutoResolve',send_meeting_invitations='SendToNone')
```

Expand source code
```
def send_and_save(
self, update_fields=None, conflict_resolution=AUTO_RESOLVE, send_meeting_invitations=SEND_TO_NONE
):
# Sends Message and saves a copy in the parent folder. Does not return an ItemId.
if self.id:
return self._update(
update_fieldnames=update_fields,
message_disposition=SEND_AND_SAVE_COPY,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
if self.account.version.build < EXCHANGE_2013 and self.attachments:
# At least some versions prior to Exchange 2013 can't send-and-save attachments immediately. You need
# to first save, then attach, then send. This is done in save().
self.save(
update_fields=update_fields,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
return self.send(
save_copy=False,
conflict_resolution=conflict_resolution,
send_meeting_invitations=send_meeting_invitations,
)
return self._create(message_disposition=SEND_AND_SAVE_COPY, send_meeting_invitations=send_meeting_invitations)
```

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class NoVerifyHTTPAdapter
(pool_connections=10, pool_maxsize=10, max_retries=0, pool_block=False)
```

Expand source code
```
class NoVerifyHTTPAdapter(requests.adapters.HTTPAdapter):
"""An HTTP adapter that ignores TLS validation errors. Use at own risk."""

def cert_verify(self, conn, url, verify, cert):
# pylint: disable=unused-argument
# We're overriding a method, so we have to keep the signature
super().cert_verify(conn=conn, url=url, verify=False, cert=cert)

def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
# pylint: disable=unused-argument
# Required for requests >= 2.32.3
# See: https://github.com/psf/requests/pull/6710
return super().get_connection_with_tls_context(request=request, verify=False, proxies=proxies, cert=cert)
```

An HTTP adapter that ignores TLS validation errors. Use at own risk.

### Ancestors

* requests.adapters.HTTPAdapter
* requests.adapters.BaseAdapter

### Methods

```
def cert_verify(self, conn, url, verify, cert)
```

Expand source code
```
def cert_verify(self, conn, url, verify, cert):
# pylint: disable=unused-argument
# We're overriding a method, so we have to keep the signature
super().cert_verify(conn=conn, url=url, verify=False, cert=cert)
```

Verify a SSL certificate. This method should not be called from user code, and is only exposed for use when subclassing the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

:param conn: The urllib3 connection object associated with the cert. :param url: The requested URL. :param verify: Either a boolean, in which case it controls whether we verify the server's TLS certificate, or a string, in which case it must be a path to a CA bundle to use :param cert: The SSL certificate to verify.

```
def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None)
```

Expand source code
```
def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
# pylint: disable=unused-argument
# Required for requests >= 2.32.3
# See: https://github.com/psf/requests/pull/6710
return super().get_connection_with_tls_context(request=request, verify=False, proxies=proxies, cert=cert)
```

Returns a urllib3 connection for the given request and TLS settings. This should not be called from user code, and is only exposed for use when subclassing the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

:param request: The :class:`PreparedRequest <PreparedRequest>` object to be sent over the connection. :param verify: Either a boolean, in which case it controls whether we verify the server's TLS certificate, or a string, in which case it must be a path to a CA bundle to use. :param proxies: (optional) The proxies dictionary to apply to the request. :param cert: (optional) Any user-provided SSL certificate to be used for client authentication (a.k.a., mTLS). :rtype: urllib3.ConnectionPool

```
class O365InteractiveConfiguration
(client_id, username)
```

Expand source code
```
class O365InteractiveConfiguration(Configuration):
SERVER = "outlook.office365.com"

def __init__(self, client_id, username):
credentials = O365InteractiveCredentials(client_id=client_id, username=username)
super().__init__(server=self.SERVER, auth_type=OAUTH2, credentials=credentials)
```

Contains information needed to create an authenticated connection to an EWS endpoint.

The 'credentials' argument contains the credentials needed to authenticate with the server. Multiple credentials implementations are available in 'exchangelib.credentials'.

config = Configuration(credentials=Credentials('john@example.com', 'MY_SECRET'), …)

The 'server' and 'service_endpoint' arguments are mutually exclusive. The former must contain only a domain name, the latter a full URL:

```
config = Configuration(server='example.com', ...)
config = Configuration(service_endpoint='https://mail.example.com/EWS/Exchange.asmx', ...)
```

If you know which authentication type the server uses, you add that as a hint in 'auth_type'. Likewise, you can add the server version as a hint. This allows to skip the auth type and version guessing routines:

```
config = Configuration(auth_type=NTLM, ...)
config = Configuration(version=Version(build=Build(15, 1, 2, 3)), ...)
```

You can use 'retry_policy' to define a custom retry policy for handling server connection failures:

```
config = Configuration(retry_policy=FaultTolerance(max_wait=3600), ...)
```

'max_connections' defines the max number of connections allowed for this server. This may be restricted by policies on the Exchange server.

### Ancestors

* [Configuration](https://ecederstrand.github.io/exchangelib/exchangelib/configuration.html#exchangelib.configuration.Configuration "exchangelib.configuration.Configuration")

### Class variables

`var SERVER`
The type of the None singleton.

```
class OAuth2AuthorizationCodeCredentials
(authorization_code=None, **kwargs)
```

Expand source code
```
class OAuth2AuthorizationCodeCredentials(BaseOAuth2Credentials):
"""Login info for OAuth 2.0 authentication using the authorization code grant type. This can be used in one of
several ways:
* Given an authorization code, client ID, and client secret, fetch a token ourselves and refresh it as needed if
supplied with a refresh token.
* Given an existing access token, client ID, and client secret, use the access token until it expires and then
refresh it as needed.
* Given only an existing access token, use it until it expires. This can be used to let the calling application
refresh tokens itself by subclassing and implementing refresh().

Unlike the base (client credentials) grant, authorization code credentials don't require a Microsoft tenant ID
because each access token (and the authorization code used to get the access token) is restricted to a single
tenant.
"""

def __init__(self, authorization_code=None, **kwargs):
"""

:param authorization_code: Code obtained when authorizing the application to access an account. In combination
with client_id and client_secret, will be used to obtain an access token.
"""
for attr in ("client_id", "client_secret"):
# Allow omitting these kwargs
kwargs[attr] = kwargs.pop(attr, None)
super().__init__(**kwargs)
self.authorization_code = authorization_code

@property
def scope(self):
res = super().scope
res.append("offline_access")
return res

def token_params(self):
res = super().token_params()
res["code"] = self.authorization_code # Auth code may be None
self.authorization_code = None # We can only use the code once
return res

@threaded_cached_property
def client(self):
return oauthlib.oauth2.WebApplicationClient(client_id=self.client_id)

def __repr__(self):
return self.__class__.__name__ + repr(
(self.client_id, "[client_secret]", "[authorization_code]", "[access_token]")
)

def __str__(self):
client_id = self.client_id
credential = (
"[access_token]"
if self.access_token is not None
else ("[authorization_code]" if self.authorization_code is not None else None)
)
description = " ".join(filter(None, [client_id, credential]))
return description or "[underspecified credentials]"
```

Login info for OAuth 2.0 authentication using the authorization code grant type. This can be used in one of several ways: * Given an authorization code, client ID, and client secret, fetch a token ourselves and refresh it as needed if supplied with a refresh token. * Given an existing access token, client ID, and client secret, use the access token until it expires and then refresh it as needed. * Given only an existing access token, use it until it expires. This can be used to let the calling application refresh tokens itself by subclassing and implementing refresh().

Unlike the base (client credentials) grant, authorization code credentials don't require a Microsoft tenant ID because each access token (and the authorization code used to get the access token) is restricted to a single tenant.

:param authorization_code: Code obtained when authorizing the application to access an account. In combination with client_id and client_secret, will be used to obtain an access token.

### Ancestors

* [BaseOAuth2Credentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseOAuth2Credentials "exchangelib.credentials.BaseOAuth2Credentials")
* [BaseCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseCredentials "exchangelib.credentials.BaseCredentials")

### Subclasses

* [O365InteractiveCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.O365InteractiveCredentials "exchangelib.credentials.O365InteractiveCredentials")

### Inherited members

* `BaseOAuth2Credentials`:
* `client`
* `on_token_auto_refreshed`
* `refresh`
* `scope`
* `session_params`
* `token_params`
* `token_url`

```
class OAuth2Credentials
(client_id, client_secret, tenant_id=None, identity=None, access_token=None)
```

Expand source code
```
class OAuth2Credentials(BaseOAuth2Credentials):
"""Login info for OAuth 2.0 client credentials authentication, as well as a base for other OAuth 2.0 grant types.

This is primarily useful for in-house applications accessing data from a single Microsoft account. For applications
that will access multiple tenants' data, the client credentials flow does not give the application enough
information to restrict end users' access to the appropriate account. Use OAuth2AuthorizationCodeCredentials and
the associated auth code grant type for multi-tenant applications.
"""

@threaded_cached_property
def client(self):
return oauthlib.oauth2.BackendApplicationClient(client_id=self.client_id)
```

Login info for OAuth 2.0 client credentials authentication, as well as a base for other OAuth 2.0 grant types.

This is primarily useful for in-house applications accessing data from a single Microsoft account. For applications that will access multiple tenants' data, the client credentials flow does not give the application enough information to restrict end users' access to the appropriate account. Use OAuth2AuthorizationCodeCredentials and the associated auth code grant type for multi-tenant applications.

:param client_id: ID of an authorized OAuth application, required for automatic token fetching and refreshing :param client_secret: Secret associated with the OAuth application :param tenant_id: Microsoft tenant ID of the account to access :param identity: An Identity object representing the account that these credentials are connected to. :param access_token: Previously-obtained access token, as a dict or an oauthlib.oauth2.OAuth2Token

### Ancestors

* [BaseOAuth2Credentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseOAuth2Credentials "exchangelib.credentials.BaseOAuth2Credentials")
* [BaseCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseCredentials "exchangelib.credentials.BaseCredentials")

### Subclasses

* [OAuth2LegacyCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.OAuth2LegacyCredentials "exchangelib.credentials.OAuth2LegacyCredentials")

### Inherited members

* `BaseOAuth2Credentials`:
* `client`
* `on_token_auto_refreshed`
* `refresh`
* `scope`
* `session_params`
* `token_params`
* `token_url`

```
class OAuth2LegacyCredentials
(username, password, **kwargs)
```

Expand source code
```
class OAuth2LegacyCredentials(OAuth2Credentials):
"""Login info for OAuth 2.0 authentication using delegated permissions and application permissions.

This requires the app to acquire username and password from the user and pass that when requesting authentication
tokens for the given user. This allows the app to act as the signed-in user.
"""

def __init__(self, username, password, **kwargs):
"""
:param username: The username of the user to act as
:param password: The password of the user to act as
"""
super().__init__(**kwargs)
self.username = username
self.password = password

def token_params(self):
res = super().token_params()
res["username"] = self.username
res["password"] = self.password
return res

@threaded_cached_property
def client(self):
return oauthlib.oauth2.LegacyApplicationClient(client_id=self.client_id)

@property
def scope(self):
return ["https://outlook.office365.com/EWS.AccessAsUser.All"]
```

Login info for OAuth 2.0 authentication using delegated permissions and application permissions.

This requires the app to acquire username and password from the user and pass that when requesting authentication tokens for the given user. This allows the app to act as the signed-in user.

:param username: The username of the user to act as :param password: The password of the user to act as

### Ancestors

* [OAuth2Credentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.OAuth2Credentials "exchangelib.credentials.OAuth2Credentials")
* [BaseOAuth2Credentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseOAuth2Credentials "exchangelib.credentials.BaseOAuth2Credentials")
* [BaseCredentials](https://ecederstrand.github.io/exchangelib/exchangelib/credentials.html#exchangelib.credentials.BaseCredentials "exchangelib.credentials.BaseCredentials")

### Inherited members

* `OAuth2Credentials`:
* `token_params`

* `OAuth2Credentials`:
* `on_token_auto_refreshed`
* `refresh`
* `scope`
* `session_params`
* `token_url`

* `BaseOAuth2Credentials`:
* `client`

```
class OofSettings
(**kwargs)
```

Expand source code
```
class OofSettings(EWSElement):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/oofsettings"""

ELEMENT_NAME = "OofSettings"
REQUEST_ELEMENT_NAME = "UserOofSettings"

ENABLED = "Enabled"
SCHEDULED = "Scheduled"
DISABLED = "Disabled"
STATE_CHOICES = (ENABLED, SCHEDULED, DISABLED)

state = ChoiceField(field_uri="OofState", is_required=True, choices={Choice(c) for c in STATE_CHOICES})
external_audience = ChoiceField(
field_uri="ExternalAudience", choices={Choice("None"), Choice("Known"), Choice("All")}, default="All"
)
start = DateTimeField(field_uri="StartTime")
end = DateTimeField(field_uri="EndTime")
internal_reply = MessageField(field_uri="InternalReply")
external_reply = MessageField(field_uri="ExternalReply")

def clean(self, version=None):
super().clean(version=version)
if self.state == self.SCHEDULED:
if not self.start or not self.end:
raise ValueError(f"'start' and 'end' must be set when state is {self.SCHEDULED!r}")
if self.start >= self.end:
raise ValueError("'start' must be before 'end'")
if self.end < datetime.datetime.now(tz=UTC):
raise ValueError("'end' must be in the future")
# Some servers only like UTC timestamps
self.start = self.start.astimezone(UTC)
self.end = self.end.astimezone(UTC)
if self.state != self.DISABLED and (not self.internal_reply or not self.external_reply):
raise ValueError(f"'internal_reply' and 'external_reply' must be set when state is not {self.DISABLED!r}")

@classmethod
def from_xml(cls, elem, account):
kwargs = {}
for attr in ("state", "external_audience", "internal_reply", "external_reply"):
f = cls.get_field_by_fieldname(attr)
kwargs[attr] = f.from_xml(elem=elem, account=account)
kwargs.update(OutOfOffice.duration_to_start_end(elem=elem, account=account))
cls._clear(elem)
return cls(**kwargs)

def to_xml(self, version):
self.clean(version=version)
elem = create_element(f"t:{self.REQUEST_ELEMENT_NAME}")
for attr in ("state", "external_audience"):
value = getattr(self, attr)
f = self.get_field_by_fieldname(attr)
set_xml_value(elem, f.to_xml(value, version=version))
if self.start or self.end:
duration = create_element("t:Duration")
if self.start:
f = self.get_field_by_fieldname("start")
set_xml_value(duration, f.to_xml(self.start, version=version))
if self.end:
f = self.get_field_by_fieldname("end")
set_xml_value(duration, f.to_xml(self.end, version=version))
elem.append(duration)
for attr in ("internal_reply", "external_reply"):
value = getattr(self, attr)
if value is None:
value = "" # The value can be empty, but the XML element must always be present
f = self.get_field_by_fieldname(attr)
set_xml_value(elem, f.to_xml(value, version=version))
return elem

def __hash__(self):
# Customize comparison
if self.state == self.DISABLED:
# All values except state are ignored by the server
relevant_attrs = ("state",)
elif self.state != self.SCHEDULED:
# 'start' and 'end' values are ignored by the server, and the server always returns today's date
relevant_attrs = tuple(f.name for f in self.FIELDS if f.name not in ("start", "end"))
else:
relevant_attrs = tuple(f.name for f in self.FIELDS)
return hash(tuple(getattr(self, attr) for attr in relevant_attrs))
```

### Ancestors

* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var DISABLED`
The type of the None singleton.

`var ENABLED`
The type of the None singleton.

`var REQUEST_ELEMENT_NAME`
The type of the None singleton.

`var SCHEDULED`
The type of the None singleton.

`var STATE_CHOICES`
The type of the None singleton.

### Static methods

```
def from_xml(elem, account)
```

### Instance variables

`var end`
The type of the None singleton.

`var external_audience`
The type of the None singleton.

`var external_reply`
The type of the None singleton.

`var internal_reply`
The type of the None singleton.

`var start`
The type of the None singleton.

`var state`
The type of the None singleton.

### Methods

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
super().clean(version=version)
if self.state == self.SCHEDULED:
if not self.start or not self.end:
raise ValueError(f"'start' and 'end' must be set when state is {self.SCHEDULED!r}")
if self.start >= self.end:
raise ValueError("'start' must be before 'end'")
if self.end < datetime.datetime.now(tz=UTC):
raise ValueError("'end' must be in the future")
# Some servers only like UTC timestamps
self.start = self.start.astimezone(UTC)
self.end = self.end.astimezone(UTC)
if self.state != self.DISABLED and (not self.internal_reply or not self.external_reply):
raise ValueError(f"'internal_reply' and 'external_reply' must be set when state is not {self.DISABLED!r}")
```

```
def to_xml(self, version)
```

Expand source code
```
def to_xml(self, version):
self.clean(version=version)
elem = create_element(f"t:{self.REQUEST_ELEMENT_NAME}")
for attr in ("state", "external_audience"):
value = getattr(self, attr)
f = self.get_field_by_fieldname(attr)
set_xml_value(elem, f.to_xml(value, version=version))
if self.start or self.end:
duration = create_element("t:Duration")
if self.start:
f = self.get_field_by_fieldname("start")
set_xml_value(duration, f.to_xml(self.start, version=version))
if self.end:
f = self.get_field_by_fieldname("end")
set_xml_value(duration, f.to_xml(self.end, version=version))
elem.append(duration)
for attr in ("internal_reply", "external_reply"):
value = getattr(self, attr)
if value is None:
value = "" # The value can be empty, but the XML element must always be present
f = self.get_field_by_fieldname(attr)
set_xml_value(elem, f.to_xml(value, version=version))
return elem
```

### Inherited members

* `EWSElement`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `remove_field`
* `supported_fields`
* `validate_field`

```
class PostItem
(**kwargs)
```

Expand source code
```
class PostItem(Item):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/postitem"""

ELEMENT_NAME = "PostItem"

conversation_index = Message.FIELDS["conversation_index"]
conversation_topic = Message.FIELDS["conversation_topic"]

author = Message.FIELDS["author"]
message_id = Message.FIELDS["message_id"]
is_read = Message.FIELDS["is_read"]

posted_time = DateTimeField(field_uri="postitem:PostedTime", is_read_only=True)
references = TextField(field_uri="message:References")
sender = MailboxField(field_uri="message:Sender", is_read_only=True, is_read_only_after_send=True)
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Instance variables

`var author`
The type of the None singleton.

`var conversation_index`
The type of the None singleton.

`var conversation_topic`
The type of the None singleton.

`var is_read`
The type of the None singleton.

`var message_id`
The type of the None singleton.

`var posted_time`
The type of the None singleton.

`var references`
The type of the None singleton.

`var sender`
The type of the None singleton.

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class PostReplyItem
(**kwargs)
```

Expand source code
```
class PostReplyItem(Item):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/postreplyitem"""

ELEMENT_NAME = "PostReplyItem"

# This element only has Item fields up to, and including, 'culture'
# TDO: Plus all message fields
new_body = BodyField(field_uri="NewBodyContent") # Accepts and returns Body or HTMLBody instances

culture_idx = Item.FIELDS.index_by_name("culture")
sender_idx = Message.FIELDS.index_by_name("sender")
FIELDS = Item.FIELDS[: culture_idx + 1] + Message.FIELDS[sender_idx:]
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var culture_idx`
The type of the None singleton.

`var sender_idx`
The type of the None singleton.

### Instance variables

`var author`
The type of the None singleton.

`var bcc_recipients`
The type of the None singleton.

`var cc_recipients`
The type of the None singleton.

`var conversation_index`
The type of the None singleton.

`var conversation_topic`
The type of the None singleton.

`var is_delivery_receipt_requested`
The type of the None singleton.

`var is_read`
The type of the None singleton.

`var is_read_receipt_requested`
The type of the None singleton.

`var is_response_requested`
The type of the None singleton.

`var message_id`
The type of the None singleton.

`var new_body`
The type of the None singleton.

`var received_by`
The type of the None singleton.

`var received_representing`
The type of the None singleton.

`var references`
The type of the None singleton.

`var reminder_message_data`
The type of the None singleton.

`var reply_to`
The type of the None singleton.

`var sender`
The type of the None singleton.

`var to_recipients`
The type of the None singleton.

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class Q
(*args, **kwargs)
```

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

A class with an API similar to Django Q objects. Used to implement advanced filtering logic.

### Class variables

`var AND`
The type of the None singleton.

`var CONN_TYPES`
The type of the None singleton.

`var CONTAINS`
The type of the None singleton.

`var CONTAINS_OPS`
The type of the None singleton.

`var EQ`
The type of the None singleton.

`var EXACT`
The type of the None singleton.

`var EXISTS`
The type of the None singleton.

`var GT`
The type of the None singleton.

`var GTE`
The type of the None singleton.

`var ICONTAINS`
The type of the None singleton.

`var IEXACT`
The type of the None singleton.

`var ISTARTSWITH`
The type of the None singleton.

`var LOOKUP_CONTAINS`
The type of the None singleton.

`var LOOKUP_EXACT`
The type of the None singleton.

`var LOOKUP_EXISTS`
The type of the None singleton.

`var LOOKUP_GT`
The type of the None singleton.

`var LOOKUP_GTE`
The type of the None singleton.

`var LOOKUP_ICONTAINS`
The type of the None singleton.

`var LOOKUP_IEXACT`
The type of the None singleton.

`var LOOKUP_IN`
The type of the None singleton.

`var LOOKUP_ISTARTSWITH`
The type of the None singleton.

`var LOOKUP_LT`
The type of the None singleton.

`var LOOKUP_LTE`
The type of the None singleton.

`var LOOKUP_NOT`
The type of the None singleton.

`var LOOKUP_RANGE`
The type of the None singleton.

`var LOOKUP_STARTSWITH`
The type of the None singleton.

`var LOOKUP_TYPES`
The type of the None singleton.

`var LT`
The type of the None singleton.

`var LTE`
The type of the None singleton.

`var NE`
The type of the None singleton.

`var NEVER`
The type of the None singleton.

`var NOT`
The type of the None singleton.

`var OP_TYPES`
The type of the None singleton.

`var OR`
The type of the None singleton.

`var STARTSWITH`
The type of the None singleton.

### Instance variables

`var children`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

`var conn_type`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

`var field_path`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

`var op`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

`var query_string`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

`var value`

Expand source code
```
class Q:
"""A class with an API similar to Django Q objects. Used to implement advanced filtering logic."""

# Connection types
AND = "AND"
OR = "OR"
NOT = "NOT"
NEVER = "NEVER" # This is not specified by EWS. We use it for queries that will never match, e.g. 'foo__in=()'
CONN_TYPES = {AND, OR, NOT, NEVER}

# EWS Operators
EQ = "=="
NE = "!="
GT = ">"
GTE = ">="
LT = "<"
LTE = "<="
EXACT = "exact"
IEXACT = "iexact"
CONTAINS = "contains"
ICONTAINS = "icontains"
STARTSWITH = "startswith"
ISTARTSWITH = "istartswith"
EXISTS = "exists"
OP_TYPES = {EQ, NE, GT, GTE, LT, LTE, EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH, EXISTS}
CONTAINS_OPS = {EXACT, IEXACT, CONTAINS, ICONTAINS, STARTSWITH, ISTARTSWITH}

# Valid lookups
LOOKUP_RANGE = "range"
LOOKUP_IN = "in"
LOOKUP_NOT = "not"
LOOKUP_GT = "gt"
LOOKUP_GTE = "gte"
LOOKUP_LT = "lt"
LOOKUP_LTE = "lte"
LOOKUP_EXACT = "exact"
LOOKUP_IEXACT = "iexact"
LOOKUP_CONTAINS = "contains"
LOOKUP_ICONTAINS = "icontains"
LOOKUP_STARTSWITH = "startswith"
LOOKUP_ISTARTSWITH = "istartswith"
LOOKUP_EXISTS = "exists"
LOOKUP_TYPES = {
LOOKUP_RANGE,
LOOKUP_IN,
LOOKUP_NOT,
LOOKUP_GT,
LOOKUP_GTE,
LOOKUP_LT,
LOOKUP_LTE,
LOOKUP_EXACT,
LOOKUP_IEXACT,
LOOKUP_CONTAINS,
LOOKUP_ICONTAINS,
LOOKUP_STARTSWITH,
LOOKUP_ISTARTSWITH,
LOOKUP_EXISTS,
}

__slots__ = "conn_type", "field_path", "op", "value", "children", "query_string"

def __init__(self, *args, **kwargs):
self.conn_type = kwargs.pop("conn_type", self.AND)

self.field_path = None # Name of the field we want to filter on
self.op = None
self.value = None
self.query_string = None

# Parsing of args and kwargs may require child elements
self.children = []

# Check for query string as the only argument
if not kwargs and len(args) == 1 and isinstance(args[0], str):
self.query_string = args[0]
args = ()

# Parse args which must now be Q objects
for q in args:
if not isinstance(q, self.__class__):
raise TypeError(f"Non-keyword arg {q!r} must be of type {Q}")
self.children.extend(args)

# Parse keyword args and extract the filter
is_single_kwarg = not args and len(kwargs) == 1
for key, value in kwargs.items():
self.children.extend(self._get_children_from_kwarg(key=key, value=value, is_single_kwarg=is_single_kwarg))

# Simplify this object
self.reduce()

# Final sanity check
self._check_integrity()

def _get_children_from_kwarg(self, key, value, is_single_kwarg=False):
"""Generate Q objects corresponding to a single keyword argument. Make this a leaf if there are no children to
generate.
"""
key_parts = key.rsplit("__", 1)
if len(key_parts) == 2 and key_parts[1] in self.LOOKUP_TYPES:
# This is a kwarg with a lookup at the end
field_path, lookup = key_parts
if lookup == self.LOOKUP_EXISTS:
# value=True will fall through to further processing
if not value:
return (~self.__class__(**{key: True}),)

if lookup == self.LOOKUP_RANGE:
# EWS doesn't have a 'range' operator. Emulate 'foo__range=(1, 2)' as 'foo__gte=1 and foo__lte=2'
# (both values inclusive).
if len(value) != 2:
raise ValueError(f"Value of lookup {key!r} must have exactly 2 elements")
return (
self.__class__(**{f"{field_path}__gte": value[0]}),
self.__class__(**{f"{field_path}__lte": value[1]}),
)

# Filtering on list types is a bit quirky. The only lookup type I have found to work is:
#
# item:Categories == 'foo' AND item:Categories == 'bar' AND ...
#
# item:Categories == 'foo' OR item:Categories == 'bar' OR ...
#
# The former returns items that have all these categories, but maybe also others. The latter returns
# items that have at least one of these categories. This translates to the 'contains' and 'in' lookups,
# respectively. Both versions are case-insensitive.
#
# Exact matching and case-sensitive or partial-string matching is not possible since that requires the
# 'Contains' element which only supports matching on string elements, not arrays.
#
# Exact matching of categories (i.e. match ['a', 'b'] but not ['a', 'b', 'c']) could be implemented by
# post-processing items by fetching the categories field unconditionally and removing the items that don't
# have an exact match.
if lookup == self.LOOKUP_IN:
# EWS doesn't have an '__in' operator. Allow '__in' lookups on list and non-list field types,
# specifying a list value. We'll emulate it as a set of OR'ed exact matches.
if not is_iterable(value, generators_allowed=True):
raise TypeError(f"Value for lookup {key!r} must be of type {list}")
children = tuple(self.__class__(**{field_path: v}) for v in value)
if not children:
# This is an '__in' operator with an empty list as the value. We interpret it to mean "is foo
# contained in the empty set?" which is always false. Mark this Q object as such.
return (self.__class__(conn_type=self.NEVER),)
return (self.__class__(*children, conn_type=self.OR),)

if lookup == self.LOOKUP_CONTAINS and is_iterable(value, generators_allowed=True):
# A '__contains' lookup with a list as the value ony makes sense for list fields, since exact match
# on multiple distinct values will always fail for single-value fields.
#
# An empty list as value is allowed. We interpret it to mean "are all values in the empty set contained
# in foo?" which is always true.
children = tuple(self.__class__(**{field_path: v}) for v in value)
return (self.__class__(*children, conn_type=self.AND),)

try:
op = self._lookup_to_op(lookup)
except KeyError:
raise ValueError(f"Lookup {lookup!r} is not supported (called as '{key}={value!r}')")
else:
field_path, op = key, self.EQ

if not is_single_kwarg:
return (self.__class__(**{key: value}),)

# This is a single-kwarg Q object with a lookup that requires a single value. Make this a leaf
self.field_path = field_path
self.op = op
self.value = value
return ()

def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()

def _reduce_children(self):
"""Look at the children of this object and remove unnecessary items."""
children = self.children
if any((isinstance(a, self.__class__) and a.is_never()) for a in children):
# We have at least one 'never' arg
if self.conn_type == self.AND:
# Remove all other args since nothing we AND together with a 'never' arg can change the result
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.OR:
# Remove all 'never' args because all other args will decide the result. Keep one 'never' arg in case
# all args are 'never' args.
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]
if not children:
children = [self.__class__(conn_type=self.NEVER)]
elif self.conn_type == self.NOT:
# Let's interpret 'not never' to mean 'always'. Remove all 'never' args
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_never())]

# Remove any empty Q elements in args before proceeding
children = [a for a in children if not (isinstance(a, self.__class__) and a.is_empty())]
self.children = children

def _promote(self):
"""When we only have one child and no expression on ourselves, we are a no-op. Flatten by taking over the only
child.
"""
if len(self.children) != 1 or self.field_path is not None or self.conn_type == self.NOT:
return

q = self.children[0]
self.conn_type = q.conn_type
self.field_path = q.field_path
self.op = q.op
self.value = q.value
self.query_string = q.query_string
self.children = q.children

def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)

@classmethod
def _lookup_to_op(cls, lookup):
return {
cls.LOOKUP_NOT: cls.NE,
cls.LOOKUP_GT: cls.GT,
cls.LOOKUP_GTE: cls.GTE,
cls.LOOKUP_LT: cls.LT,
cls.LOOKUP_LTE: cls.LTE,
cls.LOOKUP_EXACT: cls.EXACT,
cls.LOOKUP_IEXACT: cls.IEXACT,
cls.LOOKUP_CONTAINS: cls.CONTAINS,
cls.LOOKUP_ICONTAINS: cls.ICONTAINS,
cls.LOOKUP_STARTSWITH: cls.STARTSWITH,
cls.LOOKUP_ISTARTSWITH: cls.ISTARTSWITH,
cls.LOOKUP_EXISTS: cls.EXISTS,
}[lookup]

@classmethod
def _conn_to_xml(cls, conn_type):
xml_tag_map = {
cls.AND: "t:And",
cls.OR: "t:Or",
cls.NOT: "t:Not",
}
return create_element(xml_tag_map[conn_type])

@classmethod
def _op_to_xml(cls, op):
xml_tag_map = {
cls.EQ: "t:IsEqualTo",
cls.NE: "t:IsNotEqualTo",
cls.GTE: "t:IsGreaterThanOrEqualTo",
cls.LTE: "t:IsLessThanOrEqualTo",
cls.LT: "t:IsLessThan",
cls.GT: "t:IsGreaterThan",
cls.EXISTS: "t:Exists",
}
if op in xml_tag_map:
return create_element(xml_tag_map[op])
valid_ops = cls.EXACT, cls.IEXACT, cls.CONTAINS, cls.ICONTAINS, cls.STARTSWITH, cls.ISTARTSWITH
if op not in valid_ops:
raise InvalidEnumValue("op", op, valid_ops)

# For description of Contains attribute values, see
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/contains
#
# Possible ContainmentMode values:
# FullString, Prefixed, Substring, PrefixOnWords, ExactPhrase
# Django lookups have no equivalent of PrefixOnWords and ExactPhrase (and I'm unsure how they actually
# work).
#
# EWS has no equivalent of '__endswith' or '__iendswith'. That could be emulated using '__contains' and
# '__icontains' and filtering results afterwards in Python. But it could be inefficient because we might be
# fetching and discarding a lot of non-matching items, plus we would need to always fetch the field we're
# matching on, to be able to do the filtering. I think it's better to leave this to the consumer, i.e.:
#
# items = [i for i in fld.filter(subject__contains=suffix) if i.subject.endswith(suffix)]
# items = [i for i in fld.filter(subject__icontains=suffix) if i.subject.lower().endswith(suffix.lower())]
#
# Possible ContainmentComparison values (there are more, but the rest are "To be removed"):
# Exact, IgnoreCase, IgnoreNonSpacingCharacters, IgnoreCaseAndNonSpacingCharacters
# I'm unsure about non-spacing characters, but as I read
# https://en.wikipedia.org/wiki/Graphic_character#Spacing_and_non-spacing_characters
# we shouldn't ignore them ('a' would match both 'a' and 'å', the latter having a non-spacing character).
if op in {cls.EXACT, cls.IEXACT}:
match_mode = "FullString"
elif op in (cls.CONTAINS, cls.ICONTAINS):
match_mode = "Substring"
elif op in (cls.STARTSWITH, cls.ISTARTSWITH):
match_mode = "Prefixed"
else:
raise ValueError(f"Unsupported op: {op}")
if op in (cls.IEXACT, cls.ICONTAINS, cls.ISTARTSWITH):
compare_mode = "IgnoreCase"
else:
compare_mode = "Exact"
return create_element("t:Contains", attrs=dict(ContainmentMode=match_mode, ContainmentComparison=compare_mode))

def is_leaf(self):
return not self.children

def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER

def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER

def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr

def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction

def _check_integrity(self):
if self.is_empty():
return
if self.conn_type == self.NEVER:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("'never' queries cannot be combined with other settings")
return
if self.query_string:
if any([self.field_path, self.op, self.value, self.children]):
raise ValueError("Query strings cannot be combined with other settings")
return
if self.conn_type not in self.CONN_TYPES:
raise InvalidEnumValue("conn_type", self.conn_type, self.CONN_TYPES)
if not self.is_leaf():
for q in self.children:
if q.query_string and len(self.children) > 1:
raise ValueError("A query string cannot be combined with other restrictions")
return
if not self.field_path:
raise ValueError("'field_path' must be set")
if self.op not in self.OP_TYPES:
raise InvalidEnumValue("op", self.op, self.OP_TYPES)
if self.op == self.EXISTS and self.value is not True:
raise ValueError("'value' must be True when operator is EXISTS")
if self.value is None:
raise ValueError(f"Value for filter on field path {self.field_path!r} cannot be None")
if is_iterable(self.value, generators_allowed=True):
raise ValueError(
f"Value {self.value!r} for filter on field path {self.field_path!r} must be a single value"
)

def _validate_field_path(self, field_path, folder, applies_to, version):
from .indexed_properties import MultiFieldIndexedElement

if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
folder.validate_field(field=field_path.field, version=version)
else:
folder.validate_item_field(field=field_path.field, version=version)
if not field_path.field.is_searchable:
raise ValueError(f"EWS does not support filtering on field {field_path.field.name!r}")
if field_path.subfield and not field_path.subfield.is_searchable:
raise ValueError(f"EWS does not support filtering on subfield {field_path.subfield.name!r}")
if issubclass(field_path.field.value_cls, MultiFieldIndexedElement) and not field_path.subfield:
raise ValueError(f"Field path {self.field_path!r} must contain a subfield")

def _get_field_path(self, folders, applies_to, version):
# Convert the string field path to a real FieldPath object. The path is validated using the given folders.
for folder in folders:
try:
if applies_to == Restriction.FOLDERS:
# This is a restriction on Folder fields
field = folder.get_field_by_fieldname(fieldname=self.field_path)
field_path = FieldPath(field=field)
else:
field_path = FieldPath.from_string(field_path=self.field_path, folder=folder)
except ValueError:
continue
self._validate_field_path(field_path=field_path, folder=folder, applies_to=applies_to, version=version)
break
else:
raise InvalidField(f"Unknown field path {self.field_path!r} on folders {folders}")
return field_path

def _get_clean_value(self, field_path, version):
if self.op == self.EXISTS:
return None
clean_field = field_path.subfield if (field_path.subfield and field_path.label) else field_path.field
if clean_field.is_list:
# __contains and __in are implemented as multiple leaves, with one value per leaf. clean() on list fields
# only works on lists, so clean a one-element list.
return clean_field.clean(value=[self.value], version=version)[0]
return clean_field.clean(value=self.value, version=version)

def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem

def __and__(self, other):
# & operator. Return a new Q with two children and conn_type AND
return self.__class__(self, other, conn_type=self.AND)

def __or__(self, other):
# | operator. Return a new Q with two children and conn_type OR
return self.__class__(self, other, conn_type=self.OR)

def __invert__(self):
# ~ operator. If op has an inverse, change op. Else return a new Q with conn_type NOT
if self.conn_type == self.NOT:
# This is 'NOT NOT'. Change to 'AND'
new = copy(self)
new.conn_type = self.AND
new.reduce()
return new
if self.is_leaf():
inverse_ops = {
self.EQ: self.NE,
self.NE: self.EQ,
self.GT: self.LTE,
self.GTE: self.LT,
self.LT: self.GTE,
self.LTE: self.GT,
}
with suppress(KeyError):
new = copy(self)
new.op = inverse_ops[self.op]
new.reduce()
return new
return self.__class__(self, conn_type=self.NOT)

def __eq__(self, other):
return repr(self) == repr(other)

def __hash__(self):
return hash(repr(self))

def __str__(self):
return self.expr() or "Q()"

def __repr__(self):
if self.is_leaf():
if self.query_string:
return self.__class__.__name__ + f"({self.query_string!r})"
if self.is_never():
return self.__class__.__name__ + f"(conn_type={self.conn_type!r})"
return self.__class__.__name__ + f"({self.field_path} {self.op} {self.value!r})"
sorted_children = tuple(sorted(self.children, key=lambda i: i.field_path or ""))
if self.conn_type == self.NOT or len(self.children) > 1:
return self.__class__.__name__ + repr((self.conn_type,) + sorted_children)
return self.__class__.__name__ + repr(sorted_children)
```

### Methods

```
def clean(self, version)
```

Expand source code
```
def clean(self, version):
"""Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of
validating. There's no reason to replicate much of that here.
"""
from .folders import Folder

self.to_xml(folders=[Folder()], version=version, applies_to=Restriction.ITEMS)
```

Do some basic checks on the attributes, using a generic folder. to_xml() does a good job of validating. There's no reason to replicate much of that here.

```
def expr(self)
```

Expand source code
```
def expr(self):
if self.is_empty():
return None
if self.is_never():
return self.NEVER
if self.query_string:
return self.query_string
if self.is_leaf():
expr = f"{self.field_path} {self.op} {self.value!r}"
else:
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty.
expr = f" {self.AND if self.conn_type == self.NOT else self.conn_type} ".join(
(c.expr() if c.is_leaf() or c.conn_type == self.NOT else f"({c.expr()})")
for c in sorted(self.children, key=lambda i: i.field_path or "")
)
if self.conn_type == self.NOT:
# Add the NOT operator. Put children in parens if there is more than one child.
if self.is_leaf() or len(self.children) == 1:
return self.conn_type + f" {expr}"
return self.conn_type + f" ({expr})"
return expr
```

```
def is_empty(self)
```

Expand source code
```
def is_empty(self):
"""Return True if this object is without any restrictions at all."""
return self.is_leaf() and self.field_path is None and self.query_string is None and self.conn_type != self.NEVER
```

Return True if this object is without any restrictions at all.

```
def is_leaf(self)
```

Expand source code
```
def is_leaf(self):
return not self.children
```

```
def is_never(self)
```

Expand source code
```
def is_never(self):
"""Return True if this object has a restriction that will never match anything."""
return self.conn_type == self.NEVER
```

Return True if this object has a restriction that will never match anything.

```
def reduce(self)
```

Expand source code
```
def reduce(self):
"""Simplify this object, if possible."""
self._reduce_children()
self._promote()
```

Simplify this object, if possible.

```
def to_xml(self, folders, version, applies_to)
```

Expand source code
```
def to_xml(self, folders, version, applies_to):
if self.query_string:
self._check_integrity()
if version.build < EXCHANGE_2010:
raise NotImplementedError("QueryString filtering is only supported for Exchange 2010 servers and later")
if version.build < EXCHANGE_2013:
elem = create_element("m:QueryString")
else:
elem = create_element(
"m:QueryString", attrs=dict(ResetCache=True, ReturnDeletedItems=False, ReturnHighlightTerms=False)
)
elem.text = self.query_string
return elem
# Translate this Q object to a valid Restriction XML tree
elem = self.xml_elem(folders=folders, version=version, applies_to=applies_to)
if elem is None:
return None
restriction = create_element("m:Restriction")
restriction.append(elem)
return restriction
```

```
def xml_elem(self, folders, version, applies_to)
```

Expand source code
```
def xml_elem(self, folders, version, applies_to):
# Recursively build an XML tree structure of this Q object. If this is an empty leaf (the equivalent of Q()),
# return None.
from .indexed_properties import SingleFieldIndexedElement

# Don't check self.value just yet. We want to return error messages on the field path first, and then the value.
# This is done in _get_field_path() and _get_clean_value(), respectively.
self._check_integrity()
if self.is_empty():
return None
if self.is_never():
raise ValueError("EWS does not support 'never' queries")
if self.is_leaf():
elem = self._op_to_xml(self.op)
field_path = self._get_field_path(folders, applies_to=applies_to, version=version)
clean_value = self._get_clean_value(field_path=field_path, version=version)
if issubclass(field_path.field.value_cls, SingleFieldIndexedElement) and not field_path.label:
# We allow a filter shortcut of e.g. email_addresses__contains=EmailAddress(label='Foo', ...) instead of
# email_addresses__Foo_email_address=.... Set FieldPath label now, so we can generate the field_uri.
field_path.label = clean_value.label
elif isinstance(field_path.field, DateTimeBackedDateField):
# We need to convert to datetime
clean_value = field_path.field.date_to_datetime(clean_value)
elem.append(field_path.to_xml())
if self.op != self.EXISTS:
constant = create_element("t:Constant", attrs=dict(Value=value_to_xml_text(clean_value)))
if self.op in self.CONTAINS_OPS:
elem.append(constant)
else:
uriorconst = create_element("t:FieldURIOrConstant")
uriorconst.append(constant)
elem.append(uriorconst)
elif len(self.children) == 1:
# We have only one child
elem = self.children[0].xml_elem(folders=folders, version=version, applies_to=applies_to)
else:
# We have multiple children. If conn_type is NOT, then group children with AND. We'll add the NOT later
elem = self._conn_to_xml(self.AND if self.conn_type == self.NOT else self.conn_type)
# Sort children by field name, so we get stable output (for easier testing). Children should never be empty
for c in sorted(self.children, key=lambda i: i.field_path or ""):
elem.append(c.xml_elem(folders=folders, version=version, applies_to=applies_to))
if elem is None:
return None # Should not be necessary, but play safe
if self.conn_type == self.NOT:
# Encapsulate everything in the NOT element
not_elem = self._conn_to_xml(self.conn_type)
not_elem.append(elem)
return not_elem
return elem
```

```
class ReplyAllToItem
(**kwargs)
```

Expand source code
```
class ReplyAllToItem(BaseReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/replyalltoitem"""

ELEMENT_NAME = "ReplyAllToItem"
```

### Ancestors

* [BaseReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseReplyItem "exchangelib.items.base.BaseReplyItem")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `author`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `new_body`
* `received_by`
* `received_representing`
* `reference_item_id`
* `remove_field`
* `save`
* `subject`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class ReplyToItem
(**kwargs)
```

Expand source code
```
class ReplyToItem(BaseReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/replytoitem"""

ELEMENT_NAME = "ReplyToItem"
```

### Ancestors

* [BaseReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseReplyItem "exchangelib.items.base.BaseReplyItem")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `NAMESPACE`
* `add_field`
* `author`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `new_body`
* `received_by`
* `received_representing`
* `reference_item_id`
* `remove_field`
* `save`
* `subject`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class Room
(**kwargs)
```

Expand source code
```
class Room(Mailbox):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/room"""

ELEMENT_NAME = "Room"

@classmethod
def from_xml(cls, elem, account):
id_elem = elem.find(f"{{{TNS}}}Id")
item_id_elem = id_elem.find(ItemId.response_tag())
kwargs = dict(
name=get_xml_attr(id_elem, f"{{{TNS}}}Name"),
email_address=get_xml_attr(id_elem, f"{{{TNS}}}EmailAddress"),
mailbox_type=get_xml_attr(id_elem, f"{{{TNS}}}MailboxType"),
item_id=ItemId.from_xml(elem=item_id_elem, account=account) if item_id_elem else None,
)
cls._clear(elem)
return cls(**kwargs)
```

### Ancestors

* [Mailbox](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Mailbox "exchangelib.properties.Mailbox")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Static methods

```
def from_xml(elem, account)
```

### Inherited members

* `Mailbox`:
* `ELEMENT_NAME`
* `FIELDS`
* `MAILBOX`
* `MAILBOX_TYPE_CHOICES`
* `NAMESPACE`
* `ONE_OFF`
* `add_field`
* `email_address`
* `item_id`
* `mailbox_type`
* `name`
* `remove_field`
* `routing_type`
* `supported_fields`
* `validate_field`

```
class RoomList
(**kwargs)
```

Expand source code
```
class RoomList(Mailbox):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/roomlist"""

ELEMENT_NAME = "RoomList"
NAMESPACE = MNS

@classmethod
def response_tag(cls):
# In a GetRoomLists response, room lists are delivered as Address elements. See
# https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/address-emailaddresstype
return f"{{{TNS}}}Address"
```

### Ancestors

* [Mailbox](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.Mailbox "exchangelib.properties.Mailbox")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Static methods

```
def response_tag()
```

### Inherited members

* `Mailbox`:
* `ELEMENT_NAME`
* `FIELDS`
* `MAILBOX`
* `MAILBOX_TYPE_CHOICES`
* `NAMESPACE`
* `ONE_OFF`
* `add_field`
* `email_address`
* `item_id`
* `mailbox_type`
* `name`
* `remove_field`
* `routing_type`
* `supported_fields`
* `validate_field`

```
class RootOfHierarchy
(**kwargs)
```

Expand source code
```
class RootOfHierarchy(BaseFolder, metaclass=EWSMeta):
"""Base class for folders that implement the root of a folder hierarchy."""

# A list of wellknown, or "distinguished", folders that are belong in this folder hierarchy. See
# https://docs.microsoft.com/en-us/dotnet/api/microsoft.exchange.webservices.data.wellknownfoldername
# and https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/distinguishedfolderid
# 'RootOfHierarchy' subclasses must not be in this list.
WELLKNOWN_FOLDERS = []

# This folder type also has 'folder:PermissionSet' on some server versions, but requesting it sometimes causes
# 'ErrorAccessDenied', as reported by some users. Ignore it entirely for root folders - it's usefulness is
# deemed minimal at best.
effective_rights = EffectiveRightsField(
field_uri="folder:EffectiveRights", is_read_only=True, supported_from=EXCHANGE_2007_SP1
)

__slots__ = "_account", "_subfolders", "_subfolders_lock"

# A special folder that acts as the top of a folder hierarchy. Finds and caches sub-folders at arbitrary depth.
def __init__(self, **kwargs):
self._account = kwargs.pop("account", None) # A pointer back to the account holding the folder hierarchy
super().__init__(**kwargs)
self._subfolders = None # See self._folders_map()
self._subfolders_lock = Lock()

@property
def account(self):
return self._account

@property
def root(self):
return self

@property
def parent(self):
return None

@classmethod
def register(cls, *args, **kwargs):
if cls is not RootOfHierarchy:
raise TypeError("For folder roots, custom fields must be registered on the RootOfHierarchy class")
return super().register(*args, **kwargs)

@classmethod
def deregister(cls, *args, **kwargs):
if cls is not RootOfHierarchy:
raise TypeError("For folder roots, custom fields must be registered on the RootOfHierarchy class")
return super().deregister(*args, **kwargs)

def get_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
return self._folders_map.get(folder.id)

def add_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
self._folders_map[folder.id] = folder

def update_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
self._folders_map[folder.id] = folder

def remove_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
with suppress(KeyError):
del self._folders_map[folder.id]

def clear_cache(self):
with self._subfolders_lock:
self._subfolders = None

def get_children(self, folder):
for f in self._folders_map.values():
if not f.parent:
continue
if f.parent.id == folder.id:
yield f

def get_default_folder(self, folder_cls):
"""Return the distinguished folder instance of type folder_cls belonging to this account. If no distinguished
folder was found, try as best we can to return the default folder of type 'folder_cls'
"""
if not folder_cls.DISTINGUISHED_FOLDER_ID:
raise ValueError(f"'folder_cls' {folder_cls} must have a DISTINGUISHED_FOLDER_ID value")
# Use cached distinguished folder instance, but only if cache has already been prepped. This is an optimization
# for accessing e.g. 'account.contacts' without fetching all folders of the account.
if self._subfolders is not None:
for f in self._folders_map.values():
# Require exact class, to not match subclasses, e.g. RecipientCache instead of Contacts
if f.__class__ == folder_cls and f.is_distinguished:
log.debug("Found cached distinguished %s folder", folder_cls)
return f
try:
log.debug("Requesting distinguished %s folder explicitly", folder_cls)
return folder_cls.get_distinguished(root=self)
except ErrorAccessDenied:
# Maybe we just don't have GetFolder access? Try FindItem instead
log.debug("Testing default %s folder with FindItem", folder_cls)
fld = folder_cls(
_distinguished_id=DistinguishedFolderId(
id=folder_cls.DISTINGUISHED_FOLDER_ID,
mailbox=Mailbox(email_address=self.account.primary_smtp_address),
),
root=self,
)
fld.test_access()
return self._folders_map.get(fld.id, fld) # Use cached instance if available
except MISSING_FOLDER_ERRORS:
# The Exchange server does not return a distinguished folder of this type
pass
raise ErrorFolderNotFound(f"No usable default {folder_cls} folders")

@classmethod
def get_distinguished(cls, account):
"""Get the distinguished folder for this folder class.

:param account:
:return:
"""
return cls._get_distinguished(
folder=cls(
_distinguished_id=DistinguishedFolderId(
id=cls.DISTINGUISHED_FOLDER_ID,
mailbox=Mailbox(email_address=account.primary_smtp_address),
),
account=account,
)
)

@property
def _folders_map(self):
if self._subfolders is not None:
return self._subfolders

with self._subfolders_lock:
# Map root, and all sub-folders of root, at arbitrary depth by folder ID. First get distinguished folders,
# so we are sure to apply the correct Folder class, then fetch all sub-folders of this root.
folders_map = {self.id: self}
distinguished_folders = [
cls(
_distinguished_id=DistinguishedFolderId(
id=cls.DISTINGUISHED_FOLDER_ID,
mailbox=Mailbox(email_address=self.account.primary_smtp_address),
),
root=self,
)
for cls in self.WELLKNOWN_FOLDERS
if cls.get_folder_allowed and cls.supports_version(self.account.version)
]
for f in FolderCollection(account=self.account, folders=distinguished_folders).resolve():
if isinstance(f, MISSING_FOLDER_ERRORS):
# This is just a distinguished folder the server does not have
continue
if isinstance(f, ErrorInvalidOperation):
# This is probably a distinguished folder the server does not have. We previously tested the exact
# error message (f.value), but some Exchange servers return localized error messages, so that's not
# possible to do reliably.
continue
if isinstance(f, ErrorAccessDenied):
# We may not have GetFolder access, either to this folder or at all
continue
if isinstance(f, Exception):
raise f
folders_map[f.id] = f
for f in (
SingleFolderQuerySet(account=self.account, folder=self).depth(self.DEFAULT_FOLDER_TRAVERSAL_DEPTH).all()
):
if isinstance(f, ErrorAccessDenied):
# We may not have FindFolder access, or GetFolder access, either to this folder or at all
continue
if isinstance(f, MISSING_FOLDER_ERRORS):
# We were unlucky. The folder disappeared between the FindFolder and the GetFolder calls
continue
if isinstance(f, Exception):
raise f
if f.id in folders_map:
# Already exists. Probably a distinguished folder
continue
folders_map[f.id] = f
self._subfolders = folders_map
return folders_map

@classmethod
def from_xml(cls, elem, account):
kwargs = cls._kwargs_from_elem(elem=elem, account=account)
cls._clear(elem)
return cls(account=account, **kwargs)

@classmethod
def folder_cls_from_folder_name(cls, folder_name, folder_class, locale):
"""Return the folder class that matches a localized folder name. Take into account the 'folder_class' of the
folder, to not identify an 'IPF.Note' folder as a 'Calendar' class just because it's called e.g. 'Kalender' and
the locale is 'da_DK'.

Some folders, e.g. `System`, don't define a `folder_class`. For these folders, we match on localized folder name
if the folder class does not have its 'CONTAINER_CLASS' set.

:param folder_name:
:param folder_class:
:param locale: a string, e.g. 'da_DK'
"""
for folder_cls in cls.WELLKNOWN_FOLDERS + NON_DELETABLE_FOLDERS + MISC_FOLDERS:
if folder_cls.CONTAINER_CLASS != folder_class:
continue
if folder_name.lower() not in folder_cls.localized_names(locale):
continue
return folder_cls
raise KeyError()

def __getstate__(self):
# The lock cannot be pickled
state = {k: getattr(self, k) for k in self._slots_keys}
del state["_subfolders_lock"]
return state

def __setstate__(self, state):
# Restore the lock
for k in self._slots_keys:
setattr(self, k, state.get(k))
self._subfolders_lock = Lock()

def __repr__(self):
# Let's not create an infinite loop when printing self.root
return self.__class__.__name__ + repr(
(
self.account,
"[self]",
self.name,
self.total_count,
self.unread_count,
self.child_folder_count,
self.folder_class,
self.id,
self.changekey,
)
)
```

Base class for folders that implement the root of a folder hierarchy.

### Ancestors

* [BaseFolder](https://ecederstrand.github.io/exchangelib/exchangelib/folders/base.html#exchangelib.folders.base.BaseFolder "exchangelib.folders.base.BaseFolder")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")
* [SearchableMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/queryset.html#exchangelib.queryset.SearchableMixIn "exchangelib.queryset.SearchableMixIn")
* [SupportedVersionClassMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/version.html#exchangelib.version.SupportedVersionClassMixIn "exchangelib.version.SupportedVersionClassMixIn")

### Subclasses

* [ArchiveRoot](https://ecederstrand.github.io/exchangelib/exchangelib/folders/roots.html#exchangelib.folders.roots.ArchiveRoot "exchangelib.folders.roots.ArchiveRoot")
* [PublicFoldersRoot](https://ecederstrand.github.io/exchangelib/exchangelib/folders/roots.html#exchangelib.folders.roots.PublicFoldersRoot "exchangelib.folders.roots.PublicFoldersRoot")
* [Root](https://ecederstrand.github.io/exchangelib/exchangelib/folders/roots.html#exchangelib.folders.roots.Root "exchangelib.folders.roots.Root")

### Class variables

`var WELLKNOWN_FOLDERS`
The type of the None singleton.

### Static methods

```
def folder_cls_from_folder_name(folder_name, folder_class, locale)
```

Return the folder class that matches a localized folder name. Take into account the 'folder_class' of the folder, to not identify an 'IPF.Note' folder as a 'Calendar' class just because it's called e.g. 'Kalender' and the locale is 'da_DK'.

Some folders, e.g. `System`, don't define a `folder_class`. For these folders, we match on localized folder name if the folder class does not have its 'CONTAINER_CLASS' set.

:param folder_name: :param folder_class: :param locale: a string, e.g. 'da_DK'

```
def from_xml(elem, account)
```

```
def get_distinguished(account)
```

Get the distinguished folder for this folder class.

:param account: :return:

### Instance variables

`var effective_rights`
The type of the None singleton.

### Methods

```
def add_folder(self, folder)
```

Expand source code
```
def add_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
self._folders_map[folder.id] = folder
```

```
def clear_cache(self)
```

Expand source code
```
def clear_cache(self):
with self._subfolders_lock:
self._subfolders = None
```

```
def get_children(self, folder)
```

Expand source code
```
def get_children(self, folder):
for f in self._folders_map.values():
if not f.parent:
continue
if f.parent.id == folder.id:
yield f
```

```
def get_default_folder(self, folder_cls)
```

Expand source code
```
def get_default_folder(self, folder_cls):
"""Return the distinguished folder instance of type folder_cls belonging to this account. If no distinguished
folder was found, try as best we can to return the default folder of type 'folder_cls'
"""
if not folder_cls.DISTINGUISHED_FOLDER_ID:
raise ValueError(f"'folder_cls' {folder_cls} must have a DISTINGUISHED_FOLDER_ID value")
# Use cached distinguished folder instance, but only if cache has already been prepped. This is an optimization
# for accessing e.g. 'account.contacts' without fetching all folders of the account.
if self._subfolders is not None:
for f in self._folders_map.values():
# Require exact class, to not match subclasses, e.g. RecipientCache instead of Contacts
if f.__class__ == folder_cls and f.is_distinguished:
log.debug("Found cached distinguished %s folder", folder_cls)
return f
try:
log.debug("Requesting distinguished %s folder explicitly", folder_cls)
return folder_cls.get_distinguished(root=self)
except ErrorAccessDenied:
# Maybe we just don't have GetFolder access? Try FindItem instead
log.debug("Testing default %s folder with FindItem", folder_cls)
fld = folder_cls(
_distinguished_id=DistinguishedFolderId(
id=folder_cls.DISTINGUISHED_FOLDER_ID,
mailbox=Mailbox(email_address=self.account.primary_smtp_address),
),
root=self,
)
fld.test_access()
return self._folders_map.get(fld.id, fld) # Use cached instance if available
except MISSING_FOLDER_ERRORS:
# The Exchange server does not return a distinguished folder of this type
pass
raise ErrorFolderNotFound(f"No usable default {folder_cls} folders")
```

Return the distinguished folder instance of type folder_cls belonging to this account. If no distinguished folder was found, try as best we can to return the default folder of type 'folder_cls'

```
def get_folder(self, folder)
```

Expand source code
```
def get_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
return self._folders_map.get(folder.id)
```

```
def remove_folder(self, folder)
```

Expand source code
```
def remove_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
with suppress(KeyError):
del self._folders_map[folder.id]
```

```
def update_folder(self, folder)
```

Expand source code
```
def update_folder(self, folder):
if not folder.id:
raise ValueError("'folder' must have an ID")
self._folders_map[folder.id] = folder
```

### Inherited members

* `BaseFolder`:
* `CONTAINER_CLASS`
* `DEFAULT_FOLDER_TRAVERSAL_DEPTH`
* `DEFAULT_ITEM_TRAVERSAL_DEPTH`
* `DISTINGUISHED_FOLDER_ID`
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `ITEM_MODEL_MAP`
* `LOCALIZED_NAMES`
* `NAMESPACE`
* `account`
* `add_field`
* `all`
* `child_folder_count`
* `deprecated_from`
* `deregister`
* `exclude`
* `filter`
* `folder_class`
* `folder_cls_from_container_class`
* `get`
* `get_events`
* `get_folder_allowed`
* `get_streaming_events`
* `name`
* `none`
* `parent`
* `parent_folder_id`
* `people`
* `register`
* `remove_field`
* `root`
* `subscribe_to_pull`
* `subscribe_to_push`
* `subscribe_to_streaming`
* `supported_fields`
* `supported_from`
* `supported_item_models`
* `sync_hierarchy`
* `sync_items`
* `test_access`
* `total_count`
* `tree`
* `unread_count`
* `unsubscribe`
* `validate_field`

```
class TLSClientAuth
(pool_connections=10, pool_maxsize=10, max_retries=0, pool_block=False)
```

Expand source code
```
class TLSClientAuth(requests.adapters.HTTPAdapter):
"""An HTTP adapter that implements Certificate Based Authentication (CBA)."""

cert_file = None

def init_poolmanager(self, *args, **kwargs):
kwargs["cert_file"] = self.cert_file
return super().init_poolmanager(*args, **kwargs)
```

An HTTP adapter that implements Certificate Based Authentication (CBA).

### Ancestors

* requests.adapters.HTTPAdapter
* requests.adapters.BaseAdapter

### Class variables

`var cert_file`
The type of the None singleton.

### Methods

```
def init_poolmanager(self, *args, **kwargs)
```

Expand source code
```
def init_poolmanager(self, *args, **kwargs):
kwargs["cert_file"] = self.cert_file
return super().init_poolmanager(*args, **kwargs)
```

Initializes a urllib3 PoolManager.

This method should not be called from user code, and is only exposed for use when subclassing the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

:param connections: The number of urllib3 connection pools to cache. :param maxsize: The maximum number of connections to save in the pool. :param block: Block when no free connections are available. :param pool_kwargs: Extra keyword arguments used to initialize the Pool Manager.

```
class Task
(**kwargs)
```

Expand source code
```
class Task(Item):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/task"""

ELEMENT_NAME = "Task"
NOT_STARTED = "NotStarted"
COMPLETED = "Completed"

actual_work = IntegerField(field_uri="task:ActualWork", min=0)
assigned_time = DateTimeField(field_uri="task:AssignedTime", is_read_only=True)
billing_information = TextField(field_uri="task:BillingInformation")
change_count = IntegerField(field_uri="task:ChangeCount", is_read_only=True, min=0)
companies = TextListField(field_uri="task:Companies")
# 'complete_date' can be set, but is ignored by the server, which sets it to now()
complete_date = DateTimeField(field_uri="task:CompleteDate", is_read_only=True)
contacts = TextListField(field_uri="task:Contacts")
delegation_state = ChoiceField(
field_uri="task:DelegationState",
choices={
Choice("NoMatch"),
Choice("OwnNew"),
Choice("Owned"),
Choice("Accepted"),
Choice("Declined"),
Choice("Max"),
},
is_read_only=True,
)
delegator = CharField(field_uri="task:Delegator", is_read_only=True)
due_date = DateTimeBackedDateField(field_uri="task:DueDate")
is_editable = BooleanField(field_uri="task:IsAssignmentEditable", is_read_only=True)
is_complete = BooleanField(field_uri="task:IsComplete", is_read_only=True)
is_recurring = BooleanField(field_uri="task:IsRecurring", is_read_only=True)
is_team_task = BooleanField(field_uri="task:IsTeamTask", is_read_only=True)
mileage = TextField(field_uri="task:Mileage")
owner = CharField(field_uri="task:Owner", is_read_only=True)
percent_complete = DecimalField(
field_uri="task:PercentComplete",
is_required=True,
default=Decimal(0.0),
min=Decimal(0),
max=Decimal(100),
is_searchable=False,
)
recurrence = TaskRecurrenceField(field_uri="task:Recurrence", is_searchable=False)
start_date = DateTimeBackedDateField(field_uri="task:StartDate")
status = ChoiceField(
field_uri="task:Status",
choices={
Choice(NOT_STARTED),
Choice("InProgress"),
Choice(COMPLETED),
Choice("WaitingOnOthers"),
Choice("Deferred"),
},
is_required=True,
is_searchable=False,
default=NOT_STARTED,
)
status_description = CharField(field_uri="task:StatusDescription", is_read_only=True)
total_work = IntegerField(field_uri="task:TotalWork", min=0)

# O365 throws ErrorInternalServerError "[0x004f0102] MapiReplyToBlob" if UniqueBody is requested
unique_body_idx = Item.FIELDS.index_by_name("unique_body")
FIELDS = Item.FIELDS[:unique_body_idx] + Item.FIELDS[unique_body_idx + 1 :]

def clean(self, version=None):
super().clean(version=version)
if self.due_date and self.start_date and self.due_date < self.start_date:
log.warning(
"'due_date' must be greater than 'start_date' (%s vs %s). Resetting 'due_date'",
self.due_date,
self.start_date,
)
self.due_date = self.start_date
if self.complete_date:
if self.status != self.COMPLETED:
log.warning(
"'status' must be '%s' when 'complete_date' is set (%s). Resetting", self.COMPLETED, self.status
)
self.status = self.COMPLETED
now = datetime.datetime.now(tz=UTC)
if (self.complete_date - now).total_seconds() > 120:
# Reset complete_date values that are in the future
# 'complete_date' can be set automatically by the server. Allow some grace between local and server time
log.warning("'complete_date' must be in the past (%s vs %s). Resetting", self.complete_date, now)
self.complete_date = now
if self.start_date and self.complete_date.date() < self.start_date:
log.warning(
"'complete_date' must be greater than 'start_date' (%s vs %s). Resetting",
self.complete_date,
self.start_date,
)
self.complete_date = EWSDateTime.combine(self.start_date, datetime.time(0, 0)).replace(tzinfo=UTC)
if self.percent_complete is not None:
if self.status == self.COMPLETED and self.percent_complete != Decimal(100):
# percent_complete must be 100% if task is complete
log.warning(
"'percent_complete' must be 100 when 'status' is '%s' (%s). Resetting",
self.COMPLETED,
self.percent_complete,
)
self.percent_complete = Decimal(100)
elif self.status == self.NOT_STARTED and self.percent_complete != Decimal(0):
# percent_complete must be 0% if task is not started
log.warning(
"'percent_complete' must be 0 when 'status' is '%s' (%s). Resetting",
self.NOT_STARTED,
self.percent_complete,
)
self.percent_complete = Decimal(0)

def complete(self):
# A helper method to mark a task as complete on the server
self.status = Task.COMPLETED
self.percent_complete = Decimal(100)
self.save()
```

### Ancestors

* [Item](https://ecederstrand.github.io/exchangelib/exchangelib/items/item.html#exchangelib.items.item.Item "exchangelib.items.item.Item")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Class variables

`var COMPLETED`
The type of the None singleton.

`var NOT_STARTED`
The type of the None singleton.

`var unique_body_idx`
The type of the None singleton.

### Instance variables

`var actual_work`
The type of the None singleton.

`var assigned_time`
The type of the None singleton.

`var billing_information`
The type of the None singleton.

`var change_count`
The type of the None singleton.

`var companies`
The type of the None singleton.

`var complete_date`
The type of the None singleton.

`var contacts`
The type of the None singleton.

`var delegation_state`
The type of the None singleton.

`var delegator`
The type of the None singleton.

`var due_date`
The type of the None singleton.

`var is_complete`
The type of the None singleton.

`var is_editable`
The type of the None singleton.

`var is_recurring`
The type of the None singleton.

`var is_team_task`
The type of the None singleton.

`var mileage`
The type of the None singleton.

`var owner`
The type of the None singleton.

`var percent_complete`
The type of the None singleton.

`var recurrence`
The type of the None singleton.

`var start_date`
The type of the None singleton.

`var status`
The type of the None singleton.

`var status_description`
The type of the None singleton.

`var total_work`
The type of the None singleton.

### Methods

```
def clean(self, version=None)
```

Expand source code
```
def clean(self, version=None):
super().clean(version=version)
if self.due_date and self.start_date and self.due_date < self.start_date:
log.warning(
"'due_date' must be greater than 'start_date' (%s vs %s). Resetting 'due_date'",
self.due_date,
self.start_date,
)
self.due_date = self.start_date
if self.complete_date:
if self.status != self.COMPLETED:
log.warning(
"'status' must be '%s' when 'complete_date' is set (%s). Resetting", self.COMPLETED, self.status
)
self.status = self.COMPLETED
now = datetime.datetime.now(tz=UTC)
if (self.complete_date - now).total_seconds() > 120:
# Reset complete_date values that are in the future
# 'complete_date' can be set automatically by the server. Allow some grace between local and server time
log.warning("'complete_date' must be in the past (%s vs %s). Resetting", self.complete_date, now)
self.complete_date = now
if self.start_date and self.complete_date.date() < self.start_date:
log.warning(
"'complete_date' must be greater than 'start_date' (%s vs %s). Resetting",
self.complete_date,
self.start_date,
)
self.complete_date = EWSDateTime.combine(self.start_date, datetime.time(0, 0)).replace(tzinfo=UTC)
if self.percent_complete is not None:
if self.status == self.COMPLETED and self.percent_complete != Decimal(100):
# percent_complete must be 100% if task is complete
log.warning(
"'percent_complete' must be 100 when 'status' is '%s' (%s). Resetting",
self.COMPLETED,
self.percent_complete,
)
self.percent_complete = Decimal(100)
elif self.status == self.NOT_STARTED and self.percent_complete != Decimal(0):
# percent_complete must be 0% if task is not started
log.warning(
"'percent_complete' must be 0 when 'status' is '%s' (%s). Resetting",
self.NOT_STARTED,
self.percent_complete,
)
self.percent_complete = Decimal(0)
```

```
def complete(self)
```

Expand source code
```
def complete(self):
# A helper method to mark a task as complete on the server
self.status = Task.COMPLETED
self.percent_complete = Decimal(100)
self.save()
```

### Inherited members

* `Item`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attach`
* `attachments`
* `body`
* `categories`
* `conversation_id`
* `culture`
* `datetime_created`
* `datetime_received`
* `datetime_sent`
* `deregister`
* `detach`
* `display_cc`
* `display_to`
* `effective_rights`
* `has_attachments`
* `headers`
* `importance`
* `in_reply_to`
* `is_associated`
* `is_draft`
* `is_from_me`
* `is_resend`
* `is_submitted`
* `is_unmodified`
* `item_class`
* `last_modified_name`
* `last_modified_time`
* `mime_content`
* `parent_folder_id`
* `register`
* `reminder_due_by`
* `reminder_is_set`
* `reminder_minutes_before_start`
* `remove_field`
* `response_objects`
* `sensitivity`
* `size`
* `subject`
* `supported_fields`
* `text_body`
* `unique_body`
* `validate_field`
* `web_client_edit_form_query_string`
* `web_client_read_form_query_string`

```
class TentativelyAcceptItem
(**kwargs)
```

Expand source code
```
class TentativelyAcceptItem(BaseMeetingReplyItem):
"""MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/tentativelyacceptitem"""

ELEMENT_NAME = "TentativelyAcceptItem"
```

### Ancestors

* [BaseMeetingReplyItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/calendar_item.html#exchangelib.items.calendar_item.BaseMeetingReplyItem "exchangelib.items.calendar_item.BaseMeetingReplyItem")
* [BaseItem](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.BaseItem "exchangelib.items.base.BaseItem")
* [RegisterMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/items/base.html#exchangelib.items.base.RegisterMixIn "exchangelib.items.base.RegisterMixIn")
* [IdChangeKeyMixIn](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.IdChangeKeyMixIn "exchangelib.properties.IdChangeKeyMixIn")
* [EWSElement](https://ecederstrand.github.io/exchangelib/exchangelib/properties.html#exchangelib.properties.EWSElement "exchangelib.properties.EWSElement")

### Inherited members

* `BaseMeetingReplyItem`:
* `ELEMENT_NAME`
* `FIELDS`
* `ID_ELEMENT_CLS`
* `INSERT_AFTER_FIELD`
* `NAMESPACE`
* `add_field`
* `attachments`
* `bcc_recipients`
* `body`
* `cc_recipients`
* `deregister`
* `headers`
* `is_delivery_receipt_requested`
* `is_read_receipt_requested`
* `item_class`
* `proposed_end`
* `proposed_start`
* `received_by`
* `received_representing`
* `reference_item_id`
* `register`
* `remove_field`
* `sender`
* `sensitivity`
* `supported_fields`
* `to_recipients`
* `validate_field`

```
class UID
(uid)
```

Expand source code
```
class UID(bytes):
"""Helper class to encode Calendar UIDs. See issue #453. Example:

class GlobalObjectId(ExtendedProperty):
distinguished_property_set_id = 'Meeting'
property_id = 3
property_type = 'Binary'

CalendarItem.register('global_object_id', GlobalObjectId)
account.calendar.filter(global_object_id=UID('261cbc18-1f65-5a0a-bd11-23b1e224cc2f'))
"""

_HEADER = binascii.hexlify(
bytearray((0x04, 0x00, 0x00, 0x00, 0x82, 0x00, 0xE0, 0x00, 0x74, 0xC5, 0xB7, 0x10, 0x1A, 0x82, 0xE0, 0x08))
)

_EXCEPTION_REPLACEMENT_TIME = binascii.hexlify(bytearray((0, 0, 0, 0)))

_CREATION_TIME = binascii.hexlify(bytearray((0, 0, 0, 0, 0, 0, 0, 0)))

_RESERVED = binascii.hexlify(bytearray((0, 0, 0, 0, 0, 0, 0, 0)))

# https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxocal/1d3aac05-a7b9-45cc-a213-47f0a0a2c5c1
# https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-asemail/e7424ddc-dd10-431e-a0b7-5c794863370e
# https://stackoverflow.com/questions/42259122
# https://stackoverflow.com/questions/33757805

def __new__(cls, uid):
payload = binascii.hexlify(bytearray(f"vCal-Uid\x01\x00\x00\x00{uid}\x00".encode("ascii")))
length = binascii.hexlify(bytearray(struct.pack("<I", int(len(payload) / 2))))
encoding = b"".join(
[cls._HEADER, cls._EXCEPTION_REPLACEMENT_TIME, cls._CREATION_TIME, cls._RESERVED, length, payload]
)
return super().__new__(cls, codecs.decode(encoding, "hex"))

@classmethod
def to_global_object_id(cls, uid):
"""Converts a UID as returned by EWS to GlobalObjectId format"""
return binascii.unhexlify(uid)
```

Helper class to encode Calendar UIDs. See issue #453. Example:

class GlobalObjectId(ExtendedProperty): distinguished_property_set_id = 'Meeting' property_id = 3 property_type = 'Binary'

CalendarItem.register('global_object_id', GlobalObjectId) account.calendar.filter(global_object_id=UID('261cbc18-1f65-5a0a-bd11-23b1e224cc2f'))

### Ancestors

* builtins.bytes

### Static methods

```
def to_global_object_id(uid)
```

Converts a UID as returned by EWS to GlobalObjectId format

```
class Version
(build, api_version=None)
```

Expand source code
```
class Version:
"""Holds information about the server version."""

__slots__ = "build", "api_version"

def __init__(self, build, api_version=None):
if api_version is None:
if not isinstance(build, Build):
raise InvalidTypeError("build", build, Build)
self.api_version = build.api_version()
else:
if not isinstance(build, (Build, type(None))):
raise InvalidTypeError("build", build, Build)
if not isinstance(api_version, str):
raise InvalidTypeError("api_version", api_version, str)
self.api_version = api_version
self.build = build

@property
def fullname(self):
for build, api_version, full_name in VERSIONS:
if self.build and (
self.build.major_version != build.major_version or self.build.minor_version != build.minor_version
):
continue
if self.api_version == api_version:
return full_name
log.warning("Full name for API version %s build %s is unknown", self.api_version, self.build)
return "UNKNOWN"

@classmethod
def guess(cls, protocol, api_version_hint=None):
"""Ask the server which version it has. We haven't set up an Account object yet, so we generate requests
by hand. We only need a response header containing a ServerVersionInfo element.

To get API version and build numbers from the server, we need to send a valid SOAP request. We can't do that
without a valid API version. To solve this chicken-and-egg problem, we try all possible API versions that this
package supports, until we get a valid response.

:param protocol:
:param api_version_hint: (Default value = None)
"""
from .properties import ENTRY_ID, EWS_ID, AlternateId
from .services import ConvertId

# The protocol doesn't have a version yet, so default to the latest supported version if we don't have a hint.
api_version = api_version_hint or ConvertId.supported_api_versions()[0]
log.debug("Asking server for version info using API version %s", api_version)
# We don't know the build version yet. Hopefully, the server will report it in the SOAP header. Lots of
# places expect a version to have a build, so this is a bit dangerous, but passing a fake build around is also
# dangerous.
protocol.config.version = Version(build=None, api_version=api_version)
# Use ConvertId as a minimal request to the server to test if the version is correct. If not, ConvertId will
# try to guess the version automatically. Make sure the call to ConvertId does not require a version build.
try:
list(ConvertId(protocol=protocol).call([AlternateId(id="DUMMY", format=EWS_ID, mailbox="DUMMY")], ENTRY_ID))
except ResponseMessageError as e:
# We may have survived long enough to get a new version
if not protocol.config.version.build:
raise TransportError(f"No valid version headers found in response ({e!r})")
if not protocol.config.version.build:
raise TransportError("No valid version headers found in response")
return protocol.config.version

@staticmethod
def _is_invalid_version_string(version):
# Check if a version string is bogus, e.g. V2_, V2015_ or V2018_
return re.match(r"V[0-9]{1,4}_.*", version)

@classmethod
def from_soap_header(cls, requested_api_version, header):
info = header.find(f"{{{TNS}}}ServerVersionInfo")
if info is None:
info = header.find(f"{{{ANS}}}ServerVersionInfo")
if info is None:
raise TransportError(f"No ServerVersionInfo in header: {xml_to_str(header)!r}")
try:
build = Build.from_xml(elem=info)
except ValueError:
raise TransportError(f"Bad ServerVersionInfo in response: {xml_to_str(header)!r}")
# Not all Exchange servers send the Version element
api_version_from_server = info.get("Version") or get_xml_attr(info, f"{{{ANS}}}Version") or build.api_version()
if api_version_from_server != requested_api_version:
if cls._is_invalid_version_string(api_version_from_server):
# For unknown reasons, Office 365 may respond with an API version strings that is invalid in a request.
# Detect these, so we can fall back to a valid version string.
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
requested_api_version,
)
api_version_from_server = requested_api_version
else:
# Trust API version from server response
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
api_version_from_server,
)
return cls(build=build, api_version=api_version_from_server)

def copy(self):
return self.__class__(build=self.build, api_version=self.api_version)

@classmethod
def all_versions(cls):
# Return all supported versions, sorted newest to oldest
return [cls(build=build, api_version=api_version) for build, api_version, _ in VERSIONS]

def __hash__(self):
return hash((self.build, self.api_version))

def __eq__(self, other):
if self.api_version != other.api_version:
return False
if self.build and not other.build:
return False
if other.build and not self.build:
return False
return self.build == other.build

def __repr__(self):
return self.__class__.__name__ + repr((self.build, self.api_version))

def __str__(self):
return f"Build={self.build}, API={self.api_version}, Fullname={self.fullname}"
```

Holds information about the server version.

### Static methods

```
def all_versions()
```

```
def guess(protocol, api_version_hint=None)
```

Ask the server which version it has. We haven't set up an Account object yet, so we generate requests by hand. We only need a response header containing a ServerVersionInfo element.

To get API version and build numbers from the server, we need to send a valid SOAP request. We can't do that without a valid API version. To solve this chicken-and-egg problem, we try all possible API versions that this package supports, until we get a valid response.

:param protocol: :param api_version_hint: (Default value = None)

### Instance variables

`var api_version`

Expand source code
```
class Version:
"""Holds information about the server version."""

__slots__ = "build", "api_version"

def __init__(self, build, api_version=None):
if api_version is None:
if not isinstance(build, Build):
raise InvalidTypeError("build", build, Build)
self.api_version = build.api_version()
else:
if not isinstance(build, (Build, type(None))):
raise InvalidTypeError("build", build, Build)
if not isinstance(api_version, str):
raise InvalidTypeError("api_version", api_version, str)
self.api_version = api_version
self.build = build

@property
def fullname(self):
for build, api_version, full_name in VERSIONS:
if self.build and (
self.build.major_version != build.major_version or self.build.minor_version != build.minor_version
):
continue
if self.api_version == api_version:
return full_name
log.warning("Full name for API version %s build %s is unknown", self.api_version, self.build)
return "UNKNOWN"

@classmethod
def guess(cls, protocol, api_version_hint=None):
"""Ask the server which version it has. We haven't set up an Account object yet, so we generate requests
by hand. We only need a response header containing a ServerVersionInfo element.

To get API version and build numbers from the server, we need to send a valid SOAP request. We can't do that
without a valid API version. To solve this chicken-and-egg problem, we try all possible API versions that this
package supports, until we get a valid response.

:param protocol:
:param api_version_hint: (Default value = None)
"""
from .properties import ENTRY_ID, EWS_ID, AlternateId
from .services import ConvertId

# The protocol doesn't have a version yet, so default to the latest supported version if we don't have a hint.
api_version = api_version_hint or ConvertId.supported_api_versions()[0]
log.debug("Asking server for version info using API version %s", api_version)
# We don't know the build version yet. Hopefully, the server will report it in the SOAP header. Lots of
# places expect a version to have a build, so this is a bit dangerous, but passing a fake build around is also
# dangerous.
protocol.config.version = Version(build=None, api_version=api_version)
# Use ConvertId as a minimal request to the server to test if the version is correct. If not, ConvertId will
# try to guess the version automatically. Make sure the call to ConvertId does not require a version build.
try:
list(ConvertId(protocol=protocol).call([AlternateId(id="DUMMY", format=EWS_ID, mailbox="DUMMY")], ENTRY_ID))
except ResponseMessageError as e:
# We may have survived long enough to get a new version
if not protocol.config.version.build:
raise TransportError(f"No valid version headers found in response ({e!r})")
if not protocol.config.version.build:
raise TransportError("No valid version headers found in response")
return protocol.config.version

@staticmethod
def _is_invalid_version_string(version):
# Check if a version string is bogus, e.g. V2_, V2015_ or V2018_
return re.match(r"V[0-9]{1,4}_.*", version)

@classmethod
def from_soap_header(cls, requested_api_version, header):
info = header.find(f"{{{TNS}}}ServerVersionInfo")
if info is None:
info = header.find(f"{{{ANS}}}ServerVersionInfo")
if info is None:
raise TransportError(f"No ServerVersionInfo in header: {xml_to_str(header)!r}")
try:
build = Build.from_xml(elem=info)
except ValueError:
raise TransportError(f"Bad ServerVersionInfo in response: {xml_to_str(header)!r}")
# Not all Exchange servers send the Version element
api_version_from_server = info.get("Version") or get_xml_attr(info, f"{{{ANS}}}Version") or build.api_version()
if api_version_from_server != requested_api_version:
if cls._is_invalid_version_string(api_version_from_server):
# For unknown reasons, Office 365 may respond with an API version strings that is invalid in a request.
# Detect these, so we can fall back to a valid version string.
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
requested_api_version,
)
api_version_from_server = requested_api_version
else:
# Trust API version from server response
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
api_version_from_server,
)
return cls(build=build, api_version=api_version_from_server)

def copy(self):
return self.__class__(build=self.build, api_version=self.api_version)

@classmethod
def all_versions(cls):
# Return all supported versions, sorted newest to oldest
return [cls(build=build, api_version=api_version) for build, api_version, _ in VERSIONS]

def __hash__(self):
return hash((self.build, self.api_version))

def __eq__(self, other):
if self.api_version != other.api_version:
return False
if self.build and not other.build:
return False
if other.build and not self.build:
return False
return self.build == other.build

def __repr__(self):
return self.__class__.__name__ + repr((self.build, self.api_version))

def __str__(self):
return f"Build={self.build}, API={self.api_version}, Fullname={self.fullname}"
```

`var build`

Expand source code
```
class Version:
"""Holds information about the server version."""

__slots__ = "build", "api_version"

def __init__(self, build, api_version=None):
if api_version is None:
if not isinstance(build, Build):
raise InvalidTypeError("build", build, Build)
self.api_version = build.api_version()
else:
if not isinstance(build, (Build, type(None))):
raise InvalidTypeError("build", build, Build)
if not isinstance(api_version, str):
raise InvalidTypeError("api_version", api_version, str)
self.api_version = api_version
self.build = build

@property
def fullname(self):
for build, api_version, full_name in VERSIONS:
if self.build and (
self.build.major_version != build.major_version or self.build.minor_version != build.minor_version
):
continue
if self.api_version == api_version:
return full_name
log.warning("Full name for API version %s build %s is unknown", self.api_version, self.build)
return "UNKNOWN"

@classmethod
def guess(cls, protocol, api_version_hint=None):
"""Ask the server which version it has. We haven't set up an Account object yet, so we generate requests
by hand. We only need a response header containing a ServerVersionInfo element.

To get API version and build numbers from the server, we need to send a valid SOAP request. We can't do that
without a valid API version. To solve this chicken-and-egg problem, we try all possible API versions that this
package supports, until we get a valid response.

:param protocol:
:param api_version_hint: (Default value = None)
"""
from .properties import ENTRY_ID, EWS_ID, AlternateId
from .services import ConvertId

# The protocol doesn't have a version yet, so default to the latest supported version if we don't have a hint.
api_version = api_version_hint or ConvertId.supported_api_versions()[0]
log.debug("Asking server for version info using API version %s", api_version)
# We don't know the build version yet. Hopefully, the server will report it in the SOAP header. Lots of
# places expect a version to have a build, so this is a bit dangerous, but passing a fake build around is also
# dangerous.
protocol.config.version = Version(build=None, api_version=api_version)
# Use ConvertId as a minimal request to the server to test if the version is correct. If not, ConvertId will
# try to guess the version automatically. Make sure the call to ConvertId does not require a version build.
try:
list(ConvertId(protocol=protocol).call([AlternateId(id="DUMMY", format=EWS_ID, mailbox="DUMMY")], ENTRY_ID))
except ResponseMessageError as e:
# We may have survived long enough to get a new version
if not protocol.config.version.build:
raise TransportError(f"No valid version headers found in response ({e!r})")
if not protocol.config.version.build:
raise TransportError("No valid version headers found in response")
return protocol.config.version

@staticmethod
def _is_invalid_version_string(version):
# Check if a version string is bogus, e.g. V2_, V2015_ or V2018_
return re.match(r"V[0-9]{1,4}_.*", version)

@classmethod
def from_soap_header(cls, requested_api_version, header):
info = header.find(f"{{{TNS}}}ServerVersionInfo")
if info is None:
info = header.find(f"{{{ANS}}}ServerVersionInfo")
if info is None:
raise TransportError(f"No ServerVersionInfo in header: {xml_to_str(header)!r}")
try:
build = Build.from_xml(elem=info)
except ValueError:
raise TransportError(f"Bad ServerVersionInfo in response: {xml_to_str(header)!r}")
# Not all Exchange servers send the Version element
api_version_from_server = info.get("Version") or get_xml_attr(info, f"{{{ANS}}}Version") or build.api_version()
if api_version_from_server != requested_api_version:
if cls._is_invalid_version_string(api_version_from_server):
# For unknown reasons, Office 365 may respond with an API version strings that is invalid in a request.
# Detect these, so we can fall back to a valid version string.
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
requested_api_version,
)
api_version_from_server = requested_api_version
else:
# Trust API version from server response
log.debug(
'API version "%s" worked but server reports version "%s". Using "%s"',
requested_api_version,
api_version_from_server,
api_version_from_server,
)
return cls(build=build, api_version=api_version_from_server)

def copy(self):
return self.__class__(build=self.build, api_version=self.api_version)

@classmethod
def all_versions(cls):
# Return all supported versions, sorted newest to oldest
return [cls(build=build, api_version=api_version) for build, api_version, _ in VERSIONS]

def __hash__(self):
return hash((self.build, self.api_version))

def __eq__(self, other):
if self.api_version != other.api_version:
return False
if self.build and not other.build:
return False
if other.build and not self.build:
return False
return self.build == other.build

def __repr__(self):
return self.__class__.__name__ + repr((self.build, self.api_version))

def __str__(self):
return f"Build={self.build}, API={self.api_version}, Fullname={self.fullname}"
```

`prop fullname`

Expand source code
```
@property
def fullname(self):
for build, api_version, full_name in VERSIONS:
if self.build and (
self.build.major_version != build.major_version or self.build.minor_version != build.minor_version
):
continue
if self.api_version == api_version:
return full_name
log.warning("Full name for API version %s build %s is unknown", self.api_version, self.build)
return "UNKNOWN"
```

### Methods

```
def copy(self)
```

Expand source code
```
def copy(self):
return self.__class__(build=self.build, api_version=self.api_version)
```