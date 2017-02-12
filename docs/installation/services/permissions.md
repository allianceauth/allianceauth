# Service Permissions
```eval_rst
.. note::
    New in 1.15
```

In the past, access to services was dictated by a list of settings in `settings.py`, granting access to each particular service for Members and/or Blues. This meant that granting access to a service was very broad and rigidly structured around these two states.

## Permissions based access

Instead of granting access to services by the previous rigid structure, access to services is now granted by the built in Django permissions system. This means that service access can be more granular, allowing only certain groups, for instance Corp CEOs, or even individual user access to each enabled service.

```eval_rst
.. important::
    If you grant access to an individual user, they will have access to that service regardless of whether or not they are a member.
```

Each service has an access permission defined, named like `Can access the <service name> service`.

To mimick the old behaviour of enabling services for all members, you would select the `Member` group from the admin panel, add the required service permission to the group and save. Likewise for Blues, select the `Blue` group and add the required permission.

A user can be granted the same permission from multiple sources. e.g. they may have it granted by several groups and directly granted on their account as well. Auth will not remove their account until all instances of the permission for that service have been revoked.

## Removing access

```eval_rst
.. danger::
    Access removal is processed immediately after removing a permission from a user or group. If you remove access from a large group, such as Member, it will immediately remove all users from that service.
```

When you remove a service permission from a user, a signal is triggered which will activate an immediate permission check. For users this will trigger an access check for all services. For groups, due to the potential extra load,  only the services whose permissions have changed will be verified, and only the users in that group.

If a user no longer has permission to access the service when this permissions check is triggered, that service will be immediately disabled for them.

### Disabling user accounts

When you unset a user as active in the admin panel, all of that users service accounts will be immediately disabled or removed. This is due to the built in behaviour of Djangos permissions system, which will return False for all permissions if a users account is disabled, regardless of their actual permissions state.
