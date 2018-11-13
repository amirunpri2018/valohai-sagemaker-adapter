# Valohai and SageMaker Adapter

Python package for integrating Jupyter notebooks 
(e.g. hosted in [SageMaker](https://aws.amazon.com/sagemaker/)) 
with [Valohai deep learning platform](https://valohai.com/).

## Development

```bash
# install release and development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# upgrading release dependencies
pip-compile --output-file requirements.txt requirements.in
pip install -r requirements.txt

# upgrading development dependencies
pip-compile --output-file requirements-dev.txt requirements-dev.in
pip install -r requirements-dev.txt

# running tests
python setup.py test
```
