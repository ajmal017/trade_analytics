1. Database optimization --> primary key, indices
2. Abstract model class to be inherited
3. files in your app --> libs.py, tasks.py, models.py, views.py
4. class based views
5. use messages
6. use assert
7. use exceptions
8. use logging
9. use test everywhere
10. design for multi threading 
10. Easily Switch between celery and multiprocessing
11. defined an initial initializer database... for a fresh restart
12.  Keep apps always as independent as possible
13.  django-datascience app --> Independent re-usable app only for Machine learning based computations and data staorage/visualize
14.                         --> separate database
14.                         --> make chart templates in javascript/bokeh/matplotlib
14.                         --> make template dashboards
15.                         --> only used for doing data science and visualizations
16.                         --> interactive : form to select data type of columns
15. raise 404 pages from view with clearn message
16. should contain multiple try excepts to capture the right error and serve the right error
17. Each request served by a class-based view has an independent state; therefore, it is safe to store state variables on the instance (i.e., self.foo = 3 is a thread-safe operation). Arguments passed to a view are shared between every instance of a view. This means that you shouldn’t use a list, dictionary, or any other mutable object as an argument to a view. If you do and the shared object is modified, the actions of one user visiting your view could have an effect on subsequent users visiting the same view.
18.  










----------------------------------------USEFULL Commands-----------------------------------

1. python manage.py startapp polls
2. 
