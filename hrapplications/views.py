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


@login_required
def hr_application_management_view(request):
	personal_app = None
	corp_applications = None

	if request.user.is_superuser:
		corp_applications = HRApplication.objects.all()
	else:
		# Get the corp the member is in
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		if auth_info.main_char_id != "":
			main_alliance_id = EveManager.get_charater_alliance_id_by_id(auth_info.main_char_id)
			if main_alliance_id == settings.ALLIANCE_ID:
				main_char = EveCharacter.objects.get(character_id=auth_info.main_char_id)
				corp = EveCorporationInfo.objects.get(corporation_id=main_char.corporation_id)
				corp_applications = HRApplication.objects.filter(corp=corp).filter(approved_denied=None)
			else:
				corp_applications = None

	context = {'personal_apps': HRApplication.objects.all().filter(user=request.user),
			   'applications': corp_applications,
			   'search_form': HRApplicationSearchForm()}

	return render_to_response('registered/hrapplicationmanagement.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_create_view(request):
	success = False

	if request.method == 'POST':
		form = HRApplicationForm(request.POST)
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
	else:
		form = HRApplicationForm()

	context = {'form': form, 'success': success}
	return render_to_response('registered/hrcreateapplication.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_view(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		if application.user != request.user:
			application = HRApplication()
	else:
		application = HRApplication()
	context = {'application': application}

	return render_to_response('registered/hrapplicationview.html',
							  context, context_instance=RequestContext(request))


@login_required
def hr_application_personal_removal(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		if application.user == request.user:
			application.delete()

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_view(request, app_id):
	if request.method == 'POST':
		form = HRApplicationCommentForm(request.POST)
		if form.is_valid():
			auth_info = AuthServicesInfo.objects.get(user=request.user)

			comment = HRApplicationComment()
			comment.application = HRApplication.objects.get(id=int(form.cleaned_data['app_id']))
			comment.commenter_user = request.user
			comment.commenter_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
			comment.comment = form.cleaned_data['comment']
			comment.save()

	else:
		form = HRApplicationCommentForm()

	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		comments = HRApplicationComment.objects.all().filter(application=application)
	else:
		application = HRApplication()
		comments = []

	context = {'application': application, 'comments': comments, 'comment_form': form}

	return render_to_response('registered/hrapplicationview.html',
							  context, context_instance=RequestContext(request))


@login_required
@permission_required('auth.human_resources')
def hr_application_remove(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		application = HRApplication.objects.get(id=app_id)
		if application:
			application.delete()

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_approve(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.approved_denied = True
		application.reviewer_user = request.user
		application.reviewer_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_reject(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.approved_denied = False
		application.reviewer_user = request.user
		application.reviewer_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()

	return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_search(request):
	if request.method == 'POST':
		form = HRApplicationSearchForm(request.POST)
		if form.is_valid():
			# Really dumb search and only checks character name
			# This can be improved but it does the job for now
			searchstring = form.cleaned_data['search_string']
			applications = []

			for application in HRApplication.objects.all():
				if searchstring in application.character_name:
					applications.append(application)

			context = {'applications': applications, 'search_form': HRApplicationSearchForm()}

			return render_to_response('registered/hrapplicationsearchview.html',
									  context, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect("/hr_application_management/")


@login_required
@permission_required('auth.human_resources')
def hr_application_mark_in_progress(request, app_id):
	if HRApplication.objects.filter(id=app_id).exists():
		auth_info = AuthServicesInfo.objects.get(user=request.user)
		application = HRApplication.objects.get(id=app_id)
		application.reviewer_inprogress_character = EveCharacter.objects.get(character_id=auth_info.main_char_id)
		application.save()

	return HttpResponseRedirect("/hr_application_view/" + str(app_id))
