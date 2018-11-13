# Valohai and SageMaker Adapter

Python package for integrating Jupyter notebooks 
(e.g. hosted in [SageMaker](https://aws.amazon.com/sagemaker/)) 
with [Valohai deep learning platform](https://valohai.com/).

## Development

Development setup:

```bash
# install release and development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Upgrading dependencies:

```bash
# upgrading release dependencies
pip-compile --output-file requirements.txt requirements.in
pip install -r requirements.txt

# upgrading development dependencies
pip-compile --output-file requirements-dev.txt requirements-dev.in
pip install -r requirements-dev.txt
```

Testing the package:

```bash
# run all tests
python setup.py test
```

Test coverage:

```bash
# calculate coverage
coverage run --source valohai_sagemaker setup.py test

# view coverage in text (after calculating it)
coverage report -m

# view coverage in HTML (after calculating it)
coverage html
open htmlcov/index.html
```
