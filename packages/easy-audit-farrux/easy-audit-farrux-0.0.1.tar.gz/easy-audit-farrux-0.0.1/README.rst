=================
easy-audit-farrux
=================

Yet another Django audit log app, hopefully the simplest one.

Quick start
-----------

1. Add "easyauditfarrux" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'easyauditfarrux',
    ]

2. Add easyauditfarrux's middleware to your MIDDLEWARE (or MIDDLEWARE_CLASSES) setting like this::

    MIDDLEWARE = (
        ...
        'easyauditfarrux.middleware.easyaudit.EasyAuditMiddleware',
    )

3. Run 'python manage.py migrate easyauditfarrux' to create the audit models.

4. That's it! Now every CRUD event on your whole project will be registered in the audit models, which you will be able to query from the Django admin app. Additionally, this app will also log all authentication events and all URLs requested.
