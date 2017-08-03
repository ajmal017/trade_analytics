from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from . import models as md
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import pdb

def HomePage(request):
    context = RequestContext(request)
    SavedQueriesView=md.SavedQueryView()
    return render(request, 'homepage/homepage.html',{'SavedQueriesView':SavedQueriesView},context)

def Boot(request):
    context = RequestContext(request)
    return render(request, 'homepage/base2.html',{},context)


@csrf_exempt
def HomePage2(request):
    context = RequestContext(request)
    if request.method == 'GET':
        SQVIEW=pd.DataFrame()
        for key in request.GET:
            # SQVIEW=[{'pk':2,'pageno':10},{'pk':3,'pageno':22}]
            
            if 'SQpk' in key:
                # value=request.GET.get(key,'')
                cnt=int(key.split('_')[1])
                pk=int(request.GET.get('SQpk_'+str(cnt),0))
                name=request.GET.get('SQname_'+str(cnt),'')
                pageno=request.GET.get('pageno_'+str(cnt),None)
                if pageno is not None:
                    pageno=int(pageno)
                dd=pd.DataFrame({'pk':pk,'name':name,'pageno':pageno},index=[cnt])
                SQVIEW=pd.concat([SQVIEW,dd])
        # pdb.set_trace()
        
        SQVIEW.sort_index(inplace=True)
        SQVIEW=SQVIEW.to_dict(orient='records')
        SQVIEW=md.SQVIEW(SQVIEW=SQVIEW)
    else:
        SQVIEW=md.SQVIEW(SQVIEW=[])
    return render(request, 'homepage/homepage2.html',{'SQVIEW':SQVIEW},context)


def Welcome(request):
    context = RequestContext(request)
    return render(request, 'homepage/welcome.html',{},context)








def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = md.UserForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() :
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()



            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors
    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = md.UserForm()

    # Render the template depending on the context.
    return render(request,'homepage/register.html',{'user_form': user_form,  'registered': registered},
            context)


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    print request.POST
    print request.GET
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                nextt=request.GET.get('next')
                if nextt=='' or nextt==None or nextt==False:
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect(nextt)
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username,password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        user_form = md.UserLoginForm()
        context['next']=request.GET.get('next')
	return render(request, 'homepage/login.html',{'user_form':user_form},context)
        #return render_to_response('homepage/login.html', {'user_form':user_form}, context)


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')
