=====
JW-NX
=====

#ToDO

Quick start
-----------

1. Add "jw_nx and knox" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'knox',
        'jw_nx',
        ...
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('jw_nx/', include('jw_nx.urls')),

3. Run ``python manage.py makemigrations``.
4. Run ``python manage.py migrate``.