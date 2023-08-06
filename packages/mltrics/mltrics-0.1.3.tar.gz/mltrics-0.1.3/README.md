# Mltrics

<b>Official command line utility to use Mltrics API programmatically.</b>

We help businesses evaluate, compare, and monitor machine learning models in production. Therefore, identify failure cases and take action immidiately.

## Installation

Mltrics and its required dependencies can be installed using pip:
```sh
pip install mltrics
```

## Usage

Once mltrics package is installed, check out the following usage documentation:

#### Create model

```python
from mltrics.models import (
    create_model,
    get_models,
    upload_model_predictions,
    get_model_predictions,
    compare_model_predictions,
)

org = "<your-organization-name>"
model = create_model(model_id="svm", model_name="Support Vector Machine", org=org)
print(model)
```

#### Get all models

```python
models = get_models(org=org)
print(models[0])
```

#### Upload model predictions

```python
pred_data = [
     {
          'pred_class': 'dog',
          'label_class': 'cat',
          'model_id': 'svm',
          'image_id': 'img1',
          'image_url': 'https://mltrics.s3.us-west-2.amazonaws.com/datasets/cats_vs_dogs/Cat/10896.jpg',
          'pred_file': None,
          'predictions': {}  # store metadata in this dict
     },
]

predictions = upload_model_predictions(model_id="svm", org=org, predictions=pred_data)
print(predictions[0])
```

#### Get model predictions

```python
predictions = get_model_predictions(model_id="svm", org=org)
print(predictions[0])
```

#### Get models prediction comparison programatically

```python
result = compare_model_predictions(model_1="lr1", model_2="rf1", org="mltrics")
print(result[0])
```
