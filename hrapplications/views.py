from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect

from models import HRApplication
from models import HRApplicationComment
from forms import HRApplicationForm
from forms import HRApplicationCommentForm
from forms import HRApplicationSearchForm
from eveonline.models import EveCorporationInfo
from eveonline.models import EveCharacter
from authentication.models import AuthServicesInfo

from django.conf import settings
from eveonline.managers import EveManager

import logging

logger = logging.getLogger(__name__)

@login_required
def hr_application_management_view(request):
	logger.debug("hr_application_management_view called by user %s" % request.user)
	personal_app = None
	corp_applications = None

	if request.user.is_superuser:
		logger.debug("User %s is superuser: returning all applications." % request.user)
		corp_applications = HRApplication.objects.all()
	else:
		# Get the corp the member is in
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		if auth_info.main_char_id != "":
			try:
				main_corp_id = EveManager.get_charater_corporation_id_by_id(auth_info.main_char_id)
        	                main_alliance_id = EveManager.get_charater_alliance_id_by_id(auth_info.main_char_id)
				if (settings.IS_CORP and main_corp_id == settings.CORP_ID) or (not settings.IS_CORP and main_alliance_id == settings.ALLIANCE_ID):
					main_char = EveCharacter.objects.get(character_id=auth_info.main_char_id)
					if EveCorporationInfo.objects.filter(corporation_id=main_char.corporation_id).exists():
	                                    corp = EveCorporationInfo.objects.get(corporation_id=main_char.corporation_id)
        	                            corp_applications = HRApplication.objects.filter(corp=corp).filter(approved_denied=None)
                	                else:
                        	            corp_applications = None
				else:
					corp_applications = None
			except:
				logger.error("Unable to determine user %s main character id %s corp. Returning no corp hrapplications." % (request.user, auth_info.main_char_id))
				corp_applications = None
	context = {'personal_apps': HRApplication.objects.all().filter(user=request.user),
			   'applications': corp_applications,
			   'search_form': HRApplicationSearchForm()}

	return render_to_response('registered/hrapplicationmanagement.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_create_view(request):
	logger.debug("hr_application_create_view called by user %s" % request.user)
	success = False

	if request.method == 'POST':
		form = HRApplicationForm(request.POST)
		logger.debug("Request type POST with form valid: %s" % form.is_valid())
		if form.is_valid():
			application = HRApplication()
			application.user = request.user
			application.character_name = form.cleaned_data['character_name']
			application.full_api_id = form.cleaned_data['full_api_id']
			application.full_api_key = form.cleaned_data['full_api_key']
			application.corp = EveCorporationInfo.objects.get(corporation_id=form.cleaned_data['corp'])
			application.is_a_spi = form.cleaned_data['is_a_spi']
			application.about = form.cleaned_data['about']
			application.extra = form.cleaned_data['extra']
			application.save()
			success = True
			logger.info("Created HRApplication for user %s to corp %s" % (request.user, application.corp))
	else:
		logger.debug("Providing empty form.")
		form = HRApplicationForm()

	context = {'form': form, 'success': success}
	return render_to_response('registered/hrcreateapplication.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_view(request, app_id):
	logger.debug("hr_application_personal_view called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		logger.debug("Got application id %s: %s" % (app_id, application))
		if application.user != request.user:
			logger.warn("HRApplication id %s user %s does not match request user %s - returning blank application." % (app_id, application.user, request.user))
			application = HRApplication()
	else:
		logger.warn("Unable to locate HRApplication matching id %s - returning blank application to user %s" % (app_id, request.user))
		application = HRApplication()
	context = {'application': application}

	return render_to_response('registered/hrapplicationview.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_removal(request, app_id):
	logger.debug("hr_application_personal_removal called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		if application.user == request.user:
			application.delete()
			logger.info("Deleted HRApplication with id %s for user %s to corp %s" % (app_id, request.user, application.corp))
		else:
			logger.warn("HRapplication id %s user %s does not match request user %s - refusing to delete." % (app_id, application.user, request.user))
	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_view(request, app_id):
	logger.debug("hr_application_view called by user %s for app id %s" % (request.user, app_id))
	if request.method == 'POST':
		form = HRApplicationCommentForm(request.POST)
		logger.debug("Request type POST contains form valid: %s" % form.is_valid())
		if form.is_valid():
			auth_info = AuthServicesInfo.objects.get(user=request.user)

			comment = HRApplicationComment()
			comment.application = HRApplication.objects.get(id=int(form.cleaned_data['app_id']))
			comment.commenter_user = request.user
			comment.commenter_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
			comment.comment = form.cleaned_data['comment']
			comment.save()
			logger.info("Saved comment by user %s to hrapplication %s" % (request.user, comment.hrapplication))

	else:
		logger.debug("Returning blank HRApplication comment form.")
		form = HRApplicationCommentForm()

	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		comments = HRApplicationComment.objects.all().filter(application=application)
		logger.debug("Retrieved hrpplication id %s for user %s with comments %s" % (app_id, request.user, commends))
	else:
		application = HRApplication()
		comments = []
		logger.error("HRAppllication with id %s not found - returning blank applicatin to user %s" % request.user)

	context = {'application': application, 'comments': comments, 'comment_form': form}

	return render_to_response('registered/hrapplicationview.html',
							  context, context_instance=RequestContext(request))


@login_required
@permission_required('auth.human_resources')
def hr_application_remove(request, app_id):
	logger.debug("hr_application_remove called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		if application:
			logger.info("Deleted HRApplication id %s on behalf of user %s" % (app_id, request.user))
			application.delete()
		else:
                    logger.error("Unable to delete HRApplication with id %s for user %s: application is NoneType" % (app_id, request.user))
	else:
		logger.error("Unable to delete HRApplication with id %s for user %s: application not found." % (app_id, request.user))

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_approve(request, app_id):
	logger.debug("hr_application_approve called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.approved_denied = True
		application.reviewer_user = request.user
		application.reviewer_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()
		logger.info("HRApplication for user %s to corp %s approved by %s" % (application.user, application.corp, request.user))
	else:
		logger.error("User %s unable to approve HRApplication id %s - hrapplication with that id not found." % (request.user, app_id))

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_reject(request, app_id):
	logger.debug("hr_application_reject called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.approved_denied = False
		application.reviewer_user = request.user
		application.reviewer_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()
		logger.info("HRApplication for user %s to corp %s rejected by %s" % (application.user, application.corp, request.user))
	else:
		logger.error("User %s unable to reject HRApplication id %s - hrapplication with that id not found." % (request.user, app_id))

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_search(request):
	logger.debug("hr_application_search called by user %s" % request.user)
	if request.method == 'POST':
		form = HRApplicationSearchForm(request.POST)
		logger.debug("Request type POST contains form valid: %s" % form.is_valid())
		if form.is_valid():
			# Really dumb search and only checks character name
			# This can be improved but it does the job for now
			searchstring = form.cleaned_data['search_string']
			applications = []
			logger.debug("Searching for application with character name %s for user %s" % (searchstring, request.user))

			for application in HRApplication.objects.all():
				if searchstring in application.character_name:
					applications.append(application)
			logger.info("Found %s HRApplications for user %s matching search string %s" % (len(applications), request.user, searchstring))

			context = {'applications': applications, 'search_form': HRApplicationSearchForm()}

			return render_to_response('registered/hrapplicationsearchview.html',
									  context, context_instance=RequestContext(request))
		else:
			context = {'applications': None, 'search_form': form}
			return render_to_response('registered/hrapplicationsearchview.html',
                                                                          context, context_instance=RequestContext(request))
	
	else:
		logger.debug("Returning empty search form for user %s" % request.user)
		return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_mark_in_progress(request, app_id):
	logger.debug("hr_application_mark_in_progress called by user %s for app id %s" % (request.user, app_id))
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.reviewer_inprogress_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()
		logger.info("Marked HRApplication for user %s to corp %s in progress by user %s" % (application.user, application.corp, request.user))
	else:
		logger.error("Unable to mark HRApplication id %s in progress by user %s - hrapplication matching id not found." % (app_id, request.user))

	return HttpResponseRedirect("/hr_application_view/" + str(app_id))
