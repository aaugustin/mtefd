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
being recommended as Django's default deployment platform. Its support for
Python 3 is still experimental. PyPy is still a second-class citizen of the
Python ecosystem. For instance, well-known Linux distributions don't ship a
WSGI server running on PyPy out of the box.

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


Design decisions
================

General architecture
--------------------

The operation of a template engine can be split in three steps:

1. Configure: set options that will affect the following two steps
2. Load: find the template for a given identifier and preprocess it
3. Render: process a template with a context and return a string

When this document discusses configuring, loading or rendering, it refers to
these steps or to their implementation.

General principles
------------------

The Django Template Language hasn't evolved much over the years. It carries
several design decisions made in 2005. Nine years later, if the Django team
started from a clean slate, it may make different decisions.

As a consequence, this project avoids encoding the legacy of the Django
Template Language in APIs. It doesn't encourage third-party engines to provide
compatibility with specific features of Django templates.

The main exception is security, especially defense against XSS and CSRF
attacks. This DEP is prescriptive for security-related APIs.

Built-in engines
----------------

Supporting pluggable engines is a strategy that has served Django well in many
areas. It's more valuable in the long term than just merging a mature Django -
Jinja2 adapter.

The Django Template Language must remain the default to avoid creating a huge
backwards incompatibility without an acceptable upgrade path for the ecosystem
at large.

Support for template strings is built-in to validate a minimal implementation.
This is akin to the local memory cache backend or, to a lesser extent, to the
SQLite database backend.

Support for Jinja2 is built-in because it appears to be the most widely used
alternative. This DEP will be updated if evidence appears that another engine
is more popular.

Support for other template engines is expected to be provided by third-party
libraries. The reasons for doing so are exactly the same as for the cache and
database engines.

Engine selection
----------------

Developers must be able to select the most appropriate engine for each page
e.g. use Jinja2 only for a few performance-intensive pages. This provides a
better migration story for converting a website from one engine to another
too. That's why Django has to support several template engines in the same
project.

If several template engines are configured, when tasked with rendering a given
template, Django must choose one. There are at least four ways to do this.

1. Explicitly selecting an engine, for example::

       html = render_to_string('index.html', context, engine='jinja2')

   Many APIs would work here, but all would add some boilerplate.

2. Explicitly tagging templates, for example::

       {# language: jinja2 #}

   This would work like charset declaration in Python modules. It's marginally
   less ugly than option 1.

   Unfortunately, due to the way template engines are implemented, Django
   would have to locate the template, figure out which engine it uses, and
   then the engine would locate the template again, load it and render it.
   That would restrict engines to selection mechanisms that Django implements.
   That would also introduce an unhealthy amount of duplication and possibly
   some bugs.

3. Convention: the file extension would define which engine to use. That's a
   pragmatic solution. Ruby on Rails would likely take this route.

   However, since the Django ecosystem favors configuration over convention,
   most Django - Jinja2 bridges provide a setting that controls which
   templates must be rendered with Jinja2. That setting defines a regular
   expression against which template names are tested.

   If extensions are configurable, there's a risk that pluggable apps will end
   up with incompatible requirements. For example, if app A wants .html files
   to be rendered with the DTL and app B wants them to be rendered with
   Jinja2, it becomes impossible to use both apps in the same project. A
   configuration mechanism that handles such cases would be too complex.

   If extensions are enforced, some users will be have to use file names that
   they don't like or that their editors don't handle well. The potential for
   bikeshedding makes this an unattractive option. Finally template loaders
   that don't store templates in the filesystem may use identifiers without a
   file extension.

4. Trial and error: in order to load a template, Django would iterate over the
   list of configured template engines and attempt to locate the template with
   each of them until one succeeds.

   Since there's no way to ascertain whether a particular file is intended for
   a given template engine, engines that load templates from the filesystem
   should search for templates in distinct locations. Each engine must have
   its own list of directories to load templates from and these lists mustn't
   overlap.

   As a consequence, a convention would still be necessary to give each engine
   its own subdirectory within installed applications to load templates from.
   This should simply be the engine's name e.g. ``/jinja2/`` for Jinja2. In
   order to preserve backwards-compatibility, it would remain ``/templates/``
   for Django templates. This convention has a lower impact on users because
   editors don't care about directory names the same way they do about file
   extensions.

   The intent of this design is that only one engine will find a template with
   a given identifier and that the order of template engines won't matter.
   That said, nothing prevents users from relying on the order of template
   engines to implement fallback schemes.

Option 4 appears to provide the best compromise. It isn't perfect but it beats
the alternatives and it doesn't have any drawbacks for daily use. It creates a
healthy separation between templates designed for each engine.

In addition, option 1 should be provided because it lets users implement their
own scheme if option 4 doesn't cater for their use case and it won't add much
complexity to the implementation.

Configuring
-----------

Template engines are configured in a new setting called ``TEMPLATES``. Here's
an example::

    TEMPLATES = {
        'django': {
            'ENGINE': 'django.template.backends.django',
            'DIRS': [],
            'APP_DIRS': True,
        },
        'jinja2': {
            'ENGINE': 'django.template.backends.jinja2',
            'DIRS': [os.path.join(BASE_DIR, 'jinja2')],
            'APP_DIRS': False,
            'OPTIONS': {
                'extensions': ['jinja2.ext.loopcontrols'],
            },
        },
    }

The structure is modeled after ``DATABASES`` and ``CACHES``, although there's
a fairly important difference. Since the algorithm described above will allow
Django to select a template engine automatically, key names won't matter much
in general. However the order may matter; in that case the setting should be a
``collections.OrderedDict``.

Since most engines load templates from files, the top-level configuration
contains two normalized settings:

- ``DIRS`` works like Django's current ``TEMPLATE_DIRS``
- ``APP_DIRS`` tells whether the engine should try to load templates from
  conventional subdirectories inside applications

``APP_DIRS`` is a boolean rather than the name of the subdirectory because
that name is a property of the template engine, not a property of the project.
It must be shared by all applications for interoperability of pluggable apps.
Each engine will define a conventional name.

Engine-specific settings go inside an ``OPTIONS`` dictionary. The intent is
that they should be passed as keyword arguments when initializing the template
engine.

Loading
-------

Loading and rendering look like they could be handled independently, but
they're coupled as soon as a template extends or includes another one, as the
renderer needs to call the loader. Thus Django must have each template engine
configure and use its own loading infrastructure.

With its default settings, Django loads templates from directories listed in
the ``TEMPLATE_DIRS`` setting and from the ``'templates'`` subdirectories
inside installed applications. The latter allows pluggable applications to
ship templates.

These basic features should be provided by all template engines. Template
engines may provide other options such as loading templates from Python eggs.

Rendering
---------

Template engines must provide automatic HTML escaping to protect against XSS
attacks. It must be enabled by default for two reasons:

- security should be the default
- that's Django's historical behavior

Autoescaping is disabled by default in Jinja2, leaving it up the developer to
define which variables need escaping and favoring performance over security.
The Django adapter will reverse this default.

Furthermore, when a template is rendered with a ``RequestContext``, templates
engines must make the CSRF token available in the context, ideally with an
equivalent of Django's ``{% csrf_token %}`` tag.

This makes it less likely that developers encounter problems with the CSRF
protection framework and choose te simply disable it.


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


Appendix: Django - Jinja2 adapters
==================================

There are three maintained and mature Django - Jinja2 adapters: in
chronological order, Coffin, Jingo, and Django-Jinja.

Coffin
------

Coffin provides replacements for several Django APIs related to templates such
as ``render``. Views must use Coffin APIs explicitly.

This approach predates 44b9076b_ which recommends integrating third-party
template engines with custom template loaders.

Coffin focuses on minimizing differences between Django and Jinja2 template by
making many Django filters and tags usable from Jinja2 templates.

Jingo
-----

Jingo provides a template loader for Jinja2 templates that must be placed
before Django's template loaders in ``TEMPLATE_LOADERS``.

It provides APIs for registering globals and filters, but not tests. It
recommends doing the registration in a conventional ``helpers`` submodule in
installed applications.

It registers a few globals and filters, including replacements for two of
Django's most useful template tags: ``csrf`` and ``url``. However it doesn't
deal with ``static``.

It's capable of monkey-patching support for ``__html__`` but that isn't needed
any more since af64429b_.

Django-Jinja
------------

Django-Jinja replaces Django's template loaders with alternatives that handle
both Jinja2 and Django templates.

It advertises wide compatibility with Django template filters and tags. The
documentation doesn't talk about limitations, if any.

It integrates with Django's i18n framework, especially the ``makemessages``
management command.

It connects Jinja2's bytecode cache to Django's caching framework.

It provides APIs for registering globals and filters.

It includes ``url`` and ``static`` globals to replace Django's tags.

It supports a few popular third-party applications explicitly.


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

Shouldn't Jinja2 be the default?
--------------------------------

In order to minimize disruption for developers, this project doesn't change
the default engine. However it paves the way for doing so in a later release.

Will the Django Template Langage be deprecated?
-----------------------------------------------

No, there is no plan to deprecate it at this time.

How does this account for differences in APIs?
----------------------------------------------

As shown above, most Python templates engines support the following pattern::

    loader = TemplateLoader(**CONFIG)
    template = loader.load(NAME)
    html = template.render(**CONTEXT)

This basic API serves as a common denominator for all engines. Then it's up to
each engine to provide additional APIs, mainly as ``TemplateLoader`` options.

This document describes other APIs but they aren't mandatory. If they don't
make sense for a particular engine, they can be stubbed.

Isn't this going to fragment the ecosystem of pluggable apps?
-------------------------------------------------------------

First, there's a debate about the usefulness of shipping user-facing templates
in pluggable apps. Templates must be customized to fit the website's design,
usually by inheriting a base template. That's why many pluggable apps don't
ship templates and document which templates the developer must create instead.
In that case, the developer can use their favorite template engine.

If a pluggable app ships standalone templates, then which template engine
they're written for doesn't matter. The author must document which template
engine it uses and the developer must ensure their project meets this
requirement.

Pluggable apps that provide template filters or tags should consider adding
equivalent Python functions to their public APIs for interoperability with any
template engine.

Is it possible to use Django template filters or tags with other engines?
-------------------------------------------------------------------------

This project doesn't aim at creating Django-flavored versions of various
Python template engines. It aims at building a foundation upon which every
developer can build the template engine they need if it doesn't exist yet.

This idea can be implemented but it belongs to a third-party module.

What about template loaders and context processors?
---------------------------------------------------

Likewise, these are specific features of the Django template engine. Other
engines should provide their own APIs for loading templates and for adding
common context to all templates.

Can Django support my favorite frontend template engine?
--------------------------------------------------------

Nice try ;-) This is out of scope for this project.


Acknowledgements
================

Thanks Loic Bistuer, Tim Graham, Jannis Leidel, Carl Meyer, Baptiste Mispelon,
Daniele Procida and Josh Smeaton for commenting drafts of this document. Many
good ideas are theirs.


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
.. _44b9076b: https://github.com/django/django/commit/44b9076bbed3e629230d9b77a8765e4c906036d1
.. _af64429b: https://github.com/django/django/commit/af64429b991471b7a441e133b5b7d29070984f24
.. _Topic guide: https://docs.djangoproject.com/en/stable/topics/templates/
.. _Reference: https://docs.djangoproject.com/en/stable/ref/templates/api/
.. _Built-in tags and filters: https://docs.djangoproject.com/en/stable/ref/templates/builtins/
.. _Custom tags and filters: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/
.. _Creative Commons CC0 1.0 Universal license: http://creativecommons.org/publicdomain/zero/1.0/deed
