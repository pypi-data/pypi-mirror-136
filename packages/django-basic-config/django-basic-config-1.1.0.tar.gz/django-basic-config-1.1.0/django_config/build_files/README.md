# to build

- make a folder named `django_config_build`.
- get source code.  Either:

    - clone this repository into that folder: `git clone https://github.com/jonathanmorgan/django_config"
    - or (DO THIS) grab the release source tar ball for the release you want to build.

- move the following files into `django_config_build`:

    - django_config/build/LICENSE
    - django_config/build/MANIFEST.in
    - django_config/build/setup.py
    - django_config/README.md

- make sure you have `setuptools`, `wheel`, and `twine` packages installed in the Python environment you are using to build.
- in the `django_config_build` folder:

    - build: `python setup.py sdist bdist_wheel`
    - test upload to test.pypi.org: `python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
    - to install from test: `pip install --index-url https://test.pypi.org/simple/ django-basic-config`
    - if all works OK, upload to pypi.org: `python3 -m twine upload dist/*`
    - install using pip and test: `pip install django-basic-config`

# More details

- [https://packaging.python.org/tutorials/packaging-projects/](https://packaging.python.org/tutorials/packaging-projects/)
- semantic versioning: [https://semver.org/](https://semver.org/)
- More details on all the options for setup.py: [https://packaging.python.org/guides/distributing-packages-using-setuptools/](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- creating releases on github.com: [https://help.github.com/en/github/administering-a-repository/creating-releases](https://help.github.com/en/github/administering-a-repository/creating-releases)
- making your code citable: [https://guides.github.com/activities/citable-code/](https://guides.github.com/activities/citable-code/)
- packaging django apps: [https://docs.djangoproject.com/en/dev/intro/reusable-apps/](https://docs.djangoproject.com/en/dev/intro/reusable-apps/)
