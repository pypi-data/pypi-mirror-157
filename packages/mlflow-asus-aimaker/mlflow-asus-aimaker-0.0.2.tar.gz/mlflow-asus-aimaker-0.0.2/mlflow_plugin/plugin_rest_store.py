import urllib.parse
import os

from mlflow.store.tracking.file_store import FileStore
from mlflow.store.tracking.rest_store import RestStore
from mlflow.utils import rest_utils

# Extra environment variables which take precedence for setting the basic/bearer
# auth on http requests.
_TRACKING_USERNAME_ENV_VAR = "MLFLOW_TRACKING_USERNAME"
_TRACKING_PASSWORD_ENV_VAR = "MLFLOW_TRACKING_PASSWORD"
_TRACKING_TOKEN_ENV_VAR = "MLFLOW_TRACKING_TOKEN"

# sets verify param of 'requests.request' function
# see https://requests.readthedocs.io/en/master/api/
_TRACKING_INSECURE_TLS_ENV_VAR = "MLFLOW_TRACKING_INSECURE_TLS"
_TRACKING_SERVER_CERT_PATH_ENV_VAR = "MLFLOW_TRACKING_SERVER_CERT_PATH"

# sets cert param of 'requests.request' function
# see https://requests.readthedocs.io/en/master/api/
_TRACKING_CLIENT_CERT_PATH_ENV_VAR = "MLFLOW_TRACKING_CLIENT_CERT_PATH"


class PluginRestStore(RestStore):
    """FileStore provided through entrypoints system"""

    def __init__(self, store_uri=None, artifact_uri=None):
        self.is_plugin = True
        self.run_id = os.environ.get("MLFLOW_RUN_ID")
        self.experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID")
        super().__init__(self._get_default_host_creds)

    def _get_default_host_creds(store_uri):
        return rest_utils.MlflowHostCreds(
            host=os.environ.get("MLFLOW_REST_URL"),
            username=os.environ.get(_TRACKING_USERNAME_ENV_VAR),
            password=os.environ.get(_TRACKING_PASSWORD_ENV_VAR),
            token=os.environ.get(_TRACKING_TOKEN_ENV_VAR),
            ignore_tls_verification=os.environ.get(
                _TRACKING_INSECURE_TLS_ENV_VAR) == "true",
            client_cert_path=os.environ.get(
                _TRACKING_CLIENT_CERT_PATH_ENV_VAR),
            server_cert_path=os.environ.get(
                _TRACKING_SERVER_CERT_PATH_ENV_VAR),
        )

    def create_experiment(self, name, artifact_location=None, tags=None):
        # print("plugin:create_experiment")
        return self.experiment_id

    def delete_experiment(self, experiment_id):
        # print("plugin:delete_experiment - disable this func")
        return

    def restore_experiment(self, experiment_id):
        # print("plugin:restore_experiment - disable this func")
        return

    def rename_experiment(self, experiment_id, new_name):
        # print("plugin:rename_experiment - disable this func")
        return

    def get_run(self, run_id):
        # print("plugin:get_run")
        return super().get_run(self.run_id)

    def create_run(self, experiment_id, user_id, start_time, tags):
        # print("plugin:create_run")
        return super().get_run(self.run_id)

    def delete_run(self, run_id):
        # print("plugin:delete_run - disable this func")
        return

    def restore_run(self, run_id):
        # print("plugin:restore_run - disable this func")
        return

    def update_run_info(self, run_id, run_status, end_time):
        # print("plugin:update_run_info")
        return super().update_run_info(self.run_id, run_status, end_time)

    def set_tag(self, run_id, tag):
        # print("plugin:set_tag")
        return super().set_tag(self.run_id, tag)

    def delete_tag(self, run_id, key):
        # print("plugin:delete_tag")
        return super().delete_tag(self.run_id, key)

    def log_metric(self, run_id, metric):
        # print("plugin:log_metric")
        return super().log_metric(self.run_id, metric)

    def log_param(self, run_id, param):
        # print("plugin:log_param")
        return super().log_param(self.run_id, param)

    def record_logged_model(self, run_id, mlflow_model):
        # print("plugin:record_logged_model")
        return super().record_logged_model(self.run_id, mlflow_model)
