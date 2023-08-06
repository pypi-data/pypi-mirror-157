# Investing Scraper
> This project created by __SamedZZZZ__.
___
# Introductions for Release a Version
1. Change version from [setup](./setup.py) file.
2. Delete the old version from [dist](./dist) folder.
3. python ".\setup.py" sdist
4. Test & actual servers
    1. twine upload --repository testpypi dist/*
    2. twine upload --repository-url "https://upload.pypi.org/legacy/" ".\dist\\*"