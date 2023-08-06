import logging
import requests


logging.basicConfig(level=logging.INFO)


def get_mltrics_hostname(env):
    if env == "prod":
        return "https://mltrics.ai"
    if env == "dev":
        return "https://dev.mltrics.ai"
    return "http://localhost:8000"


class MltricsClient:
    def __init__(self, username, password, env="prod"):
        self.username = username
        self.env = env
        self.hostname = get_mltrics_hostname(self.env)
        self.access_token = self._get_access_token(username, password)
        self.organization = self._get_organization()
        if self.organization is None:
            logging.warning(
                f"Organization not found for user {self.username}. Please update your profile by calling `client.update_user_profile(organizxaion='<organization>')` method"
            )

    def _get_access_token(self, username, password):
        response = requests.post(
            f"{self.hostname}/api/v1/access_token",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_organization(self):
        response = requests.get(
            f"{self.hostname}/api/v1/users",
            headers={"Authorization": "Bearer " + self.access_token},
        ).json()
        if "error" in response:
            return None
        return response["organization"]

    def update_user_profile(self, organization=None, full_name=None):
        body = {"full_name": full_name, "organization": organization}
        response = requests.put(
            f"{self.hostname}/api/v1/users",
            json=body,
            headers={"Authorization": "Bearer " + self.access_token},
        )
        response.raise_for_status()
        return response.json()

    def create_model(self, model_id, model_name):
        body = {
            "model_id": model_id,
            "model_name": model_name,
            "organization": self.organization,
        }
        response = requests.post(
            f"{self.hostname}/api/v1/models",
            json=body,
            headers={"Authorization": "Bearer " + self.access_token},
        ).json()
        if "error" in response:
            return (
                f"Error occured while creating model. Error: {str(response['error'])}"
            )
        return response

    def get_models(self):
        params = {"organization": self.organization}
        response = requests.get(
            f"{self.hostname}/api/v1/models",
            params=params,
            headers={"Authorization": "Bearer " + self.access_token},
        )
        response.raise_for_status()
        return response.json()

    def upload_model_predictions(self, model_id, predictions):
        body = {"predictions": predictions, "organization": self.organization}
        response = requests.post(
            f"{self.hostname}/api/v1/models/{model_id}",
            json=body,
            headers={"Authorization": "Bearer " + self.access_token},
        ).json()
        if "error" in response:
            return response["error"]
        return response["success"]

    def get_model_predictions(self, model_id):
        params = {"organization": self.organization}
        response = requests.get(
            f"{self.hostname}/api/v1/models/{model_id}/predictions",
            params=params,
            headers={"Authorization": "Bearer " + self.access_token},
        )
        response.raise_for_status()
        return response.json()["predictions"]

    def compare_model_predictions(self, baseline_model, candidate_model):
        params = {"organization": self.organization}
        response = requests.get(
            f"{self.hostname}/api/v1/models/compare/{baseline_model}/{candidate_model}",
            params=params,
            headers={"Authorization": "Bearer " + self.access_token},
        )
        response.raise_for_status()
        return response.json()["results"]
