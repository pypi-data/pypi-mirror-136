from .return_class import AbstractApiClass


class ModelVersion(AbstractApiClass):
    """
        A version of a model
    """

    def __init__(self, client, modelVersion=None, status=None, modelId=None, modelConfig=None, modelPredictionConfig=None, trainingStartedAt=None, trainingCompletedAt=None, datasetVersions=None, error=None, pendingDeploymentIds=None, failedDeploymentIds=None):
        super().__init__(client, modelVersion)
        self.model_version = modelVersion
        self.status = status
        self.model_id = modelId
        self.model_config = modelConfig
        self.model_prediction_config = modelPredictionConfig
        self.training_started_at = trainingStartedAt
        self.training_completed_at = trainingCompletedAt
        self.dataset_versions = datasetVersions
        self.error = error
        self.pending_deployment_ids = pendingDeploymentIds
        self.failed_deployment_ids = failedDeploymentIds

    def __repr__(self):
        return f"ModelVersion(model_version={repr(self.model_version)},\n  status={repr(self.status)},\n  model_id={repr(self.model_id)},\n  model_config={repr(self.model_config)},\n  model_prediction_config={repr(self.model_prediction_config)},\n  training_started_at={repr(self.training_started_at)},\n  training_completed_at={repr(self.training_completed_at)},\n  dataset_versions={repr(self.dataset_versions)},\n  error={repr(self.error)},\n  pending_deployment_ids={repr(self.pending_deployment_ids)},\n  failed_deployment_ids={repr(self.failed_deployment_ids)})"

    def to_dict(self):
        return {'model_version': self.model_version, 'status': self.status, 'model_id': self.model_id, 'model_config': self.model_config, 'model_prediction_config': self.model_prediction_config, 'training_started_at': self.training_started_at, 'training_completed_at': self.training_completed_at, 'dataset_versions': self.dataset_versions, 'error': self.error, 'pending_deployment_ids': self.pending_deployment_ids, 'failed_deployment_ids': self.failed_deployment_ids}

    def delete(self):
        """Deletes the specified model version. Model Versions which are currently used in deployments cannot be deleted."""
        return self.client.delete_model_version(self.model_version)

    def refresh(self):
        """Calls describe and refreshes the current object's fields"""
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """Retrieves a full description of the specified model version"""
        return self.client.describe_model_version(self.model_version)

    def get_training_logs(self, stdout=False, stderr=False):
        """Returns training logs for the model."""
        return self.client.get_training_logs(self.model_version, stdout, stderr)

    def wait_for_training(self, timeout=None):
        """
        A waiting call until model gets trained.

        Args:
            timeout (int, optional): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out.

        Returns:
            None
        """
        return self.client._poll(self, {'PENDING', 'TRAINING'}, delay=30, timeout=timeout)

    def get_status(self):
        """
        Gets the status of the model version under training.

        Returns:
            Enum (string): A string describing the status of a model training (pending, complete, etc.).
        """
        return self.describe().status
