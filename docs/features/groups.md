# Groups
Group Management is one of the core tasks of Alliance Auth. Many of Alliance Auth's services allow for synchronising of group membership, allowing you to grant permissions or roles in services to access certain aspects of them.

## Automatic Groups
When a member registers in Alliance Auth and selects a main character, Auth will assign them some groups automatically based on some factors.

```eval_rst
.. important::
    The ``Corp_`` and ``Alliance_`` group name prefixes are reserved for Alliance Auth internal group management. If you prefix a group with these you will find Alliance Auth automatically removes users from the group.
```

```eval_rst
+------------------------------+-----------------------------------------------------------------------------------+
| Group                        | Condition                                                                         |
+------------------------------+-----------------------------------------------------------------------------------+
| ``Corp_<corp_name>``         | Users Main Character belongs to the Corporation                                   |
+------------------------------+-----------------------------------------------------------------------------------+
| ``Alliance_<alliance_name>`` | Users Main Character belongs to the Alliance                                      |
+------------------------------+-----------------------------------------------------------------------------------+
| ``Member``                   | User is a member of one of the tenant Corps or Alliances                          |
+------------------------------+-----------------------------------------------------------------------------------+
| ``Blue``                     | User is a member of a blue Corp or Alliance, be it via standings or static config |
+------------------------------+-----------------------------------------------------------------------------------+
```

When the user no longer has the condition required to be a member of that group they are automatically removed by Auth.

## User Organised Groups

Along with the automated groups, administrators can create custom groups for users to join. Examples might be groups like `Leadership`, `CEO` or `Scouts`.

When you create a Django `Group`, Auth automatically creates a corresponding `AuthGroup` model. The admin page looks like this:

![AuthGroup Admin page](/_static/images/features/group-admin.png)

Here you have several options:

#### Internal
Users cannot see, join or request to join this group. This is primarily used for Auth's internally managed groups, though can be useful if you want to prevent users from managing their membership of this group themselves. This option will override the Hidden, Open and Public options when enabled.

By default, every new group created will be an internal group.

#### Hidden
Group is hidden from the user interface, but users can still join if you give them the appropriate join link. The URL will be along the lines of `https://example.com/en/group/request_add/{group_id}`. You can get the Group ID from the admin page URL.

This option still respects the Open option.


### Open
When a group is toggled open, users who request to join the group will be immediately added to the group. 

If the group is not open, their request will have to be approved manually by someone with the group management role, or a group leader of that group.


### Public
Group is accessible to any registered user, even when they do not have permission to join regular groups.

The key difference is that the group is completely unmanaged by Auth. **Once a member joins they will not be removed unless they leave manually, you remove them manually, or their account is deliberately set inactive or deleted.**

Most people won't have a use for public groups, though it can be useful if you wish to allow public access to some services. You can grant service permissions on a public group to allow this behaviour.


## Permission
In order to join a group other than a public group, the permission `groupmanagement.request_groups` (`Can request non-public groups` in the admin panel) must be active on their account, either via a group or directly applied to their User account.

When a user loses this permission, they will be removed from all groups _except_ Public groups.

```eval_rst
.. note::
    By default, the ``groupmanagement.request_groups`` permission is applied to the ``Member`` group. In most instances this, and perhaps adding it to the ``Blue`` group, should be all that is ever needed. It is unsupported and NOT advisable to apply this permission to a public group. See #697 for more information.
```

# Group Management

In order to access group management, users need to be either a superuser, granted the `auth | user | group_management ( Access to add members to groups within the alliance )` permission or a group leader (discussed later).

## Group Requests

When a user joins or leaves a group which is not marked as "Open", their group request will have to be approved manually by a user with the `group_management` permission or by a group leader of the group they are requesting.

## Group Membership

The group membership tab gives an overview of all of the non-internal groups.

![Group overview](/_static/images/features/group-membership.png)

### Group Member Management

Clicking on the blue eye will take you to the group member management screen. Here you can see a list of people who are in the group, and remove members where necessary.

![Group overview](/_static/images/features/group-member-management.png)


## Group Leaders

Group leaders have the same abilities as users with the `group_management` permission, _however_, they will only be able to:

- Approve requests for groups they are a leader of.
- View the Group Membership and Group Members of groups they are leaders of.

This allows you to more finely control who has access to manage which groups. Currently it is not possible to add a Group as group leaders.
