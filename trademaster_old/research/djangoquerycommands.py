from django.db.models import Q
from django.db.models import F, Count
from django.db.models.functions import Length, Upper, Value



Q(question__startswith='Who'),
Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))
Q(question__startswith='Who') | Q(question__startswith='What')
Q(pub_date__year=2005)
Q(pub_date__gt=datetime.date(2005, 1, 3))
Q(num_employees__gt=F('num_chairs') * 2)   # num of employess > twice the number of chairs

Entry.objects.filter(pub_date__year=2005).order_by('-pub_date', 'headline')
Entry.objects.order_by('?')  // for random
Entry.objects.order_by('pub_date').distinct('pub_date')

Entry.objects.dates('pub_date', 'year') # all disticnt year
Entry.objects.dates('pub_date','month') # all disticnt 'month'
Entry.objects.dates('pub_date', 'day', order='DESC')

Blog.objects.get(name__iexact='beatles blog')
Blog.objects.get(name__iexact=None)

Entry.objects.get(id__exact=14)
Entry.objects.get(id__exact=None)

Entry.objects.get(headline__contains='Lennon')

Entry.objects.filter(id__in=[1, 3, 4])


inner_qs = Blog.objects.filter(name__contains='Cheddar')
entries = Entry.objects.filter(blog__in=inner_qs)


values = Blog.objects.filter(name__contains='Cheddar').values_list('pk', flat=True)
enstries = Entry.objects.filter(blog__in=list(values))


Entry.objects.filter(id__gt=4)
Entry.objects.filter(headline__startswith='Will')
Entry.objects.filter(headline__istartswith='will')
Entry.objects.filter(headline__endswith='cats')
Entry.objects.filter(headline__iendswith='will')

Entry.objects.filter(pub_date__date=datetime.date(2005, 1, 1))
Entry.objects.filter(pub_date__date__gt=datetime.date(2005, 1, 1))


import datetime
start_date = datetime.date(2005, 1, 1)
end_date = datetime.date(2005, 3, 31)
Entry.objects.filter(pub_date__range=(start_date, end_date))




#slow
e = Entry.objects.get(id=5)
b = e.blog

#fast
e = Entry.objects.select_related('blog').get(id=5)
b = e.blog


# create and refreshing ---- this is autosave
company = Company.objects.create(name='Google', ticker=Upper(Value('goog')))
company.refresh_from_db()


 Poll.objects.get( Q(question__startswith='Who'), Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))  )



filter()
exclude()
Entry.objects.exclude(pub_date__gt=datetime.date(2005, 1, 3), headline='Hello')



## annotation create new fields in model instance
company = Company.objects.filter(num_employees__gt=F('num_chairs')).annotate(chairs_needed=F('num_employees') - F('num_chairs')).first()
Company.objects.annotate(num_products=Count('products'))
Company.objects.annotate(num_products=Count(F('products')))


>>> q = Blog.objects.aggregate(Count('entry'))
{'entry__count': 16}


