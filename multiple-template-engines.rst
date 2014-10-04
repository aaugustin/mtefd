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


.. _Jinja2: http://jinja.pocoo.org/
.. _quite opinionated: https://docs.djangoproject.com/en/stable/misc/design-philosophies/#template-system
.. _have failed: https://github.com/mitsuhiko/templatetk/blob/master/POST_MORTEM
.. _simple_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#simple-tags
.. _inclusion_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#inclusion-tags
.. _assignment_tag: https://docs.djangoproject.com/en/stable/howto/custom-template-tags/#assignment-tags
.. _loose coupling: https://docs.djangoproject.com/en/stable/misc/design-philosophies/#loose-coupling
.. _half a dozen libraries: https://www.djangopackages.com/grids/g/jinja2-template-loaders/
.. _template strings: https://docs.python.org/3/library/string.html#template-strings
