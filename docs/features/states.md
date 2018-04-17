# The State System

## Overview

In Alliance Auth v1 admins were able to define which Corporations and Alliances were to be considered "members" with full permissions and "blues" with restricted permissions. The state system is the replacement for these static definitions: admins can now create as many states as desired, as well as extend membership to specific characters.

## Creating a State
States are created through your installation's admin site. Upon install three states are created for you: `Member`, `Blue`, and `Guest`. New ones can be created like any other Django model by users with the appropriate permission (`authentication | state | Can add state`) or superusers.

A number of fields are available and are described below.

### Name
This is the displayed name of a state. Should be self-explanatory.

### Permissions
This lets you select permissions to grant to the entire state, much like a group. Any user with this state will be granted these permissions.

A common use case would be granting service access to a state.

### Priority
This value determines the order in which states are applied to users. Higher numbers come first. So if a random user `Bob` could member of both the `Member` and `Blue` states, because `Member` has a higher priority `Bob` will be assigned to it.

### Public
Checking this box means this state is available to all users. There isn't much use for this outside the `Guest` state.

### Member Characters
This lets you select which characters the state is available to. Characters can be added by selecting the green plus icon.

### Member Corporations
This lets you select which Corporations the state is available to. Corporations can be added by selecting the green plus icon.

### Member Alliances
This lets you select which Alliances the state is available to. Alliances can be added by selecting the green plus icon.

## Determining a User's State
States are mutually exclusive, meaning a user can only be in one at a time.

Membership is determined based on a user's main character. States are tested in order of descending priority - the first one which allows membership to the main character is assigned to the user.

States are automatically assigned when a user registers to the site, their main character changes, they are activated or deactivated, or states are edited. Note that editing states triggers lots of state checks so it can be a very slow process.

Assigned states are visible in the `Users` section of the `Authentication` admin site.

## The Guest State
If no states are available to a user's main character, or their account has been deactivated, they are assigned to a catch-all `Guest` state. This state cannot be deleted nor can its name be changed.

The `Guest` state allows permissions to be granted to users who would otherwise not get any. For example access to public services can be granted by giving the `Guest` state a service access permission.
