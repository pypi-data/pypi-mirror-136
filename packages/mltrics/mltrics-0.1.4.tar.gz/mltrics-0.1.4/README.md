# Mltrics

<b>Official command line utility to use Mltrics API programmatically.</b>

We help businesses evaluate, compare, and monitor machine learning models in production. Therefore, identify failure cases and take action immediately.

## Installation

Mltrics and its required dependencies can be installed using pip:
```sh
pip install mltrics
```

## Usage

Once mltrics package is installed, check out the following usage documentation:

#### Authenticate to mltrics platform

```python
from mltrics.mltrics import MltricsClient

import getpass

username = input("Enter username: ")
password = getpass.getpass(prompt='Enter password: ')
client = MltricsClient(username=username, password=password, env="prod")
```

### Update user profile

```python
organization, full_name = "<your-organization-name>", "<Your name>"
client.update_user_profile(organization=organization, full_name=full_name)
```

### Create model and upload predictions


#### Create a baseline model
```python
baseline_model_id, baseline_model_name = 'nn_iter_10k', 'Neural network (trained for 10K iters)'
baseline_model = client.create_model(baseline_model_id, baseline_model_name)
print(baseline_model)
```

### Update model details
```python
baseline_model_new_name = "Neural network (trained for 20K iters)"
updated_model = client.update_model_details(baseline_model_id, baseline_model_new_name)
print(updated_model)
```

#### Get uploaded models
```python
models = client.get_models()
models
```

#### Upload predictions for model
```python
baseline_preds = [
     {
      'pred_class': 'dog',
      'label_class': None,
      'model_id': baseline_model_id,
      'image_id': 'img1',
      'image_url': 'https://mltrics.s3.us-west-2.amazonaws.com/datasets/cats_vs_dogs/Cat/10896.jpg',
      'pred_file': None,
      'predictions': {},
     },
]
response = client.upload_model_predictions(baseline_model_id, baseline_preds)
print(response)
```

#### See all uploaded predictions
```python
predictions = client.get_model_predictions(baseline_model_id)
predictions
```

#### Create candidate model and upload predictions for candidate model
```python
### Create candidate model and upload predictions

candidate_model_id, candidate_model_name = "nn_50k_iter", "Neural Network (50K iter)"
candidate_model = client.create_model(candidate_model_id, candidate_model_name)

candidate_preds = [
     {
      'pred_class': 'cat',
      'label_class': None,
      'model_id': candidate_model_id,
      'image_id': 'img1',
      'image_url': 'https://mltrics.s3.us-west-2.amazonaws.com/datasets/cats_vs_dogs/Cat/10896.jpg',
      'pred_file': None,
      'predictions': {},
     },
]
response = client.upload_model_predictions(candidate_model_id, candidate_preds)
print(response)
```
### Get model comparison between baseline and candidate model
```python
comparison_results = client.compare_model_predictions(baseline_model_id, candidate_model_id)
print(comparison_results)
```