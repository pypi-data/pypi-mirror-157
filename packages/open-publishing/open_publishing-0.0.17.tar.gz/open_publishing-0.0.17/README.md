# Releasing

1. Update version number
2. `pip install twine wheel`
3. `python setup.py bdist_wheel --universal`
4. `twine upload --repository-url https://pypi.openpublishing.com dist/*.whl`