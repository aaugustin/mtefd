=========================
Multiple Template Engines
=========================

========  ================
Author    Aymeric Augustin
Status    Draft
Created   2014-09-14
========  ================


Overview
========

Support some alternate template engines such as Jinja2_ out of the box.

Keep the Django Template Language as the default template engine.

Provide a stable API for integrating third-party template engines.

Support multiple template engines within the same Django project.


Rationale
=========

The Django Template Language (DTL) is `quite opinionated`_. It is purposefully
designed to limit the amount of logic that can be embedded in templates. This
choice keeps business logic outside of templates. Sometimes it also pushes
display logic into views.

Custom logic can be expressed through custom template filters or tags. APIs
such as simple_tag_, inclusion_tag_ and assignment_tag_ make common use cases
easier. Still, writing custom template tags can be hard. Often it results in
messy code.

Furthermore the DTL can be slow to render complex templates. While this isn't
an issue for small-to-medium websites, large websites with complex pages may
suffer from the cost of interpreting templates in Python. Attempts to optimize
rendering performance  `have failed`_.

PyPy improves rendering speed a lot. However, in 2014, PyPy isn't ready for
being recommended as Django's default deployment platform. Support for Python
3 is still experimental. PyPy is still a second-class citizen of the Python
ecosystem. For instance, well-known Linux distributions don't ship a WSGI
server running on PyPy out of the box.

For at least these two reasons, Django users are increasingly turning to
alternate template engines. Jinja2 is the most popular choice thanks to its
syntax inspired by the DTL and its excellent performance.

Given Django's `loose coupling`_ philosophy, it is relatively easy to swap the
template engine. However seamless integration requires a non-trivial amount of
code. For example `half a dozen libraries`_ compete for providing integration
between Django and Jinja2.

Therefore, this DEP proposes to define a formal API for integrating template
engines and to provide built-in support for two of them: `template strings`_
and Jinja2_.


Appendix: the Django Template Language
======================================

Documentation
-------------

Django's documentation describes the Django Template Language in four pages:

* `Topic guide`_
* `Reference`_
* `Built-in tags and filters`_
* `Custom tags and filters`_

Features
--------

The syntax of the Django Template Language supports four constructs:

* Variables and lookups
* Filters, built-in or custom
* Tags, built-in or custom
* Comments

In addition, its rendering engine provides four notable features:

* Template inheritance
* Support for internationalization, localization and time zones
* Automatic HTML escaping for XSS protection
* Tight integration with the CSRF protection

It also provides debatable "designer-friendly" error handling.

Settings
--------

Currently, Django provides six settings to configure its template engine:

* ``ALLOWED_INCLUDE_ROOTS`` is an artifact of the ``{% ssi %}`` tag which
  should be uncommon in modern Django projects. There is no pressing reason
  to do anything about it, where "anything" would probably mean "deprecate
  this tag in favor of ``{% include %}``".

* ``TEMPLATE_CONTEXT_PROCESSORS`` configures template context processors,
  which make common values available in the context of any template that is
  rendered with a ``RequestContext`` or with the ``render`` shortcut.

* ``TEMPLATE_DEBUG`` is a generic switch. Third-party template engines that
  provide a debug mode should honor its value. When it's set, Django creates
  a template stack trace when an exception occurs in a template and adds an
  ``origin`` attribute to ``Template`` objects.

* ``TEMPLATE_DIRS`` configures the filesystem template loader.

* ``TEMPLATE_LOADERS`` configures templates loaders.

* ``TEMPLATE_STRING_IF_INVALID`` is a debugging tool that suffers from
  usability issues. It cannot be permanently set to a non-empty value because
  the admin misbehaves in that case. Everyone pretends that it doesn't exist.

The template engine also takes a few other settings into account:

* ``FILE_CHARSET`` defines the charset of template files loaded from the
  filesystem. Third-party template engines should honor its value.

* ``INSTALLED_APPS`` defines the content of the application registry, which is
  thenused by the app directories template loaders to locate templates in
  installed applications.

* ``DATE_FORMAT``, ``SHORT_DATE_FORMAT`` and ``SHORT_DATETIME_FORMAT``
  describe formatting of dates and datetimes in templates when localization
  is disabled. Third-party template engines may use them if it makes sense.

* ``USE_I18N``, ``USE_L10N`` and ``USE_TZ`` activate internationalization,
  localization and time zones. Third-party template engines that provide
  comparable features should account for these settings.

Loaders
-------

Django ships four loaders, two of which are enabled by default:

* ``filesystem``: searches ``TEMPLATE_DIRS``
* ``app_directories``: searches the ``templates`` subdirectories of installed
  applications
* ``eggs``: like ``app_directories`` but for applications installed as eggs
* ``cached``: wraps other loaders and caches compiled templates

Loaders are invoked through global APIs: ``get_template`` and
``select_template``.

Custom loaders are implemented by subclassing ``BaseLoader`` and overriding
``load_template_source``.

The documentation describes how to return a non-Django template from a loader.
While this is a reasonable point to interface with a third-party template
engine, the current API requires lots of glue code. That's why this proposal
offers a more structured solution.

Rendering
---------

In addition to the expected ``Template`` class, there are two ``Context``
classes:

* ``Template``: parses a string and compiles it, provides a ``render`` method
* ``Context``: like a ``dict``, except it's a stack of ``dict``, also stores
  some state used for rendering
* ``RequestContext``: like ``Context`` but runs template context processors

In order to preserve loose coupling, ``Context`` doesn't know anything about
HTTP requests. But almost all templates need values from the ``request``.
``RequestContext`` is the pragmatic answer: it's instantiated with ``request``
and passes it to context processors.

The CSRF processor is hardcoded in ``RequestContext`` in order to remove one
configuration step and thus minimize the likelihood that users simply disable
the CSRF protection.


Shortcuts
---------

While it isn't part of the template engine itself, the ``django.shortcuts``
module provides the ``render`` function, which is the most common entry point
for rendering a template, and its sibling ``render_to_response``.

These functions invoke ``render_to_string`` to render the template and wrap
the result in a ``HttpResponse``.

``render`` creates a ``RequestContext`` for rendering while
``render_to_response`` uses a plain ``Context``.


Appendix: Python template engines
=================================

This section shows basic usage of common Python template engines in a web
application.

All examples except Django follow the configure / load / render lifecycle.

Template engine adapters for Django would wrap these APIs.

Examples render a template called ``NAME = 'hello.html'`` found in one of
``TEMPLATE_DIRS`` with a context defined as ``CONTEXT = {'name': 'world'}``.

Chameleon_
----------

::

    from chameleon import PageTemplateLoader

    loader = PageTemplateLoader(TEMPLATE_DIRS)
    template = loader[NAME]
    html = template.render(**CONTEXT)

Configuration is performed by passing keyword arguments to
``PageTemplateLoader``, which passes them to ``render``.


Django_
-------

::

    from django.template import loader

    template = loader.get_template(NAME)
    html = template.render(CONTEXT)

or::

    from django.template.loader import render_to_string

    html = render_to_string(NAME, CONTEXT)

or::

    from django.template.loader import render_to_string

    # assuming the code is handling a HttpRequest
    html = render_to_string(NAME, CONTEXT, RequestContext(request))

Configuration is performed through global settings. (This is bad.)


Genshi_
-------

::

    from genshi.template import TemplateLoader

    loader = TemplateLoader(TEMPLATE_DIRS)
    template = loader.load(NAME)
    html = template.generate(**CONTEXT).render('html')

The author couldn't determine how configuration is performed. Genshi is more
complex than other engines analyzed here.

Jinja2_
-------

::

    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIRS))
    template = env.get_template(NAME)
    html = template.render(**CONTEXT)

Jinja2 has a concept of environment that contains global configuration.
Template loading is exposed as a method of the environment.

Loaders are configured in the environment. Jinja2 provides roughly the same
loaders as Django.


Mako_
-----

::

    from mako.lookup import TemplateLookup

    lookup = TemplateLookup(TEMPLATE_DIRS)
    template = lookup.get_template(NAME)
    html = template.render(**CONTEXT)

Configuration is performed by passing keyword arguments to ``TemplateLookup``,
which passes them to ``render``.

`Template strings`_
-------------------

Template strings provide simplified string interpolation. They only implement
rendering, with a variant that raises exceptions for missing substitutions and
another variant that ignores them.

::

    from string import Template

    html = Template("Hello $name").safe_substitute(**CONTEXT)


FAQ
===

Why not simply switch to Jinja2?
--------------------------------

Since Django templates share some syntax with Jinja2, it's possible to write a
trivial example that will work with both engines.

However, as shown above, Django templates provide several features that don't
have a straightforward equivalent in Jinja2.

Porting a non-trivial application from Django templates to Jinja2 requires a
significant amount of work and cannot be automated.

If you aren't convinced, try porting the ``django.contrib.admin`` templates —
barely 1200 lines of template code — and see for yourself.

Will the Django Template Langage be deprecated?
-----------------------------------------------

No, there is no plan to deprecate it at this time.


Acknowledgements
================

Thanks Loic Bistuer, Tim Graham, Jannis Leidel, Carl Meyer, Baptiste Mispelon
and Daniele Procida for commenting drafts of this document. Many good ideas
are theirs.


Copyright
=========

This document has been placed in the public domain per the `Creative Commons
CC0 1.0 Universal license`_.


.. _Jinja2: http://jinja.pocoo.org/
.. _quite opinionated: https://docs.djangoproject.com/en/stable/misc/design-philosophies/#template-system
.. _have failed: https://github.com/mitsuhiko/templatetk/blob/master/POST_MORTEM
.. _simple_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#simple-tags
.. _inclusion_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#inclusion-tags
.. _assignment_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#assignment-tags
.. _loose coupling: https://docs.djangoproject.com/en/stable/misc/design-philosophies/#loose-coupling
.. _half a dozen libraries: https://www.djangopackages.com/grids/g/jinja2-template-loaders/
.. _template strings: https://docs.python.org/3/library/string.html#template-strings
.. _Chameleon: https://chameleon.readthedocs.org/
.. _Django: https://docs.djangoproject.com/en/stable/topics/templates/
.. _Genshi: http://genshi.edgewall.org/
.. _Mako: http://docs.makotemplates.org/
.. _Topic guide: https://docs.djangoproject.com/en/stable/topics/templates/
.. _Reference: https://docs.djangoproject.com/en/stable/ref/templates/api/
.. _Built-in tags and filters: https://docs.djangoproject.com/en/stable/ref/templates/builtins/
.. _Custom tags and filters: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/
.. _Creative Commons CC0 1.0 Universal license: http://creativecommons.org/publicdomain/zero/1.0/deed
