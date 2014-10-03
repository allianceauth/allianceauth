from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from forms import LoginForm

# Create your views here.
def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/")
    else:
        form = LoginForm()

    return render_to_response('public/login.html',{'form':form}, context_instance=RequestContext(request))


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")