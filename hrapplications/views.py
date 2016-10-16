from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from notifications import notify
from hrapplications.models import ApplicationForm
from hrapplications.models import Application
from hrapplications.models import ApplicationResponse
from hrapplications.models import ApplicationComment
from hrapplications.forms import HRApplicationCommentForm
from hrapplications.forms import HRApplicationSearchForm
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo

import logging

logger = logging.getLogger(__name__)


def create_application_test(user):
    auth, c = AuthServicesInfo.objects.get_or_create(user=user)
    if auth.main_char_id:
        return True
    else:
        return False


@login_required
def hr_application_management_view(request):
    logger.debug("hr_application_management_view called by user %s" % request.user)
    corp_applications = []
    finished_corp_applications = []
    auth_info, c = AuthServicesInfo.objects.get_or_create(user=request.user)
    main_char = None
    if auth_info.main_char_id:
        try:
            main_char = EveCharacter.objects.get(character_id=auth_info.main_char_id)
        except EveCharacter.DoesNotExist:
            pass
    if request.user.is_superuser:
        corp_applications = Application.objects.filter(approved=None)
        finished_corp_applications = Application.objects.exclude(approved=None)
    elif request.user.has_perm('auth.human_resources') and main_char:
        if ApplicationForm.objects.filter(corp__corporation_id=main_char.corporation_id).exists():
            app_form = ApplicationForm.objects.get(corp__corporation_id=main_char.corporation_id)
            corp_applications = Application.objects.filter(form=app_form).filter(approved=None)
            finished_corp_applications = Application.objects.filter(form=app_form).filter(approved__in=[True, False])
    logger.debug("Retrieved %s personal, %s corp applications for %s" % (
        len(request.user.applications.all()), len(corp_applications), request.user))
    context = {
        'personal_apps': request.user.applications.all(),
        'applications': corp_applications,
        'finished_applications': finished_corp_applications,
        'search_form': HRApplicationSearchForm(),
        'create': create_application_test(request.user)
    }
    return render(request, 'registered/hrapplicationmanagement.html', context=context)


@login_required
@user_passes_test(create_application_test)
def hr_application_create_view(request, form_id=None):
    if form_id:
        app_form = get_object_or_404(ApplicationForm, id=form_id)
        if request.method == "POST":
            if Application.objects.filter(user=request.user).filter(form=app_form).exists():
                logger.warn("User %s attempting to duplicate application to %s" % (request.user, app_form.corp))
            else:
                application = Application(user=request.user, form=app_form)
                application.save()
                for question in app_form.questions.all():
                    response = ApplicationResponse(question=question, application=application)
                    response.answer = request.POST.get(str(question.pk),
                                                       "Failed to retrieve answer provided by applicant.")
                    response.save()
                logger.info("%s created %s" % (request.user, application))
            return redirect('auth_hrapplications_view')
        else:
            questions = app_form.questions.all()
            return render(request, 'registered/hrapplicationcreate.html',
                          context={'questions': questions, 'corp': app_form.corp})
    else:
        choices = []
        for app_form in ApplicationForm.objects.all():
            if not Application.objects.filter(user=request.user).filter(form=app_form).exists():
                choices.append((app_form.id, app_form.corp.corporation_name))
        return render(request, 'registered/hrapplicationcorpchoice.html', context={'choices': choices})


@login_required
def hr_application_personal_view(request, app_id):
    logger.debug("hr_application_personal_view called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if app.user == request.user:
        context = {
            'app': app,
            'responses': ApplicationResponse.objects.filter(application=app),
            'buttons': False,
            'comments': ApplicationComment.objects.filter(application=app),
            'comment_form': HRApplicationCommentForm(),
            'apis': [],
        }
        return render(request, 'registered/hrapplicationview.html', context=context)
    else:
        logger.warn("User %s not authorized to view %s" % (request.user, app))
        return redirect('auth_hrapplications_view')


@login_required
def hr_application_personal_removal(request, app_id):
    logger.debug("hr_application_personal_removal called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if app.user == request.user:
        if app.approved is None:
            logger.info("User %s deleting %s" % (request.user, app))
            app.delete()
        else:
            logger.warn("User %s attempting to delete reviewed app %s" % (request.user, app))
    else:
        logger.warn("User %s not authorized to delete %s" % (request.user, app))
    return redirect('auth_hrapplications_view')


@login_required
@permission_required('auth.human_resources')
def hr_application_view(request, app_id):
    logger.debug("hr_application_view called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if request.method == 'POST':
        if request.user.has_perm('hrapplications.add_applicationcomment'):
            form = HRApplicationCommentForm(request.POST)
            logger.debug("Request type POST contains form valid: %s" % form.is_valid())
            if form.is_valid():
                comment = ApplicationComment()
                comment.application = app
                comment.user = request.user
                comment.text = form.cleaned_data['comment']
                comment.save()
                logger.info("Saved comment by user %s to %s" % (request.user, app))
        else:
            logger.warn("User %s does not have permission to add ApplicationComments" % request.user)
    else:
        logger.debug("Returning blank HRApplication comment form.")
        form = HRApplicationCommentForm()
    apis = []
    if request.user.has_perm('hrapplications.view_apis'):
        apis = app.apis
    context = {
        'app': app,
        'responses': ApplicationResponse.objects.filter(application=app),
        'buttons': True,
        'apis': apis,
        'comments': ApplicationComment.objects.filter(application=app),
        'comment_form': form,
    }
    return render(request, 'registered/hrapplicationview.html', context=context)


@login_required
@permission_required('auth.human_resources')
@permission_required('hrapplications.delete_application')
def hr_application_remove(request, app_id):
    logger.debug("hr_application_remove called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    logger.info("User %s deleting %s" % (request.user, app))
    app.delete()
    notify(app.user, "Application Deleted", message="Your application to %s was deleted." % app.form.corp)
    return redirect('auth_hrapplications_view')


@login_required
@permission_required('auth.human_resources')
@permission_required('hrapplications.approve_application')
def hr_application_approve(request, app_id):
    logger.debug("hr_application_approve called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if request.user.is_superuser or request.user == app.reviewer:
        logger.info("User %s approving %s" % (request.user, app))
        app.approved = True
        app.save()
        notify(app.user, "Application Accepted", message="Your application to %s has been approved." % app.form.corp,
               level="success")
    else:
        logger.warn("User %s not authorized to approve %s" % (request.user, app))
    return redirect('auth_hrapplications_view')


@login_required
@permission_required('auth.human_resources')
@permission_required('hrapplications.reject_application')
def hr_application_reject(request, app_id):
    logger.debug("hr_application_reject called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if request.user.is_superuser or request.user == app.reviewer:
        logger.info("User %s rejecting %s" % (request.user, app))
        app.approved = False
        app.save()
        notify(app.user, "Application Rejected", message="Your application to %s has been rejected." % app.form.corp,
               level="danger")
    else:
        logger.warn("User %s not authorized to reject %s" % (request.user, app))
    return redirect('auth_hrapplications_view')


@login_required
@permission_required('auth.human_resources')
def hr_application_search(request):
    logger.debug("hr_application_search called by user %s" % request.user)
    if request.method == 'POST':
        form = HRApplicationSearchForm(request.POST)
        logger.debug("Request type POST contains form valid: %s" % form.is_valid())
        if form.is_valid():
            searchstring = form.cleaned_data['search_string'].lower()
            applications = set([])
            logger.debug("Searching for application with character name %s for user %s" % (searchstring, request.user))
            app_list = []
            if request.user.is_superuser:
                app_list = Application.objects.all()
            else:
                auth_info = AuthServicesInfo.objects.get(user=request.user)
                try:
                    character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
                    app_list = Application.objects.filter(form__corp__corporation_id=character.corporation_id)
                except EveCharacter.DoesNotExist:
                    logger.warn(
                        "User %s missing main character model: unable to filter applications to search" % request.user)
            for application in app_list:
                if application.main_character:
                    if searchstring in application.main_character.character_name.lower():
                        applications.add(application)
                    if searchstring in application.main_character.corporation_name.lower():
                        applications.add(application)
                    if searchstring in application.main_character.alliance_name.lower():
                        applications.add(application)
                for character in application.characters:
                    if searchstring in character.character_name.lower():
                        applications.add(application)
                    if searchstring in character.corporation_name.lower():
                        applications.add(application)
                    if searchstring in character.alliance_name.lower():
                        applications.add(application)
                if searchstring in application.user.username.lower():
                    applications.add(application)
            logger.info("Found %s Applications for user %s matching search string %s" % (
                len(applications), request.user, searchstring))

            context = {'applications': applications, 'search_form': HRApplicationSearchForm()}

            return render(request, 'registered/hrapplicationsearchview.html', context=context)
        else:
            logger.debug("Form invalid - returning for user %s to retry." % request.user)
            context = {'applications': None, 'search_form': form}
            return render(request, 'registered/hrapplicationsearchview.html', context=context)

    else:
        logger.debug("Returning empty search form for user %s" % request.user)
        return redirect("auth_hrapplications_view")


@login_required
@permission_required('auth.human_resources')
def hr_application_mark_in_progress(request, app_id):
    logger.debug("hr_application_mark_in_progress called by user %s for app id %s" % (request.user, app_id))
    app = get_object_or_404(Application, pk=app_id)
    if not app.reviewer:
        logger.info("User %s marking %s in progress" % (request.user, app))
        auth_info = AuthServicesInfo.objects.get(user=request.user)
        try:
            character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
        except EveCharacter.DoesNotExist:
            logger.warn("User %s marking %s in review has no main character" % (request.user, app))
            character = None
        app.reviewer = request.user
        app.reviewer_character = character
        app.save()
        notify(app.user, "Application In Progress",
               message="Your application to %s is being reviewed by %s" % (app.form.corp, app.reviewer_str))
    else:
        logger.warn(
            "User %s unable to mark %s in progress: already being reviewed by %s" % (request.user, app, app.reviewer))
    return redirect("auth_hrapplication_view", app_id)
