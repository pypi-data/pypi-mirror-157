# Django Universal Worker Service

Django implementation of the IVOA UWS pattern.

The Universal Worker Service (UWS) pattern defines how to manage asynchronous execution of jobs on a service. Any application of the pattern defines a family of related services with a common service contract. Possible uses of the pattern are also described.

Url: https://www.ivoa.net/documents/UWS/
DOI: 10.5479/ADS/bib/2016ivoa.spec.1024H

## Quick start
1. add `uws` to your `INSTALLED_APPS` setting likes this:
```python
    INSTALLED_APPS = [
        ...
        'uws',
        ...
    ]
```

2. Include the uws URLconf in your project urls.py like this::
```python
    ...
    path('uws/', include('uws.urls')),
    ...
```

3. Run `python manage.py migrate uws` to create the UWS models.
    Optionally: `python manage.py migrate uws --database uws` by specifying
```python
    DATABASE_ROUTERS = [
    ...
    "uws.database_router.UWSDatabaseRouter",
    ...
    ]
```
    and a `uws` entry in your `DATABASES` setting


4. **TODO:** Add Celery configuration
    Create a `celery.py` file in the `<project>` folder:
```python
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.default_settings")

app = Celery("project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

```



## Worker


## Contributing

For developer access to this repository, please send a message on the [ESAP channel on Rocket Chat](https://chat.escape2020.de/channel/esap).
