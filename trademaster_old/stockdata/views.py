from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from . import models as md
from django.contrib import messages
import os
import subprocess as sbp
from django.utils.safestring import mark_safe
from django.conf import settings

# from django.urls import reverse

@login_required(login_url='/login/')
def WatchListManager_create(request):
    print request.user

    context = RequestContext(request)
    if request.method == 'POST':
        if request.POST.get('watch_create', '')=="Create Watchlist":
            createwatchlistform=md.CreateWatchlistForm(request.POST)
            if createwatchlistform.is_valid():
                P,error=createwatchlistform.process_watchlist(username=request.user)
                if P==True:
                    context['error']="Watchlist successfully added"
                    createwatchlistform=md.CreateWatchlistForm()
                else:
                    context['error']=error
                    messages.error(request, error+reverse())
                    createwatchlistform=md.CreateWatchlistForm(request.POST)

            else:
                return HttpResponse("in valid form return ")

    else:
        createwatchlistform=md.CreateWatchlistForm()

    return render(request, 'stockdata/watchlistmanager_create.html', {'createwatchlistform':createwatchlistform},context)

@login_required(login_url='/login/')
def WatchListManager_amend(request):
    context = RequestContext(request)
    context['error']=None

    if request.method == 'POST':
        if request.POST.get('watch_submit', '')=="Select Watchlist":
            watchform = md.Watchlist_amend_form(request.POST,username=request.user)
            if watchform.is_valid():
                watchform = md.Watchlist_amend_form(username=request.user,watchlistname=watchform.cleaned_data['watchlist'],initial={'watchlist':watchform.cleaned_data['watchlist']})
            else:
                context['error']="invalid form return on watchlist select"
                watchform=md.Watchlist_amend_form(username=request.user)


        if request.POST.get('watch_save', '')=="Save Changes":
            print "------"*5
            print request.POST
            watchform = md.Watchlist_amend_form(request.POST,username=request.user)
            if watchform.is_valid():
                watchform = md.Watchlist_amend_form(request.POST,username=request.user,watchlistname=watchform.cleaned_data['watchlist'])
                watchform.is_valid()

                P,error=watchform.process_amend()
                if P==True:
                    context['error']="Changes to watchlist "+ watchform.cleaned_data['watchlist'] +" were successfully saved"
                    watchform=md.Watchlist_amend_form(username=request.user)
                else:
                    context['error']="error with saving "+ watchform.cleaned_data['watchlist'] +" : "+error
                    watchform=md.Watchlist_amend_form(username=request.user,watchlistname=watchform.cleaned_data['watchlist'],initial={'watchlist':watchform.cleaned_data['watchlist']})
            else:
                context['error']="invalid form return on saving changes"
                watchform=md.Watchlist_amend_form(username=request.user)
                

    else:
        watchform=md.Watchlist_amend_form(username=request.user)


    return render(request, 'stockdata/watchlistmanager_amend.html', {'watchform': watchform},context)


@login_required(login_url='/login/')
def ControlPanel(request):
    if str(request.user)!='nagavenkat':
            return HttpResponse('Only admin can access')


    if request.method == 'POST':

        if request.POST.get('load_stock_groups', '')=="Load StockGroups":
            print md.LoadStockGroups()
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})


        elif request.POST.get('watch_update_stock', '')=="Update Watchlists":
            print md.UpdateWatchlist_withStockData()
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})
        
        elif request.POST.get('Run_Seq_1', '')=="Run_Seq_1":
            import research.tasks as rmtks
            ff=os.path.join( settings.BASE_DIR,'celerylog' )
            if os.path.isfile(ff)==True:
                sbp.call(['rm',ff])


            rmtks.SequenceJobs_1.delay()
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})

        elif request.POST.get('Run_Seq_2', '')=="Run_Seq_2":
            import research.tasks as rmtks
            ff=os.path.join( settings.BASE_DIR,'celerylog' )
            if os.path.isfile(ff)==True:
                messages.info(request, 'celery log exists')
                sbp.call(['rm',ff])
                messages.info(request, 'Deleted celery log')

            messages.info(request, 'added SequenceJobs_2 delay')
            rmtks.SequenceJobs_2.delay()
            messages.info(request, 'done SequenceJobs_2 delay')
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})

        elif request.POST.get('Run_Seq_3', '')=="Run_Seq_3":
            import research.tasks as rmtks
            ff=os.path.join( settings.BASE_DIR,'celerylog' )
            if os.path.isfile(ff)==True:
                messages.info(request, 'celery log exists')
                sbp.call(['rm',ff])
                messages.info(request, 'Deleted celery log')

            messages.info(request, 'added SequenceJobs_3 delay')
            rmtks.SequenceJobs_3.delay()
            messages.info(request, 'done SequenceJobs_3 delay')
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})


        elif request.POST.get('update_stock_data', '')=="Update Stock Data":
            updatestockform=md.UpdateStockData_form(request.POST)#
            # updatestockform.process_stock_update()
            if updatestockform.is_valid():
                updatestockform.process_stock_update()
                
        else:
            updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})

    else:
        updatestockform=md.UpdateStockData_form(initial={'watchlist':'None'})

    if request.POST.get('basic_initialize', '')=="Basic Initialization":
        md.BasicInitialize()



    ff=os.path.join( settings.BASE_DIR,'celerylog' )
    if os.path.isfile(ff)==True:
        celerylog=mark_safe(sbp.check_output(['tail','-20',ff ]).replace('\n','<br>\n'))
    else:
        celerylog="log file does not exist yet"




    return render(request, 'stockdata/controlpanel.html', {'updatestockform':updatestockform,
                                                            'celerylog':celerylog,
                                                            })

def ViewStocksWatchLists(request):
    context = RequestContext(request)
    context['error']=None

    if request.method == 'POST':
        if request.POST.get('watch_view', '')=="View Watchlist":
            watchformview = md.Watchlist_view_form(request.POST,user=request.user)
            if watchformview.is_valid():
                watchformview = md.Watchlist_view_form(user=request.user,watchlistname=watchformview.cleaned_data['watchlist'],initial={'watchlist':watchformview.cleaned_data['watchlist']})
            else:
                context['error']="invalid form return on watchlist select"
                watchformview=md.Watchlist_view_form(user=request.user)

    elif request.method == 'GET':
        watchlistname=request.GET.get('w', '')
        fmt=request.GET.get('f', '')
        if watchlistname=='ListThem':
            ws=md.Watchlist.objects.all()
            L=[]
            for w in ws:
                L.append(str(w))
            ss='<h2>all available watchlists</h2>\n'
            for s in L:
                ss=ss+md.linkhref(reverse('stockdata:viewwatchlist')+'?w='+s+'&f=p',s)+'<br>\n'
            return HttpResponse(ss)

        elif watchlistname=='':
            watchformview=md.Watchlist_view_form(user=request.user)
        else:
            print "haha"
            print watchlistname
            ws=md.Watchlist.objects.get(watchlistname=watchlistname)
            L=ws.stocks.all()
            L=[str(ss) for ss in L]

            return HttpResponse("<br>".join(L))
    else:
        watchformview=md.Watchlist_view_form(user=request.user)


    return render(request, 'stockdata/watchlistmanager_view.html', {'watchformview': watchformview},context)

