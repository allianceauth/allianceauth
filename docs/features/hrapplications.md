# HR Applications

## Installation

Add `allianceauth.hrapplications` to your `INSTALLED_APPS` setting. In `myauth/settings/local.py`:

    INSTALLED_APPS += ['allianceauth.hrapplications']

Run migrations to complete installation.

## Management

### Creating Forms

The most common task is creating ApplicationForm models for corps. Only when such models exist will a corp be listed as a choice for applicants. This occurs in the django admin site, so only staff have access.

The first step is to create questions. This is achieved by creating ApplicationQuestion models, one for each question. Titles are not unique.

Next step is to create the actual ApplicationForm model. It requires an existing EveCorporationInfo model to which it will belong. It also requires the selection of questions. ApplicationForm models are unique per corp: only one may exist for any given corp concurrently.

You can adjust these questions at any time. This is the preferred method of modifying the form: deleting and recreating will cascade the deletion to all received applications from this form which is usually not intended.

Once completed the corp will be available to receive applications.

### Reviewing Applications

Superusers can see all applications, while normal members with the required permission can view only those to their corp.

Selecting an application from the management screen will provide all the answers to the questions in the form at the time the user applied.

When a reviewer assigns themselves an application, they mark it as in progress. This notifies the applicant and permanently attached the reviewer to the application.

Only the assigned reviewer can approve/reject/delete the application if they possess the appropriate permission.

Any reviewer who can see the application can view the applicant's APIs if they possess the appropriate permission.

## Permissions

The following permissions have an effect on the website above and beyond their usual admin site functions.

```eval_rst
+---------------------------------------+------------------+----------------------------------------------------+
| Permission                            | Admin Site       | Auth Site                                          |
+=======================================+==================+====================================================+
| auth.human_resources                  | None             | Can view applications and mark in progress         |
+---------------------------------------+------------------+----------------------------------------------------+
| hrapplications.approve_application    | None             | Can approve applications                           |
+---------------------------------------+------------------+----------------------------------------------------+
| hrapplications.delete_application     | Can delete model | Can delete applications                            |
+---------------------------------------+------------------+----------------------------------------------------+
| hrapplications.reject_applications    | None             | Can reject applications                            |
+---------------------------------------+------------------+----------------------------------------------------+
| hrapplications.view_apis              | None             | Can view applicant API keys, and audit in Jacknife |
+---------------------------------------+------------------+----------------------------------------------------+
| hrapplications.add_applicationcomment | Can create model | Can comment on applications                        |
+---------------------------------------+------------------+----------------------------------------------------+

```

Best practice is to bundle the `auth.human_resources` permission alongside the `hrapplications.approve_application` and `hrapplications.reject_application` permissions, as in isolation these don't make much sense.

## Models

### ApplicationQuestion

This is the model representation of a question. It contains a title, and a field for optional "helper" text. It is referenced by ApplicationForm models but acts independently. Modifying the question after it has been created will not void responses, so it's not advisable to edit the title or the answers may not make sense to reviewers.

### ApplicationForm

This is the template for an application. It points at a corp, with only one form allowed per corp. It also points at ApplicationQuestion models. When a user creates an application, they will be prompted with each question the form includes at the given time. Modifying questions in a form after it has been created will not be reflected in existing applications, so it's perfectly fine to adjust them as you see fit. Changing corps however is not advisable, as existing applications will point at the wrong corp after they've been submitted, confusing reviewers.

### Application

This is the model representation of a completed application. It references an ApplicationForm from which it was spawned which is where the corp specificity comes from. It points at a user, contains info regarding its reviewer, and has a status. Shortcut properties also provide the applicant's main character, the applicant's APIs, and a string representation of the reviewer (for cases when the reviewer doesn't have a main character or the model gets deleted).

### ApplicationResponse

This is an answer to a question. It points at the Application to which it belongs, to the ApplicationQuestion which it is answering, and contains the answer text. Modifying any of these fields in dangerous.

### ApplicationComment

This is a reviewer's comment on an application. Points at the application, points to the user, and contains the comment text. Modifying any of these fields is dangerous.

## Troubleshooting

### No corps accepting applications

Ensure there are ApplicationForm models in the admin site. Ensure the user does not already have an application to these corps. If the users wishes to re-apply they must first delete their completed application

### Reviewer unable to complete application

Reviewers require a permission for each of the three possible outcomes of an application, Approve Reject or Delete. Any user with the human resources permission can mark an application as in-progress, but if they lack these permissions then the application will get stuck. Either grant the user the required permissions or change the assigned reviewer in the admin site. Best practice is to bundle the `auth.human_resources` permission alongside the `hrapplications.approve_application` and `hrapplications.reject_application` permissions, as in isolation these don't serve much purpose.
