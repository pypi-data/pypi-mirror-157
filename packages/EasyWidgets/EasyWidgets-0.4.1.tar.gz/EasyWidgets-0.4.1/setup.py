from setuptools import setup, find_packages

version = '0.4.1'

setup(name='EasyWidgets',
      version=version,
      description="A minimalistic approach to HTML generation and validation with TurboGears",
      long_description="Not so easy.",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

        ],
      keywords='TurboGears FormEncode TurboGears2',
      author='Rick Copeland',
      author_email='rick446@usa.net',
      url='https://sourceforge.net/p/easywidgets/code/',
      project_urls={
          "Documentation": "http://easywidgets.pythonisito.com",
          "Source Code": "https://sourceforge.net/p/easywidgets/code/",
      },
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data={'ew': [
            'i18n/*/LC_MESSAGES/*.mo',
            'templates/*.html',
            'public/*/*']},
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.7',
      install_requires=[
          # -*- Extra requirements: -*-
        'python-dateutil',
        'formencode',
        'markupsafe',
        'paste',
        'webob',
        'six>=1.13.0',
      ],
      tests_require=[
          'pytest',
          'webtest',
          'bs4',
          'jinja2',
          'jsmin',
          'cssmin',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [easy_widgets.engines]
      json = ew.render:JsonEngine
      core-ew = ew.render:CoreEngine
      jinja2 = ew.render:Jinja2Engine

      [paste.filter_factory]
      easy_widgets = ew.middleware:paste_filter_factory

      """,
      )
