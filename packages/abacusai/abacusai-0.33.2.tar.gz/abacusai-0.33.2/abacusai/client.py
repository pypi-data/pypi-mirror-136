import inspect
import io
import logging
import os
import time
from functools import lru_cache
from typing import Dict, List

import pandas as pd
import requests
from packaging import version
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api_key import ApiKey
from .application_connector import ApplicationConnector
from .batch_prediction import BatchPrediction
from .batch_prediction_version import BatchPredictionVersion
from .database_connector import DatabaseConnector
from .dataset import Dataset
from .dataset_column import DatasetColumn
from .dataset_version import DatasetVersion
from .deployment import Deployment
from .deployment_auth_token import DeploymentAuthToken
from .feature import Feature
from .feature_group import FeatureGroup
from .feature_group_export import FeatureGroupExport
from .feature_group_version import FeatureGroupVersion
from .file_connector import FileConnector
from .file_connector_instructions import FileConnectorInstructions
from .file_connector_verification import FileConnectorVerification
from .function_logs import FunctionLogs
from .language_detection_prediction import LanguageDetectionPrediction
from .model import Model
from .model_metrics import ModelMetrics
from .model_monitor import ModelMonitor
from .model_monitor_version import ModelMonitorVersion
from .model_version import ModelVersion
from .modification_lock_info import ModificationLockInfo
from .nlp_sentiment_prediction import NlpSentimentPrediction
from .organization_group import OrganizationGroup
from .project import Project
from .project_dataset import ProjectDataset
from .project_validation import ProjectValidation
from .refresh_pipeline_run import RefreshPipelineRun
from .refresh_policy import RefreshPolicy
from .return_class import AbstractApiClass
from .schema import Schema
from .streaming_auth_token import StreamingAuthToken
from .streaming_connector import StreamingConnector
from .training_config_options import TrainingConfigOptions
from .upload import Upload
from .upload_part import UploadPart
from .use_case import UseCase
from .use_case_requirements import UseCaseRequirements
from .user import User


def _requests_retry_session(retries=5, backoff_factor=0.1, status_forcelist=(502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


@lru_cache(maxsize=None)
def _discover_service_url(service_discovery_url, client_version, deployment_id, deployment_token):
    from .cryptography import get_public_key, verify_response
    if not service_discovery_url:
        return None
    response = _requests_retry_session().get(service_discovery_url, headers={'clientVersion': client_version}, params={
        'deploymentId': deployment_id, 'deploymentToken': deployment_token})
    response_dict = response.json()

    verify_response(get_public_key(), response_dict)
    return response_dict['url']


@lru_cache()
def _get_service_discovery_url():
    return os.getenv('ABACUS_SERVICE_DISCOVERY_URL')


class ClientOptions:
    def __init__(self, exception_on_404=True, server='https://api.abacus.ai'):
        self.exception_on_404 = exception_on_404
        self.server = server


class ApiException(Exception):
    def __init__(self, message, http_status, exception=None):
        self.message = message
        self.http_status = http_status
        self.exception = exception or 'ApiException'

    def __str__(self):
        return f'{self.exception}({self.http_status}): {self.message}'


class BaseApiClient:
    client_version = '0.33.1'

    def __init__(self, api_key: str = None, server: str = None, client_options: ClientOptions = None, skip_version_check: bool = False):
        self.api_key = api_key
        self.web_version = None
        self.client_options = client_options or ClientOptions()
        self.server = server or self.client_options.server
        self.user = None
        self.service_discovery_url = _get_service_discovery_url()
        # Connection and version check
        if not skip_version_check:
            try:
                self.web_version = self._call_api(
                    'version', 'GET', server_override='https://api.abacus.ai')
                if version.parse(self.web_version) > version.parse(self.client_version):
                    logging.warning(
                        'A new version of the Abacus.AI library is available')
                    logging.warning(
                        f'Current Version: {self.client_version} -> New Version: {self.web_version}')
            except Exception:
                logging.error(
                    'Failed get the current API version from Abacus.AI (https://api.abacus.ai/api/v0/version)')
        if api_key is not None:
            try:
                self.user = self._call_api('getUser', 'GET')
            except Exception:
                logging.error('Invalid API Key')

    def _clean_api_objects(self, obj):
        for key, val in (obj or {}).items():
            if isinstance(val, StreamingAuthToken):
                obj[key] = val.streaming_token
            elif isinstance(val, DeploymentAuthToken):
                obj[key] = val.deployment_token
            elif isinstance(val, AbstractApiClass):
                obj[key] = getattr(val, 'id', None)
            elif callable(val):
                try:
                    obj[key] = inspect.getsource(val)
                except OSError:
                    raise OSError(
                        f'Could not get source for function {key}. Please pass a stringified version of this function when the function is defined in a shell environment.')

    def _call_api(
            self, action, method, query_params=None,
            body=None, files=None, parse_type=None, streamable_response=False, server_override=None):
        headers = {'apiKey': self.api_key, 'clientVersion': self.client_version,
                   'User-Agent': f'python-abacusai-{self.client_version}'}
        url = (server_override or self.server) + '/api/v0/' + action
        self._clean_api_objects(query_params)
        self._clean_api_objects(body)
        if self.service_discovery_url and query_params and 'deploymentId' in query_params and 'deploymentToken' in query_params:
            discovered_url = _discover_service_url(
                self.service_discovery_url, self.client_version, query_params['deploymentId'], query_params['deploymentToken'])
            if discovered_url:
                url = discovered_url + '/api/' + action
        response = self._request(url, method, query_params=query_params,
                                 headers=headers, body=body, files=files, stream=streamable_response)

        result = None
        success = False
        error_message = None
        error_type = None
        if streamable_response and response.status_code == 200:
            return response.raw
        try:
            json_data = response.json()
            success = json_data['success']
            error_message = json_data.get('error')
            error_type = json_data.get('errorType')
            result = json_data.get('result')
            if success and parse_type:
                result = self._build_class(parse_type, result)
        except Exception:
            error_message = response.text
        if not success:
            if response.status_code == 504:
                error_message = 'Gateway timeout, please try again later'
            elif response.status_code > 502 and response.status_code not in (501, 503):
                error_message = 'Internal Server Error, please contact dev@abacus.ai for support'
            elif response.status_code == 404 and not self.client_options.exception_on_404:
                return None
            raise ApiException(error_message, response.status_code, error_type)
        return result

    def _build_class(self, return_class, values):
        if values is None or values == {}:
            return None
        if isinstance(values, list):
            return [self._build_class(return_class, val) for val in values if val is not None]
        type_inputs = inspect.signature(return_class.__init__).parameters
        return return_class(self, **{key: val for key, val in values.items() if key in type_inputs})

    def _request(self, url, method, query_params=None, headers=None,
                 body=None, files=None, stream=False):
        if method == 'GET':
            return _requests_retry_session().get(url, params=query_params, headers=headers, stream=stream)
        elif method == 'POST':
            return _requests_retry_session().post(url, params=query_params, json=body, headers=headers, files=files, timeout=90)
        elif method == 'PUT':
            return _requests_retry_session().put(url, params=query_params, data=body, headers=headers, files=files, timeout=90)
        elif method == 'PATCH':
            return _requests_retry_session().patch(url, params=query_params, json=body, headers=headers, files=files, timeout=90)
        elif method == 'DELETE':
            return _requests_retry_session().delete(url, params=query_params, data=body, headers=headers)
        else:
            raise ValueError(
                'HTTP method must be `GET`, `POST`, `PATCH`, `PUT` or `DELETE`'
            )

    def _poll(self, obj, wait_states: set, delay: int = 5, timeout: int = 300, poll_args: dict = {}):
        start_time = time.time()
        while obj.get_status(**poll_args) in wait_states:
            if timeout and time.time() - start_time > timeout:
                raise TimeoutError(f'Maximum wait time of {timeout}s exceeded')
            time.sleep(delay)
        return obj.refresh()

    def _upload_from_df(self, upload, df):
        with io.StringIO(df.to_csv(index=bool(any(df.index.names)), float_format='%.7f')) as csv_out:
            return upload.upload_file(csv_out)


class ApiClient(BaseApiClient):

    def create_dataset_from_pandas(self, feature_group_table_name: str, df: pd.DataFrame, name: str = None) -> Dataset:
        """
        Creates a Dataset from a pandas dataframe
        """
        upload = self.create_dataset_from_upload(
            name=name or feature_group_table_name, table_name=feature_group_table_name, file_format='CSV')
        return self._upload_from_df(upload, df)

    def create_dataset_version_from_pandas(self, table_name_or_id: str, df: pd.DataFrame) -> Dataset:
        """
        Updates an existing dataset from a pandas dataframe
        """
        dataset_id = None
        try:
            self.describe_dataset(table_name_or_id)
            dataset_id = table_name_or_id
        except ApiException:
            pass
        if not dataset_id:
            feature_group = self.describe_feature_group_by_table_name(
                table_name_or_id)
            if feature_group.feature_group_source_type != 'DATASET':
                raise ApiException(
                    'Feature Group is not source type DATASET', 409, 'ConflictError')
            dataset_id = feature_group.dataset_id
        upload = self.create_dataset_version_from_upload(dataset_id)
        return self._upload_from_df(upload, df)

    def create_model_from_functions(self, project_id: str, train_function: callable, predict_function: callable, training_input_tables: list = None):
        function_source_code = inspect.getsource(
            train_function) + '\n\n' + inspect.getsource(predict_function)
        return self.create_model_from_python(project_id=project_id, function_source_code=function_source_code, train_function_name=train_function.__name__, predict_function_name=predict_function.__name__, training_input_tables=training_input_tables)

    def add_user_to_organization(self, email: str):
        '''Invites a user to your organization. This method will send the specified email address an invitation link to join your organization.'''
        return self._call_api('addUserToOrganization', 'POST', query_params={}, body={'email': email})

    def list_api_keys(self) -> List[ApiKey]:
        '''Lists all of the user's API keys the user's organization.'''
        return self._call_api('listApiKeys', 'GET', query_params={}, parse_type=ApiKey)

    def list_organization_users(self) -> List[User]:
        '''Retrieves a list of all users in the organization.

        This method will retrieve a list containing all the users in the organization. The list includes pending users who have been invited to the organization.
        '''
        return self._call_api('listOrganizationUsers', 'GET', query_params={}, parse_type=User)

    def describe_user(self) -> User:
        '''Get the current user's information, such as their name, email, admin status, etc.'''
        return self._call_api('describeUser', 'GET', query_params={}, parse_type=User)

    def list_organization_groups(self) -> List[OrganizationGroup]:
        '''Lists all Organizations Groups within this Organization'''
        return self._call_api('listOrganizationGroups', 'GET', query_params={}, parse_type=OrganizationGroup)

    def create_organization_group(self, group_name: str, permissions: list, default_group: bool = False) -> OrganizationGroup:
        '''Creates a new Organization Group.'''
        return self._call_api('createOrganizationGroup', 'POST', query_params={}, body={'groupName': group_name, 'permissions': permissions, 'defaultGroup': default_group}, parse_type=OrganizationGroup)

    def describe_organization_group(self, organization_group_id: str) -> OrganizationGroup:
        '''Returns the specific organization group passes in by the user.'''
        return self._call_api('describeOrganizationGroup', 'GET', query_params={'organizationGroupId': organization_group_id}, parse_type=OrganizationGroup)

    def add_organization_group_permission(self, organization_group_id: str, permission: str):
        '''Adds a permission to the specified Organization Group'''
        return self._call_api('addOrganizationGroupPermission', 'POST', query_params={}, body={'organizationGroupId': organization_group_id, 'permission': permission})

    def remove_organization_group_permission(self, organization_group_id: str, permission: str):
        '''Removes a permission from the specified Organization Group'''
        return self._call_api('removeOrganizationGroupPermission', 'POST', query_params={}, body={'organizationGroupId': organization_group_id, 'permission': permission})

    def delete_organization_group(self, organization_group_id: str):
        '''Deletes the specified Organization Group from the organization.'''
        return self._call_api('deleteOrganizationGroup', 'DELETE', query_params={'organizationGroupId': organization_group_id})

    def add_user_to_organization_group(self, organization_group_id: str, email: str):
        '''Adds a user to the specified Organization Group'''
        return self._call_api('addUserToOrganizationGroup', 'POST', query_params={}, body={'organizationGroupId': organization_group_id, 'email': email})

    def remove_user_from_organization_group(self, organization_group_id: str, email: str):
        '''Removes a user from an Organization Group'''
        return self._call_api('removeUserFromOrganizationGroup', 'DELETE', query_params={'organizationGroupId': organization_group_id, 'email': email})

    def set_default_organization_group(self, organization_group_id: str):
        '''Sets the default Organization Group that all new users that join an organization are automatically added to'''
        return self._call_api('setDefaultOrganizationGroup', 'POST', query_params={}, body={'organizationGroupId': organization_group_id})

    def delete_api_key(self, api_key_id: str):
        '''Delete a specified API Key. You can use the "listApiKeys" method to find the list of all API Key IDs.'''
        return self._call_api('deleteApiKey', 'DELETE', query_params={'apiKeyId': api_key_id})

    def remove_user_from_organization(self, email: str):
        '''Removes the specified user from the Organization. You can remove yourself, Otherwise you must be an Organization Administrator to use this method to remove other users from the organization.'''
        return self._call_api('removeUserFromOrganization', 'DELETE', query_params={'email': email})

    def create_project(self, name: str, use_case: str) -> Project:
        '''Creates a project with your specified project name and use case. Creating a project creates a container for all of the datasets and the models that are associated with a particular problem/project that you would like to work on. For example, if you want to create a model to detect fraud, you have to first create a project, upload datasets, create feature groups, and then create one or more models to get predictions for your use case.'''
        return self._call_api('createProject', 'POST', query_params={}, body={'name': name, 'useCase': use_case}, parse_type=Project)

    def list_use_cases(self) -> List[UseCase]:
        '''Retrieves a list of all use cases with descriptions. Use the given mappings to specify a use case when needed.'''
        return self._call_api('listUseCases', 'GET', query_params={}, parse_type=UseCase)

    def describe_use_case_requirements(self, use_case: str) -> UseCaseRequirements:
        '''This API call returns the feature requirements for a specified use case'''
        return self._call_api('describeUseCaseRequirements', 'GET', query_params={'useCase': use_case}, parse_type=UseCaseRequirements)

    def describe_project(self, project_id: str) -> Project:
        '''Returns a description of a project.'''
        return self._call_api('describeProject', 'GET', query_params={'projectId': project_id}, parse_type=Project)

    def list_projects(self, limit: int = 100, start_after_id: str = None) -> List[Project]:
        '''Retrieves a list of all projects in the current organization.'''
        return self._call_api('listProjects', 'GET', query_params={'limit': limit, 'startAfterId': start_after_id}, parse_type=Project)

    def list_project_datasets(self, project_id: str) -> List[ProjectDataset]:
        '''Retrieves all dataset(s) attached to a specified project. This API returns all attributes of each dataset, such as its name, type, and ID.'''
        return self._call_api('listProjectDatasets', 'GET', query_params={'projectId': project_id}, parse_type=ProjectDataset)

    def get_schema(self, project_id: str, dataset_id: str) -> List[Schema]:
        '''[DEPRECATED] Returns a schema given a specific dataset in a project. The schema of the dataset consists of the columns in the dataset, the data type of the column, and the column's column mapping.'''
        logging.warning(
            'This function (getSchema) is deprecated and will be removed in a future version. Use get_dataset_schema instead.')
        return self._call_api('getSchema', 'GET', query_params={'projectId': project_id, 'datasetId': dataset_id}, parse_type=Schema)

    def rename_project(self, project_id: str, name: str):
        '''This method renames a project after it is created.'''
        return self._call_api('renameProject', 'PATCH', query_params={}, body={'projectId': project_id, 'name': name})

    def delete_project(self, project_id: str):
        '''Deletes a specified project from your organization.

        This method deletes the project, trained models and deployments in the specified project. The datasets attached to the specified project remain available for use with other projects in the organization.

        This method will not delete a project that contains active deployments. Be sure to stop all active deployments before you use the delete option.

        Note: All projects, models, and deployments cannot be recovered once they are deleted.
        '''
        return self._call_api('deleteProject', 'DELETE', query_params={'projectId': project_id})

    def add_feature_group_to_project(self, feature_group_id: str, project_id: str, feature_group_type: str = 'CUSTOM_TABLE', feature_group_use: str = None):
        '''Adds a feature group to a project,'''
        return self._call_api('addFeatureGroupToProject', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'projectId': project_id, 'featureGroupType': feature_group_type, 'featureGroupUse': feature_group_use})

    def remove_feature_group_from_project(self, feature_group_id: str, project_id: str):
        '''Removes a feature group from a project.'''
        return self._call_api('removeFeatureGroupFromProject', 'DELETE', query_params={'featureGroupId': feature_group_id, 'projectId': project_id})

    def set_feature_group_type(self, feature_group_id: str, project_id: str, feature_group_type: str = 'CUSTOM_TABLE'):
        '''Update the feature group type in a project. The feature group must already be added to the project.'''
        return self._call_api('setFeatureGroupType', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'projectId': project_id, 'featureGroupType': feature_group_type})

    def use_feature_group_for_training(self, feature_group_id: str, project_id: str, use_for_training: bool = True):
        '''Use the feature group for model training input'''
        return self._call_api('useFeatureGroupForTraining', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'projectId': project_id, 'useForTraining': use_for_training})

    def set_feature_mapping(self, project_id: str, feature_group_id: str, feature_name: str, feature_mapping: str, nested_column_name: str = None) -> List[Feature]:
        '''Set a column's feature mapping. If the column mapping is single-use and already set in another column in this feature group, this call will first remove the other column's mapping and move it to this column.'''
        return self._call_api('setFeatureMapping', 'POST', query_params={}, body={'projectId': project_id, 'featureGroupId': feature_group_id, 'featureName': feature_name, 'featureMapping': feature_mapping, 'nestedColumnName': nested_column_name}, parse_type=Feature)

    def validate_project(self, project_id: str) -> ProjectValidation:
        '''Validates that the specified project has all required feature group types for its use case and that all required feature columns are set.'''
        return self._call_api('validateProject', 'GET', query_params={'projectId': project_id}, parse_type=ProjectValidation)

    def set_column_data_type(self, project_id: str, dataset_id: str, column: str, data_type: str) -> List[Schema]:
        '''Set a dataset's column type.'''
        return self._call_api('setColumnDataType', 'POST', query_params={'datasetId': dataset_id}, body={'projectId': project_id, 'column': column, 'dataType': data_type}, parse_type=Schema)

    def set_column_mapping(self, project_id: str, dataset_id: str, column: str, column_mapping: str) -> List[Schema]:
        '''Set a dataset's column mapping. If the column mapping is single-use and already set in another column in this dataset, this call will first remove the other column's mapping and move it to this column.'''
        return self._call_api('setColumnMapping', 'POST', query_params={'datasetId': dataset_id}, body={'projectId': project_id, 'column': column, 'columnMapping': column_mapping}, parse_type=Schema)

    def remove_column_mapping(self, project_id: str, dataset_id: str, column: str) -> List[Schema]:
        '''Removes a column mapping from a column in the dataset. Returns a list of all columns with their mappings once the change is made.'''
        return self._call_api('removeColumnMapping', 'DELETE', query_params={'projectId': project_id, 'datasetId': dataset_id, 'column': column}, parse_type=Schema)

    def create_feature_group(self, table_name: str, sql: str, description: str = None) -> FeatureGroup:
        '''Creates a new feature group from a SQL statement.'''
        return self._call_api('createFeatureGroup', 'POST', query_params={}, body={'tableName': table_name, 'sql': sql, 'description': description}, parse_type=FeatureGroup)

    def create_feature_group_from_function(self, table_name: str, function_source_code: str, function_name: str, input_feature_groups: list = [], description: str = None) -> FeatureGroup:
        '''Creates a new feature in a Feature Group from user provided code. Code language currently supported is Python.

        If a list of input feature groups are supplied, we will provide as arguments to the function DataFrame's
        (pandas in the case of Python) with the materialized feature groups for those input feature groups.

        This method expects `function_source_code to be a valid language source file which contains a function named
        `function_name`. This function needs return a DataFrame when it is executed and this DataFrame will be used
        as the materialized version of this feature group table.
        '''
        return self._call_api('createFeatureGroupFromFunction', 'POST', query_params={}, body={'tableName': table_name, 'functionSourceCode': function_source_code, 'functionName': function_name, 'inputFeatureGroups': input_feature_groups, 'description': description}, parse_type=FeatureGroup)

    def create_sampling_feature_group(self, feature_group_id: str, table_name: str, sampling_config: dict, description: str = None) -> FeatureGroup:
        '''Creates a new feature group defined as a sample of rows from another feature group.

        For efficiency, sampling is approximate unless otherwise specified. (E.g. the number of rows may vary slightly from what was requested).
        '''
        return self._call_api('createSamplingFeatureGroup', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'tableName': table_name, 'samplingConfig': sampling_config, 'description': description}, parse_type=FeatureGroup)

    def create_merge_feature_group(self, source_feature_group_id: str, table_name: str, merge_config: dict, description: str = None) -> FeatureGroup:
        '''Creates a new feature group defined as the union of other feature group versions.'''
        return self._call_api('createMergeFeatureGroup', 'POST', query_params={}, body={'sourceFeatureGroupId': source_feature_group_id, 'tableName': table_name, 'mergeConfig': merge_config, 'description': description}, parse_type=FeatureGroup)

    def set_feature_group_sampling_config(self, feature_group_id: str, sampling_config: dict) -> FeatureGroup:
        '''Set a FeatureGroup’s sampling to the config values provided, so that the rows the FeatureGroup returns will be a sample of those it would otherwise have returned.

        Currently, sampling is only for Sampling FeatureGroups, so this API only allows calling on that kind of FeatureGroup.
        '''
        return self._call_api('setFeatureGroupSamplingConfig', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'samplingConfig': sampling_config}, parse_type=FeatureGroup)

    def set_feature_group_merge_config(self, feature_group_id: str, merge_config: dict) -> None:
        '''Set a MergeFeatureGroup’s merge config to the values provided, so that the feature group only returns a bounded range of an incremental dataset.'''
        return self._call_api('setFeatureGroupMergeConfig', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'mergeConfig': merge_config})

    def set_feature_group_schema(self, feature_group_id: str, schema: list):
        '''Creates a new schema and points the feature group to the new feature group schema id.'''
        return self._call_api('setFeatureGroupSchema', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'schema': schema})

    def get_feature_group_schema(self, feature_group_id: str, project_id: str = None) -> List[Feature]:
        '''Returns a schema given a specific FeatureGroup in a project.'''
        return self._call_api('getFeatureGroupSchema', 'GET', query_params={'featureGroupId': feature_group_id, 'projectId': project_id}, parse_type=Feature)

    def create_feature(self, feature_group_id: str, name: str, select_expression: str) -> FeatureGroup:
        '''Creates a new feature in a Feature Group from a SQL select statement'''
        return self._call_api('createFeature', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'name': name, 'selectExpression': select_expression}, parse_type=FeatureGroup)

    def add_feature_group_tag(self, feature_group_id: str, tag: str):
        '''Adds a tag to the feature group'''
        return self._call_api('addFeatureGroupTag', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'tag': tag})

    def remove_feature_group_tag(self, feature_group_id: str, tag: str):
        '''Removes a tag from the feature group'''
        return self._call_api('removeFeatureGroupTag', 'DELETE', query_params={'featureGroupId': feature_group_id, 'tag': tag})

    def create_nested_feature(self, feature_group_id: str, nested_feature_name: str, table_name: str, using_clause: str, where_clause: str = None, order_clause: str = None) -> FeatureGroup:
        '''Creates a new nested feature in a feature group from a SQL statements to create a new nested feature.'''
        return self._call_api('createNestedFeature', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'nestedFeatureName': nested_feature_name, 'tableName': table_name, 'usingClause': using_clause, 'whereClause': where_clause, 'orderClause': order_clause}, parse_type=FeatureGroup)

    def update_nested_feature(self, feature_group_id: str, nested_feature_name: str, table_name: str = None, using_clause: str = None, where_clause: str = None, order_clause: str = None, new_nested_feature_name: str = None) -> FeatureGroup:
        '''Updates a previously existing nested feature in a feature group.'''
        return self._call_api('updateNestedFeature', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'nestedFeatureName': nested_feature_name, 'tableName': table_name, 'usingClause': using_clause, 'whereClause': where_clause, 'orderClause': order_clause, 'newNestedFeatureName': new_nested_feature_name}, parse_type=FeatureGroup)

    def delete_nested_feature(self, feature_group_id: str, nested_feature_name: str) -> FeatureGroup:
        '''Delete a nested feature.'''
        return self._call_api('deleteNestedFeature', 'DELETE', query_params={'featureGroupId': feature_group_id, 'nestedFeatureName': nested_feature_name}, parse_type=FeatureGroup)

    def create_point_in_time_feature(self, feature_group_id: str, feature_name: str, history_table_name: str = None, aggregation_keys: list = None, timestamp_key: str = None, historical_timestamp_key: str = None, lookback_window_seconds: float = None, lookback_window_lag_seconds: float = 0, lookback_count: int = None, lookback_until_position: int = 0, expression: str = None) -> FeatureGroup:
        '''Creates a new point in time feature in a feature group using another historical feature group, window spec and aggregate expression.

        We use the aggregation keys, and either the lookbackWindowSeconds or the lookbackCount values to perform the window aggregation for every row in the current feature group.
        If the window is specified in seconds, then all rows in the history table which match the aggregation keys and with historicalTimeFeature >= lookbackStartCount and < the value
        of the current rows timeFeature are considered. An option lookbackWindowLagSeconds (+ve or -ve) can be used to offset the current value of the timeFeature. If this value
        is negative, we will look at the future rows in the history table, so care must be taken to make sure that these rows are available in the online context when we are performing
        a lookup on this feature group. If window is specified in counts, then we order the historical table rows aligning by time and consider rows from the window where
        the rank order is >= lookbackCount and includes the row just prior to the current one. The lag is specified in term of positions using lookbackUntilPosition.
        '''
        return self._call_api('createPointInTimeFeature', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'featureName': feature_name, 'historyTableName': history_table_name, 'aggregationKeys': aggregation_keys, 'timestampKey': timestamp_key, 'historicalTimestampKey': historical_timestamp_key, 'lookbackWindowSeconds': lookback_window_seconds, 'lookbackWindowLagSeconds': lookback_window_lag_seconds, 'lookbackCount': lookback_count, 'lookbackUntilPosition': lookback_until_position, 'expression': expression}, parse_type=FeatureGroup)

    def update_point_in_time_feature(self, feature_group_id: str, feature_name: str, history_table_name: str = None, aggregation_keys: list = None, timestamp_key: str = None, historical_timestamp_key: str = None, lookback_window_seconds: float = None, lookback_window_lag_seconds: float = None, lookback_count: int = None, lookback_until_position: int = None, expression: str = None, new_feature_name: str = None) -> FeatureGroup:
        '''Updates an existing point in time feature in a feature group. See createPointInTimeFeature for detailed semantics.'''
        return self._call_api('updatePointInTimeFeature', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'featureName': feature_name, 'historyTableName': history_table_name, 'aggregationKeys': aggregation_keys, 'timestampKey': timestamp_key, 'historicalTimestampKey': historical_timestamp_key, 'lookbackWindowSeconds': lookback_window_seconds, 'lookbackWindowLagSeconds': lookback_window_lag_seconds, 'lookbackCount': lookback_count, 'lookbackUntilPosition': lookback_until_position, 'expression': expression, 'newFeatureName': new_feature_name}, parse_type=FeatureGroup)

    def set_feature_type(self, feature_group_id: str, feature: str, feature_type: str) -> Schema:
        '''Set a feature's type in a feature group/. Specify the feature group ID, feature name and feature type, and the method will return the new column with the resulting changes reflected.'''
        return self._call_api('setFeatureType', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'feature': feature, 'featureType': feature_type}, parse_type=Schema)

    def invalidate_streaming_feature_group_data(self, feature_group_id: str, invalid_before_timestamp: int):
        '''Invalidates all streaming data with timestamp before invalidBeforeTimestamp'''
        return self._call_api('invalidateStreamingFeatureGroupData', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'invalidBeforeTimestamp': invalid_before_timestamp})

    def concatenate_feature_group_data(self, feature_group_id: str, source_feature_group_id: str, merge_type: str = 'UNION', replace_until_timestamp: int = None, skip_materialize: bool = False):
        '''Concatenates data from one feature group to another. Feature groups can be merged if their schema's are compatible and they have the special updateTimestampKey column and if set, the primaryKey column. The second operand in the concatenate operation will be appended to the first operand (merge target).'''
        return self._call_api('concatenateFeatureGroupData', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'sourceFeatureGroupId': source_feature_group_id, 'mergeType': merge_type, 'replaceUntilTimestamp': replace_until_timestamp, 'skipMaterialize': skip_materialize})

    def describe_feature_group(self, feature_group_id: str) -> FeatureGroup:
        '''Describe a Feature Group.'''
        return self._call_api('describeFeatureGroup', 'GET', query_params={'featureGroupId': feature_group_id}, parse_type=FeatureGroup)

    def describe_feature_group_by_table_name(self, table_name: str) -> FeatureGroup:
        '''Describe a Feature Group by the feature group's table name'''
        return self._call_api('describeFeatureGroupByTableName', 'GET', query_params={'tableName': table_name}, parse_type=FeatureGroup)

    def set_feature_group_indexing_config(self, feature_group_id: str, primary_key: str = None, update_timestamp_key: str = None, lookup_keys: list = None):
        '''Sets various attributes of the feature group used for deployment lookups and streaming updates.'''
        return self._call_api('setFeatureGroupIndexingConfig', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'primaryKey': primary_key, 'updateTimestampKey': update_timestamp_key, 'lookupKeys': lookup_keys})

    def list_feature_groups(self, limit: int = 100, start_after_id: str = None) -> List[FeatureGroup]:
        '''Enlist all the feature groups associated with a project. A user needs to specify the unique project ID to fetch all attached feature groups.'''
        return self._call_api('listFeatureGroups', 'GET', query_params={'limit': limit, 'startAfterId': start_after_id}, parse_type=FeatureGroup)

    def list_project_feature_groups(self, project_id: str, filter_feature_group_use: str = None) -> FeatureGroup:
        '''List all the feature groups associated with a project'''
        return self._call_api('listProjectFeatureGroups', 'GET', query_params={'projectId': project_id, 'filterFeatureGroupUse': filter_feature_group_use}, parse_type=FeatureGroup)

    def update_feature_group(self, feature_group_id: str, description: str = None) -> FeatureGroup:
        '''Modifies an existing feature group'''
        return self._call_api('updateFeatureGroup', 'PATCH', query_params={}, body={'featureGroupId': feature_group_id, 'description': description}, parse_type=FeatureGroup)

    def update_feature_group_sql_definition(self, feature_group_id: str, sql: str) -> FeatureGroup:
        '''Updates the SQL statement for a feature group.'''
        return self._call_api('updateFeatureGroupSqlDefinition', 'PATCH', query_params={}, body={'featureGroupId': feature_group_id, 'sql': sql}, parse_type=FeatureGroup)

    def update_feature_group_function_definition(self, feature_group_id: str, function_source_code: str = None, function_name: str = None, input_feature_groups: list = None) -> FeatureGroup:
        '''Updates the function definition for a feature group created using createFeatureGroupFromFunction'''
        return self._call_api('updateFeatureGroupFunctionDefinition', 'PATCH', query_params={}, body={'featureGroupId': feature_group_id, 'functionSourceCode': function_source_code, 'functionName': function_name, 'inputFeatureGroups': input_feature_groups}, parse_type=FeatureGroup)

    def update_feature(self, feature_group_id: str, name: str, select_expression: str = None, new_name: str = None) -> FeatureGroup:
        '''Modifies an existing feature in a feature group. A user needs to specify the name and feature group ID and either a SQL statement or new name tp update the feature.'''
        return self._call_api('updateFeature', 'PATCH', query_params={}, body={'featureGroupId': feature_group_id, 'name': name, 'selectExpression': select_expression, 'newName': new_name}, parse_type=FeatureGroup)

    def export_feature_group_version_to_file_connector(self, feature_group_version: str, location: str, export_file_format: str, overwrite: bool = False) -> FeatureGroupExport:
        '''Export Feature group to File Connector.'''
        return self._call_api('exportFeatureGroupVersionToFileConnector', 'POST', query_params={}, body={'featureGroupVersion': feature_group_version, 'location': location, 'exportFileFormat': export_file_format, 'overwrite': overwrite}, parse_type=FeatureGroupExport)

    def export_feature_group_version_to_database_connector(self, feature_group_version: str, database_connector_id: str, object_name: str, write_mode: str, database_feature_mapping: dict, id_column: str = None) -> FeatureGroupExport:
        '''Export Feature group to Database Connector.'''
        return self._call_api('exportFeatureGroupVersionToDatabaseConnector', 'POST', query_params={}, body={'featureGroupVersion': feature_group_version, 'databaseConnectorId': database_connector_id, 'objectName': object_name, 'writeMode': write_mode, 'databaseFeatureMapping': database_feature_mapping, 'idColumn': id_column}, parse_type=FeatureGroupExport)

    def describe_feature_group_export(self, feature_group_export_id: str) -> FeatureGroupExport:
        '''A feature group export'''
        return self._call_api('describeFeatureGroupExport', 'GET', query_params={'featureGroupExportId': feature_group_export_id}, parse_type=FeatureGroupExport)

    def list_feature_group_exports(self, feature_group_id: str) -> List[FeatureGroupExport]:
        '''Lists all of the feature group exports for a given feature group'''
        return self._call_api('listFeatureGroupExports', 'GET', query_params={'featureGroupId': feature_group_id}, parse_type=FeatureGroupExport)

    def set_feature_group_modifier_lock(self, feature_group_id: str, locked: bool = True):
        '''To lock a feature group to prevent it from being modified.'''
        return self._call_api('setFeatureGroupModifierLock', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'locked': locked})

    def list_feature_group_modifiers(self, feature_group_id: str) -> ModificationLockInfo:
        '''To list users who can modify a feature group.'''
        return self._call_api('listFeatureGroupModifiers', 'GET', query_params={'featureGroupId': feature_group_id}, parse_type=ModificationLockInfo)

    def add_user_to_feature_group_modifiers(self, feature_group_id: str, email: str):
        '''Adds user to a feature group.'''
        return self._call_api('addUserToFeatureGroupModifiers', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'email': email})

    def add_organization_group_to_feature_group_modifiers(self, feature_group_id: str, organization_group_id: str):
        '''Add Organization to a feature group.'''
        return self._call_api('addOrganizationGroupToFeatureGroupModifiers', 'POST', query_params={}, body={'featureGroupId': feature_group_id, 'organizationGroupId': organization_group_id})

    def remove_user_from_feature_group_modifiers(self, feature_group_id: str, email: str):
        '''Removes user from a feature group.'''
        return self._call_api('removeUserFromFeatureGroupModifiers', 'DELETE', query_params={'featureGroupId': feature_group_id, 'email': email})

    def remove_organization_group_from_feature_group_modifiers(self, feature_group_id: str, organization_group_id: str):
        '''Removes Organization from a feature group.'''
        return self._call_api('removeOrganizationGroupFromFeatureGroupModifiers', 'DELETE', query_params={'featureGroupId': feature_group_id, 'organizationGroupId': organization_group_id})

    def delete_feature(self, feature_group_id: str, name: str) -> FeatureGroup:
        '''Removes an existing feature from a feature group. A user needs to specify the name of the feature to be deleted and the feature group ID.'''
        return self._call_api('deleteFeature', 'DELETE', query_params={'featureGroupId': feature_group_id, 'name': name}, parse_type=FeatureGroup)

    def delete_feature_group(self, feature_group_id: str):
        '''Removes an existing feature group.'''
        return self._call_api('deleteFeatureGroup', 'DELETE', query_params={'featureGroupId': feature_group_id})

    def create_feature_group_version(self, feature_group_id: str) -> FeatureGroupVersion:
        '''Creates a snapshot for a specified feature group.'''
        return self._call_api('createFeatureGroupVersion', 'POST', query_params={}, body={'featureGroupId': feature_group_id}, parse_type=FeatureGroupVersion)

    def get_materialization_logs(self, feature_group_version: str, stdout: bool = False, stderr: bool = False) -> FunctionLogs:
        '''Returns logs for materialized feature group version.'''
        return self._call_api('getMaterializationLogs', 'GET', query_params={'featureGroupVersion': feature_group_version, 'stdout': stdout, 'stderr': stderr}, parse_type=FunctionLogs)

    def list_feature_group_versions(self, feature_group_id: str, limit: int = 100, start_after_version: str = None) -> List[FeatureGroupVersion]:
        '''Retrieves a list of all feature group versions for the specified feature group.'''
        return self._call_api('listFeatureGroupVersions', 'GET', query_params={'featureGroupId': feature_group_id, 'limit': limit, 'startAfterVersion': start_after_version}, parse_type=FeatureGroupVersion)

    def describe_feature_group_version(self, feature_group_version: str) -> FeatureGroupVersion:
        '''Get a specific feature group version.'''
        return self._call_api('describeFeatureGroupVersion', 'GET', query_params={'featureGroupVersion': feature_group_version}, parse_type=FeatureGroupVersion)

    def cancel_upload(self, upload_id: str):
        '''Cancels an upload'''
        return self._call_api('cancelUpload', 'DELETE', query_params={'uploadId': upload_id})

    def upload_part(self, upload_id: str, part_number: int, part_data: io.TextIOBase) -> UploadPart:
        '''Uploads a part of a large dataset file from your bucket to our system. Our system currently supports a size of up to 5GB for a part of a full file and a size of up to 5TB for the full file. Note that each part must be >=5MB in size, unless it is the last part in the sequence of parts for the full file.'''
        return self._call_api('uploadPart', 'POST', query_params={'uploadId': upload_id, 'partNumber': part_number}, parse_type=UploadPart, files={'partData': part_data})

    def mark_upload_complete(self, upload_id: str) -> Upload:
        '''Marks an upload process as complete.'''
        return self._call_api('markUploadComplete', 'POST', query_params={}, body={'uploadId': upload_id}, parse_type=Upload)

    def create_dataset_from_file_connector(self, name: str, table_name: str, location: str, file_format: str = None, refresh_schedule: str = None, csv_delimiter: str = None, filename_column: str = None, start_prefix: str = None, until_prefix: str = None, location_date_format: str = None, date_format_lookback_days: int = None, merge_config: dict = None) -> Dataset:
        '''Creates a dataset from a file located in a cloud storage, such as Amazon AWS S3, using the specified dataset name and location.'''
        return self._call_api('createDatasetFromFileConnector', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'location': location, 'fileFormat': file_format, 'refreshSchedule': refresh_schedule, 'csvDelimiter': csv_delimiter, 'filenameColumn': filename_column, 'startPrefix': start_prefix, 'untilPrefix': until_prefix, 'locationDateFormat': location_date_format, 'dateFormatLookbackDays': date_format_lookback_days, 'mergeConfig': merge_config}, parse_type=Dataset)

    def create_dataset_version_from_file_connector(self, dataset_id: str, location: str = None, file_format: str = None, csv_delimiter: str = None) -> DatasetVersion:
        '''Creates a new version of the specified dataset.'''
        return self._call_api('createDatasetVersionFromFileConnector', 'POST', query_params={'datasetId': dataset_id}, body={'location': location, 'fileFormat': file_format, 'csvDelimiter': csv_delimiter}, parse_type=DatasetVersion)

    def create_dataset_from_database_connector(self, name: str, table_name: str, database_connector_id: str, object_name: str = None, columns: str = None, query_arguments: str = None, refresh_schedule: str = None, sql_query: str = None) -> Dataset:
        '''Creates a dataset from a Database Connector'''
        return self._call_api('createDatasetFromDatabaseConnector', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'databaseConnectorId': database_connector_id, 'objectName': object_name, 'columns': columns, 'queryArguments': query_arguments, 'refreshSchedule': refresh_schedule, 'sqlQuery': sql_query}, parse_type=Dataset)

    def create_dataset_from_application_connector(self, name: str, table_name: str, application_connector_id: str, object_id: str = None, start_timestamp: int = None, end_timestamp: int = None, refresh_schedule: str = None) -> Dataset:
        '''Creates a dataset from an Application Connector'''
        return self._call_api('createDatasetFromApplicationConnector', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'applicationConnectorId': application_connector_id, 'objectId': object_id, 'startTimestamp': start_timestamp, 'endTimestamp': end_timestamp, 'refreshSchedule': refresh_schedule}, parse_type=Dataset)

    def create_dataset_version_from_database_connector(self, dataset_id: str, object_name: str = None, columns: str = None, query_arguments: str = None, sql_query: str = None) -> DatasetVersion:
        '''Creates a new version of the specified dataset'''
        return self._call_api('createDatasetVersionFromDatabaseConnector', 'POST', query_params={'datasetId': dataset_id}, body={'objectName': object_name, 'columns': columns, 'queryArguments': query_arguments, 'sqlQuery': sql_query}, parse_type=DatasetVersion)

    def create_dataset_version_from_application_connector(self, dataset_id: str, object_id: str = None, start_timestamp: int = None, end_timestamp: int = None) -> DatasetVersion:
        '''Creates a new version of the specified dataset'''
        return self._call_api('createDatasetVersionFromApplicationConnector', 'POST', query_params={'datasetId': dataset_id}, body={'objectId': object_id, 'startTimestamp': start_timestamp, 'endTimestamp': end_timestamp}, parse_type=DatasetVersion)

    def create_dataset_from_upload(self, name: str, table_name: str, file_format: str = None, csv_delimiter: str = None) -> Upload:
        '''Creates a dataset and return an upload Id that can be used to upload a file.'''
        return self._call_api('createDatasetFromUpload', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'fileFormat': file_format, 'csvDelimiter': csv_delimiter}, parse_type=Upload)

    def create_dataset_version_from_upload(self, dataset_id: str, file_format: str = None) -> Upload:
        '''Creates a new version of the specified dataset using a local file upload.'''
        return self._call_api('createDatasetVersionFromUpload', 'POST', query_params={'datasetId': dataset_id}, body={'fileFormat': file_format}, parse_type=Upload)

    def create_streaming_dataset(self, name: str, table_name: str, project_id: str = None, dataset_type: str = None) -> Dataset:
        '''Creates a streaming dataset. Use a streaming dataset if your dataset is receiving information from multiple sources over an extended period of time.'''
        return self._call_api('createStreamingDataset', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'projectId': project_id, 'datasetType': dataset_type}, parse_type=Dataset)

    def snapshot_streaming_data(self, dataset_id: str) -> DatasetVersion:
        '''Snapshots the current data in the streaming dataset for training.'''
        return self._call_api('snapshotStreamingData', 'POST', query_params={'datasetId': dataset_id}, body={}, parse_type=DatasetVersion)

    def set_dataset_column_data_type(self, dataset_id: str, column: str, data_type: str) -> Dataset:
        '''Set a column's type in a specified dataset.'''
        return self._call_api('setDatasetColumnDataType', 'POST', query_params={'datasetId': dataset_id}, body={'column': column, 'dataType': data_type}, parse_type=Dataset)

    def create_dataset_from_streaming_connector(self, name: str, table_name: str, streaming_connector_id: str, streaming_args: dict = None, refresh_schedule: str = None) -> Dataset:
        '''Creates a dataset from a Streaming Connector'''
        return self._call_api('createDatasetFromStreamingConnector', 'POST', query_params={}, body={'name': name, 'tableName': table_name, 'streamingConnectorId': streaming_connector_id, 'streamingArgs': streaming_args, 'refreshSchedule': refresh_schedule}, parse_type=Dataset)

    def set_streaming_retention_policy(self, dataset_id: str, retention_hours: int = None, retention_row_count: int = None):
        '''Sets the streaming retention policy'''
        return self._call_api('setStreamingRetentionPolicy', 'GET', query_params={'datasetId': dataset_id, 'retentionHours': retention_hours, 'retentionRowCount': retention_row_count})

    def get_dataset_schema(self, dataset_id: str) -> List[DatasetColumn]:
        '''Retrieves the column schema of a dataset'''
        return self._call_api('getDatasetSchema', 'GET', query_params={'datasetId': dataset_id}, parse_type=DatasetColumn)

    def get_file_connector_instructions(self, bucket: str, write_permission: bool = False) -> FileConnectorInstructions:
        '''Retrieves verification information to create a data connector to a cloud storage bucket.'''
        return self._call_api('getFileConnectorInstructions', 'GET', query_params={'bucket': bucket, 'writePermission': write_permission}, parse_type=FileConnectorInstructions)

    def list_database_connectors(self) -> DatabaseConnector:
        '''Retrieves a list of all of the database connectors along with all their attributes.'''
        return self._call_api('listDatabaseConnectors', 'GET', query_params={}, parse_type=DatabaseConnector)

    def list_file_connectors(self) -> List[FileConnector]:
        '''Retrieves a list of all connected services in the organization and their current verification status.'''
        return self._call_api('listFileConnectors', 'GET', query_params={}, parse_type=FileConnector)

    def list_database_connector_objects(self, database_connector_id: str) -> List[str]:
        '''Lists querable objects in the database connector.'''
        return self._call_api('listDatabaseConnectorObjects', 'GET', query_params={'databaseConnectorId': database_connector_id})

    def get_database_connector_object_schema(self, database_connector_id: str, object_name: str = None) -> List[str]:
        '''Get the schema of an object in an database connector.'''
        return self._call_api('getDatabaseConnectorObjectSchema', 'GET', query_params={'databaseConnectorId': database_connector_id, 'objectName': object_name})

    def rename_database_connector(self, database_connector_id: str, name: str):
        '''Renames a Database Connector'''
        return self._call_api('renameDatabaseConnector', 'PATCH', query_params={}, body={'databaseConnectorId': database_connector_id, 'name': name})

    def rename_application_connector(self, application_connector_id: str, name: str):
        '''Renames an Application Connector'''
        return self._call_api('renameApplicationConnector', 'PATCH', query_params={}, body={'applicationConnectorId': application_connector_id, 'name': name})

    def verify_database_connector(self, database_connector_id: str):
        '''Checks to see if Abacus.AI can access the database.'''
        return self._call_api('verifyDatabaseConnector', 'GET', query_params={'databaseConnectorId': database_connector_id})

    def verify_file_connector(self, bucket: str) -> FileConnectorVerification:
        '''Checks to see if Abacus.AI can access the bucket.'''
        return self._call_api('verifyFileConnector', 'POST', query_params={}, body={'bucket': bucket}, parse_type=FileConnectorVerification)

    def delete_database_connector(self, database_connector_id: str):
        '''Delete a database connector.'''
        return self._call_api('deleteDatabaseConnector', 'DELETE', query_params={'databaseConnectorId': database_connector_id})

    def delete_application_connector(self, application_connector_id: str):
        '''Delete a application connector.'''
        return self._call_api('deleteApplicationConnector', 'DELETE', query_params={'applicationConnectorId': application_connector_id})

    def delete_file_connector(self, bucket: str):
        '''Removes a connected service from the specified organization.'''
        return self._call_api('deleteFileConnector', 'DELETE', query_params={'bucket': bucket})

    def list_application_connectors(self) -> ApplicationConnector:
        '''Retrieves a list of all of the application connectors along with all their attributes.'''
        return self._call_api('listApplicationConnectors', 'GET', query_params={}, parse_type=ApplicationConnector)

    def list_application_connector_objects(self, application_connector_id: str) -> List[str]:
        '''Lists querable objects in the application connector.'''
        return self._call_api('listApplicationConnectorObjects', 'GET', query_params={'applicationConnectorId': application_connector_id})

    def verify_application_connector(self, application_connector_id: str):
        '''Checks to see if Abacus.AI can access the Application.'''
        return self._call_api('verifyApplicationConnector', 'GET', query_params={'applicationConnectorId': application_connector_id})

    def set_azure_blob_connection_string(self, bucket: str, connection_string: str) -> FileConnectorVerification:
        '''Authenticates specified Azure Blob Storage bucket using an authenticated Connection String.'''
        return self._call_api('setAzureBlobConnectionString', 'POST', query_params={}, body={'bucket': bucket, 'connectionString': connection_string}, parse_type=FileConnectorVerification)

    def list_streaming_connectors(self) -> StreamingConnector:
        '''Retrieves a list of all of the streaming connectors along with all their attributes.'''
        return self._call_api('listStreamingConnectors', 'GET', query_params={}, parse_type=StreamingConnector)

    def create_streaming_token(self) -> StreamingAuthToken:
        '''Creates a streaming token for the specified project. Streaming tokens are used to authenticate requests to append data to streaming datasets.'''
        return self._call_api('createStreamingToken', 'POST', query_params={}, body={}, parse_type=StreamingAuthToken)

    def list_streaming_tokens(self) -> List[StreamingAuthToken]:
        '''Retrieves a list of all streaming tokens along with their attributes.'''
        return self._call_api('listStreamingTokens', 'GET', query_params={}, parse_type=StreamingAuthToken)

    def delete_streaming_token(self, streaming_token: str):
        '''Deletes the specified streaming token.'''
        return self._call_api('deleteStreamingToken', 'DELETE', query_params={'streamingToken': streaming_token})

    def get_recent_feature_group_streamed_data(self, feature_group_id: str):
        '''Returns recently streamed data to a streaming feature group.'''
        return self._call_api('getRecentFeatureGroupStreamedData', 'GET', query_params={'featureGroupId': feature_group_id})

    def list_uploads(self) -> List[Upload]:
        '''Lists all ongoing uploads in the organization'''
        return self._call_api('listUploads', 'GET', query_params={}, parse_type=Upload)

    def describe_upload(self, upload_id: str) -> Upload:
        '''Retrieves the current upload status (complete or inspecting) and the list of file parts uploaded for a specified dataset upload.'''
        return self._call_api('describeUpload', 'GET', query_params={'uploadId': upload_id}, parse_type=Upload)

    def list_datasets(self, limit: int = 100, start_after_id: str = None, exclude_streaming: bool = False) -> List[Dataset]:
        '''Retrieves a list of all of the datasets in the organization.'''
        return self._call_api('listDatasets', 'GET', query_params={'limit': limit, 'startAfterId': start_after_id, 'excludeStreaming': exclude_streaming}, parse_type=Dataset)

    def describe_dataset(self, dataset_id: str) -> Dataset:
        '''Retrieves a full description of the specified dataset, with attributes such as its ID, name, source type, etc.'''
        return self._call_api('describeDataset', 'GET', query_params={'datasetId': dataset_id}, parse_type=Dataset)

    def list_dataset_versions(self, dataset_id: str, limit: int = 100, start_after_version: str = None) -> List[DatasetVersion]:
        '''Retrieves a list of all dataset versions for the specified dataset.'''
        return self._call_api('listDatasetVersions', 'GET', query_params={'datasetId': dataset_id, 'limit': limit, 'startAfterVersion': start_after_version}, parse_type=DatasetVersion)

    def attach_dataset_to_project(self, dataset_id: str, project_id: str, dataset_type: str) -> List[Schema]:
        '''[DEPRECATED] Attaches the dataset to the project.

        Use this method to attach a dataset that is already in the organization to another project. The dataset type is required to let the AI engine know what type of schema should be used.
        '''
        logging.warning(
            'This function (attachDatasetToProject) is deprecated and will be removed in a future version.')
        return self._call_api('attachDatasetToProject', 'POST', query_params={'datasetId': dataset_id}, body={'projectId': project_id, 'datasetType': dataset_type}, parse_type=Schema)

    def remove_dataset_from_project(self, dataset_id: str, project_id: str):
        '''[DEPRECATED] Removes a dataset from a project.'''
        logging.warning(
            'This function (removeDatasetFromProject) is deprecated and will be removed in a future version.')
        return self._call_api('removeDatasetFromProject', 'POST', query_params={'datasetId': dataset_id}, body={'projectId': project_id})

    def rename_dataset(self, dataset_id: str, name: str):
        '''Rename a dataset.'''
        return self._call_api('renameDataset', 'PATCH', query_params={'datasetId': dataset_id}, body={'name': name})

    def delete_dataset(self, dataset_id: str):
        '''Deletes the specified dataset from the organization.

        The dataset cannot be deleted if it is currently attached to a project.
        '''
        return self._call_api('deleteDataset', 'DELETE', query_params={'datasetId': dataset_id})

    def get_training_config_options(self, project_id: str) -> List[TrainingConfigOptions]:
        '''Retrieves the full description of the model training configuration options available for the specified project.

        The configuration options available are determined by the use case associated with the specified project. Refer to the (Use Case Documentation)[https://api.abacus.ai/app/help/useCases] for more information on use cases and use case specific configuration options.
        '''
        return self._call_api('getTrainingConfigOptions', 'GET', query_params={'projectId': project_id}, parse_type=TrainingConfigOptions)

    def train_model(self, project_id: str, name: str = None, training_config: dict = {}, refresh_schedule: str = None) -> Model:
        '''Trains a model for the specified project.

        Use this method to train a model in this project. This method supports user-specified training configurations defined in the getTrainingConfigOptions method.
        '''
        return self._call_api('trainModel', 'POST', query_params={}, body={'projectId': project_id, 'name': name, 'trainingConfig': training_config, 'refreshSchedule': refresh_schedule}, parse_type=Model)

    def create_model_from_python(self, project_id: str, function_source_code: str, train_function_name: str, predict_function_name: str, training_input_tables: list, name: str = None) -> Model:
        '''Initializes a new Model from user provided Python code. If a list of input feature groups are supplied,

        we will provide as arguments to the train and predict functions with the materialized feature groups for those
        input feature groups.

        This method expects `functionSourceCode` to be a valid language source file which contains the functions named
        `trainFunctionName` and `predictFunctionName`. `trainFunctionName` returns the ModelVersion that is the result of
        training the model using `trainFunctionName` and `predictFunctionName` has no well defined return type,
        as it returns the prediction made by the `predictFunctionName`, which can be anything
        '''
        return self._call_api('createModelFromPython', 'POST', query_params={}, body={'projectId': project_id, 'functionSourceCode': function_source_code, 'trainFunctionName': train_function_name, 'predictFunctionName': predict_function_name, 'trainingInputTables': training_input_tables, 'name': name}, parse_type=Model)

    def list_models(self, project_id: str) -> List[Model]:
        '''Retrieves the list of models in the specified project.'''
        return self._call_api('listModels', 'GET', query_params={'projectId': project_id}, parse_type=Model)

    def describe_model(self, model_id: str) -> Model:
        '''Retrieves a full description of the specified model.'''
        return self._call_api('describeModel', 'GET', query_params={'modelId': model_id}, parse_type=Model)

    def rename_model(self, model_id: str, name: str):
        '''Renames a model'''
        return self._call_api('renameModel', 'PATCH', query_params={}, body={'modelId': model_id, 'name': name})

    def update_python_model(self, model_id: str, function_source_code: str = None, train_function_name: str = None, predict_function_name: str = None, training_input_tables: list = None) -> Model:
        '''Updates an existing python Model using user provided Python code. If a list of input feature groups are supplied,

        we will provide as arguments to the train and predict functions with the materialized feature groups for those
        input feature groups.

        This method expects `functionSourceCode` to be a valid language source file which contains the functions named
        `trainFunctionName` and `predictFunctionName`. `trainFunctionName` returns the ModelVersion that is the result of
        training the model using `trainFunctionName` and `predictFunctionName` has no well defined return type,
        as it returns the prediction made by the `predictFunctionName`, which can be anything
        '''
        return self._call_api('updatePythonModel', 'POST', query_params={}, body={'modelId': model_id, 'functionSourceCode': function_source_code, 'trainFunctionName': train_function_name, 'predictFunctionName': predict_function_name, 'trainingInputTables': training_input_tables}, parse_type=Model)

    def set_model_training_config(self, model_id: str, training_config: dict) -> Model:
        '''Edits the default model training config'''
        return self._call_api('setModelTrainingConfig', 'PATCH', query_params={}, body={'modelId': model_id, 'trainingConfig': training_config}, parse_type=Model)

    def set_model_prediction_params(self, model_id: str, prediction_config: dict) -> Model:
        '''Sets the model prediction config for the model'''
        return self._call_api('setModelPredictionParams', 'PATCH', query_params={}, body={'modelId': model_id, 'predictionConfig': prediction_config}, parse_type=Model)

    def get_model_metrics(self, model_id: str, model_version: str = None, baseline_metrics: bool = False) -> ModelMetrics:
        '''Retrieves a full list of the metrics for the specified model.

        If only the model's unique identifier (modelId) is specified, the latest trained version of model (modelVersion) is used.
        '''
        return self._call_api('getModelMetrics', 'GET', query_params={'modelId': model_id, 'modelVersion': model_version, 'baselineMetrics': baseline_metrics}, parse_type=ModelMetrics)

    def list_model_versions(self, model_id: str, limit: int = 100, start_after_version: str = None) -> List[ModelVersion]:
        '''Retrieves a list of the version for a given model.'''
        return self._call_api('listModelVersions', 'GET', query_params={'modelId': model_id, 'limit': limit, 'startAfterVersion': start_after_version}, parse_type=ModelVersion)

    def retrain_model(self, model_id: str, deployment_ids: list = []) -> Model:
        '''Retrains the specified model. Gives you an option to choose the deployments you want the retraining to be deployed to.'''
        return self._call_api('retrainModel', 'POST', query_params={}, body={'modelId': model_id, 'deploymentIds': deployment_ids}, parse_type=Model)

    def delete_model(self, model_id: str):
        '''Deletes the specified model and all its versions. Models which are currently used in deployments cannot be deleted.'''
        return self._call_api('deleteModel', 'DELETE', query_params={'modelId': model_id})

    def delete_model_version(self, model_version: str):
        '''Deletes the specified model version. Model Versions which are currently used in deployments cannot be deleted.'''
        return self._call_api('deleteModelVersion', 'DELETE', query_params={'modelVersion': model_version})

    def describe_model_version(self, model_version: str) -> ModelVersion:
        '''Retrieves a full description of the specified model version'''
        return self._call_api('describeModelVersion', 'GET', query_params={'modelVersion': model_version}, parse_type=ModelVersion)

    def get_training_logs(self, model_version: str, stdout: bool = False, stderr: bool = False) -> FunctionLogs:
        '''Returns training logs for the model.'''
        return self._call_api('getTrainingLogs', 'GET', query_params={'modelVersion': model_version, 'stdout': stdout, 'stderr': stderr}, parse_type=FunctionLogs)

    def create_model_monitor(self, project_id: str, training_feature_group_id: str = None, prediction_feature_group_id: str = None, name: str = None, refresh_schedule: str = None) -> ModelMonitor:
        '''Runs a model monitor for the specified project.'''
        return self._call_api('createModelMonitor', 'POST', query_params={}, body={'projectId': project_id, 'trainingFeatureGroupId': training_feature_group_id, 'predictionFeatureGroupId': prediction_feature_group_id, 'name': name, 'refreshSchedule': refresh_schedule}, parse_type=ModelMonitor)

    def rerun_model_monitor(self, model_monitor_id: str) -> ModelMonitor:
        '''Reruns the specified model monitor.'''
        return self._call_api('rerunModelMonitor', 'POST', query_params={}, body={'modelMonitorId': model_monitor_id}, parse_type=ModelMonitor)

    def list_model_monitors(self, project_id: str) -> List[ModelMonitor]:
        '''Retrieves the list of models monitors in the specified project.'''
        return self._call_api('listModelMonitors', 'GET', query_params={'projectId': project_id}, parse_type=ModelMonitor)

    def describe_model_monitor(self, model_monitor_id: str) -> ModelMonitor:
        '''Retrieves a full description of the specified model monitor.'''
        return self._call_api('describeModelMonitor', 'GET', query_params={'modelMonitorId': model_monitor_id}, parse_type=ModelMonitor)

    def list_model_monitor_versions(self, model_monitor_id: str, limit: int = 100, start_after_version: str = None) -> List[ModelMonitorVersion]:
        '''Retrieves a list of the versions for a given model monitor.'''
        return self._call_api('listModelMonitorVersions', 'GET', query_params={'modelMonitorId': model_monitor_id, 'limit': limit, 'startAfterVersion': start_after_version}, parse_type=ModelMonitorVersion)

    def describe_model_monitor_version(self, model_monitor_version: str) -> ModelMonitorVersion:
        '''Retrieves a full description of the specified model monitor version'''
        return self._call_api('describeModelMonitorVersion', 'GET', query_params={'modelMonitorVersion': model_monitor_version}, parse_type=ModelMonitorVersion)

    def rename_model_monitor(self, model_monitor_id: str, name: str):
        '''Renames a model monitor'''
        return self._call_api('renameModelMonitor', 'PATCH', query_params={}, body={'modelMonitorId': model_monitor_id, 'name': name})

    def delete_model_monitor(self, model_monitor_id: str):
        '''Deletes the specified model monitor and all its versions.'''
        return self._call_api('deleteModelMonitor', 'DELETE', query_params={'modelMonitorId': model_monitor_id})

    def delete_model_monitor_version(self, model_monitor_version: str):
        '''Deletes the specified model monitor version.'''
        return self._call_api('deleteModelMonitorVersion', 'DELETE', query_params={'modelMonitorVersion': model_monitor_version})

    def get_model_monitoring_logs(self, model_monitor_version: str, stdout: bool = False, stderr: bool = False) -> FunctionLogs:
        '''Returns monitoring logs for the model.'''
        return self._call_api('getModelMonitoringLogs', 'GET', query_params={'modelMonitorVersion': model_monitor_version, 'stdout': stdout, 'stderr': stderr}, parse_type=FunctionLogs)

    def get_drift_for_feature(self, model_monitor_version: str, feature_name: str) -> Dict:
        '''Gets the feature drift associated with a single feature in an output feature group from a prediction.'''
        return self._call_api('getDriftForFeature', 'GET', query_params={'modelMonitorVersion': model_monitor_version, 'featureName': feature_name})

    def get_outliers_for_feature(self, model_monitor_version: str, feature_name: str = None) -> Dict:
        '''Gets a list of outliers measured by a single feature (or overall) in an output feature group from a prediction.'''
        return self._call_api('getOutliersForFeature', 'GET', query_params={'modelMonitorVersion': model_monitor_version, 'featureName': feature_name})

    def create_deployment(self, name: str = None, model_id: str = None, feature_group_id: str = None, project_id: str = None, description: str = None, calls_per_second: int = None, auto_deploy: bool = True, start: bool = True) -> Deployment:
        '''Creates a deployment with the specified name and description for the specified model or feature group.

        A Deployment makes the trained model or feature group available for prediction requests.
        '''
        return self._call_api('createDeployment', 'POST', query_params={}, body={'name': name, 'modelId': model_id, 'featureGroupId': feature_group_id, 'projectId': project_id, 'description': description, 'callsPerSecond': calls_per_second, 'autoDeploy': auto_deploy, 'start': start}, parse_type=Deployment)

    def create_deployment_token(self, project_id: str) -> DeploymentAuthToken:
        '''Creates a deployment token for the specified project.

        Deployment tokens are used to authenticate requests to the prediction APIs and are scoped on the project level.
        '''
        return self._call_api('createDeploymentToken', 'POST', query_params={}, body={'projectId': project_id}, parse_type=DeploymentAuthToken)

    def describe_deployment(self, deployment_id: str) -> Deployment:
        '''Retrieves a full description of the specified deployment.'''
        return self._call_api('describeDeployment', 'GET', query_params={'deploymentId': deployment_id}, parse_type=Deployment)

    def list_deployments(self, project_id: str) -> List[Deployment]:
        '''Retrieves a list of all deployments in the specified project.'''
        return self._call_api('listDeployments', 'GET', query_params={'projectId': project_id}, parse_type=Deployment)

    def list_deployment_tokens(self, project_id: str) -> List[DeploymentAuthToken]:
        '''Retrieves a list of all deployment tokens in the specified project.'''
        return self._call_api('listDeploymentTokens', 'GET', query_params={'projectId': project_id}, parse_type=DeploymentAuthToken)

    def update_deployment(self, deployment_id: str, description: str = None):
        '''Updates a deployment's description.'''
        return self._call_api('updateDeployment', 'PATCH', query_params={'deploymentId': deployment_id}, body={'description': description})

    def rename_deployment(self, deployment_id: str, name: str):
        '''Updates a deployment's name and/or description.'''
        return self._call_api('renameDeployment', 'PATCH', query_params={'deploymentId': deployment_id}, body={'name': name})

    def set_auto_deployment(self, deployment_id: str, enable: bool = None):
        '''Enable/Disable auto deployment for the specified deployment.

        When a model is scheduled to retrain, deployments with this enabled will be marked to automatically promote the new model
        version. After the newly trained model completes, a check on its metrics in comparison to the currently deployed model version
        will be performed. If the metrics are comparable or better, the newly trained model version is automatically promoted. If not,
        it will be marked as a failed model version promotion with an error indicating poor metrics performance.
        '''
        return self._call_api('setAutoDeployment', 'POST', query_params={'deploymentId': deployment_id}, body={'enable': enable})

    def set_deployment_model_version(self, deployment_id: str, model_version: str):
        '''Promotes a Model Version to be served in the Deployment'''
        return self._call_api('setDeploymentModelVersion', 'PATCH', query_params={'deploymentId': deployment_id}, body={'modelVersion': model_version})

    def set_deployment_feature_group_version(self, deployment_id: str, feature_group_version: str):
        '''Promotes a Feature Group Version to be served in the Deployment'''
        return self._call_api('setDeploymentFeatureGroupVersion', 'PATCH', query_params={'deploymentId': deployment_id}, body={'featureGroupVersion': feature_group_version})

    def start_deployment(self, deployment_id: str):
        '''Restarts the specified deployment that was previously suspended.'''
        return self._call_api('startDeployment', 'GET', query_params={'deploymentId': deployment_id})

    def stop_deployment(self, deployment_id: str):
        '''Stops the specified deployment.'''
        return self._call_api('stopDeployment', 'GET', query_params={'deploymentId': deployment_id})

    def delete_deployment(self, deployment_id: str):
        '''Deletes the specified deployment. The deployment's models will not be affected. Note that the deployments are not recoverable after they are deleted.'''
        return self._call_api('deleteDeployment', 'DELETE', query_params={'deploymentId': deployment_id})

    def delete_deployment_token(self, deployment_token: str):
        '''Deletes the specified deployment token.'''
        return self._call_api('deleteDeploymentToken', 'DELETE', query_params={'deploymentToken': deployment_token})

    def set_deployment_feature_group_export_file_connector_output(self, deployment_id: str, output_format: str = None, output_location: str = None):
        '''Sets the export output for the Feature Group Deployment to be a file connector.'''
        return self._call_api('setDeploymentFeatureGroupExportFileConnectorOutput', 'POST', query_params={'deploymentId': deployment_id}, body={'outputFormat': output_format, 'outputLocation': output_location})

    def set_deployment_feature_group_export_database_connector_output(self, deployment_id: str, database_connector_id: str = None, object_name: str = None, write_mode: str = None, database_feature_mapping: dict = None, id_column: str = None):
        '''Sets the export output for the Feature Group Deployment to be a Database connector.'''
        return self._call_api('setDeploymentFeatureGroupExportDatabaseConnectorOutput', 'POST', query_params={'deploymentId': deployment_id}, body={'databaseConnectorId': database_connector_id, 'objectName': object_name, 'writeMode': write_mode, 'databaseFeatureMapping': database_feature_mapping, 'idColumn': id_column})

    def remove_deployment_feature_group_export_output(self, deployment_id: str):
        '''Removes the export type that is set for the Feature Group Deployment'''
        return self._call_api('removeDeploymentFeatureGroupExportOutput', 'POST', query_params={'deploymentId': deployment_id}, body={})

    def create_refresh_policy(self, name: str, cron: str, refresh_type: str, project_id: str = None, dataset_ids: list = [], model_ids: list = [], deployment_ids: list = [], batch_prediction_ids: list = [], prediction_metric_ids: list = []) -> RefreshPolicy:
        '''Creates a refresh policy with a particular cron pattern and refresh type.

        A refresh policy allows for the scheduling of a particular set of actions at regular intervals. This can be useful for periodically updated data which needs to be re-imported into the project for re-training.
        '''
        return self._call_api('createRefreshPolicy', 'POST', query_params={}, body={'name': name, 'cron': cron, 'refreshType': refresh_type, 'projectId': project_id, 'datasetIds': dataset_ids, 'modelIds': model_ids, 'deploymentIds': deployment_ids, 'batchPredictionIds': batch_prediction_ids, 'predictionMetricIds': prediction_metric_ids}, parse_type=RefreshPolicy)

    def delete_refresh_policy(self, refresh_policy_id: str):
        '''Delete a refresh policy'''
        return self._call_api('deleteRefreshPolicy', 'DELETE', query_params={'refreshPolicyId': refresh_policy_id})

    def describe_refresh_policy(self, refresh_policy_id: str) -> RefreshPolicy:
        '''Retrieve a single refresh policy'''
        return self._call_api('describeRefreshPolicy', 'GET', query_params={'refreshPolicyId': refresh_policy_id}, parse_type=RefreshPolicy)

    def describe_refresh_pipeline_run(self, refresh_pipeline_run_id: str) -> RefreshPipelineRun:
        '''Retrieve a single refresh pipeline run'''
        return self._call_api('describeRefreshPipelineRun', 'GET', query_params={'refreshPipelineRunId': refresh_pipeline_run_id}, parse_type=RefreshPipelineRun)

    def list_refresh_policies(self, project_id: str = None, dataset_ids: list = [], model_ids: list = [], deployment_ids: list = [], batch_prediction_ids: list = [], model_monitor_ids: list = []) -> RefreshPolicy:
        '''List the refresh policies for the organization'''
        return self._call_api('listRefreshPolicies', 'GET', query_params={'projectId': project_id, 'datasetIds': dataset_ids, 'modelIds': model_ids, 'deploymentIds': deployment_ids, 'batchPredictionIds': batch_prediction_ids, 'modelMonitorIds': model_monitor_ids}, parse_type=RefreshPolicy)

    def list_refresh_pipeline_runs(self, refresh_policy_id: str) -> RefreshPipelineRun:
        '''List the the times that the refresh policy has been run'''
        return self._call_api('listRefreshPipelineRuns', 'GET', query_params={'refreshPolicyId': refresh_policy_id}, parse_type=RefreshPipelineRun)

    def pause_refresh_policy(self, refresh_policy_id: str):
        '''Pauses a refresh policy'''
        return self._call_api('pauseRefreshPolicy', 'POST', query_params={}, body={'refreshPolicyId': refresh_policy_id})

    def resume_refresh_policy(self, refresh_policy_id: str):
        '''Resumes a refresh policy'''
        return self._call_api('resumeRefreshPolicy', 'POST', query_params={}, body={'refreshPolicyId': refresh_policy_id})

    def run_refresh_policy(self, refresh_policy_id: str):
        '''Force a run of the refresh policy.'''
        return self._call_api('runRefreshPolicy', 'POST', query_params={}, body={'refreshPolicyId': refresh_policy_id})

    def update_refresh_policy(self, refresh_policy_id: str, name: str = None, cron: str = None) -> RefreshPolicy:
        '''Update the name or cron string of a  refresh policy'''
        return self._call_api('updateRefreshPolicy', 'POST', query_params={}, body={'refreshPolicyId': refresh_policy_id, 'name': name, 'cron': cron}, parse_type=RefreshPolicy)

    def lookup_features(self, deployment_token: str, deployment_id: str, query_data: dict = {}) -> Dict:
        '''Returns the feature group deployed in the feature store project.'''
        return self._call_api('lookupFeatures', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict(self, deployment_token: str, deployment_id: str, query_data: dict = {}) -> Dict:
        '''Returns a prediction for Predictive Modeling'''
        return self._call_api('predict', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_multiple(self, deployment_token: str, deployment_id: str, query_data: list = {}) -> Dict:
        '''Returns a list of predictions for Predictive Modeling'''
        return self._call_api('predictMultiple', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_from_datasets(self, deployment_token: str, deployment_id: str, query_data: dict = {}) -> Dict:
        '''Returns a list of predictions for Predictive Modeling'''
        return self._call_api('predictFromDatasets', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_lead(self, deployment_token: str, deployment_id: str, query_data: dict) -> Dict:
        '''Returns the probability of a user to be a lead on the basis of his/her interaction with the service/product and user's own attributes (e.g. income, assets, credit score, etc.). Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'user_id' mapped to mapping 'LEAD_ID' in our system).'''
        return self._call_api('predictLead', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_churn(self, deployment_token: str, deployment_id: str, query_data: dict) -> Dict:
        '''Returns a probability of a user to churn out in response to his/her interactions with the item/product/service. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'churn_result' mapped to mapping 'CHURNED_YN' in our system).'''
        return self._call_api('predictChurn', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_takeover(self, deployment_token: str, deployment_id: str, query_data: dict) -> Dict:
        '''Returns a probability for each class label associated with the types of fraud or a 'yes' or 'no' type label for the possibility of fraud. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'account_name' mapped to mapping 'ACCOUNT_ID' in our system).'''
        return self._call_api('predictTakeover', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_fraud(self, deployment_token: str, deployment_id: str, query_data: dict) -> Dict:
        '''Returns a probability of a transaction performed under a specific account as being a fraud or not. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'account_number' mapped to the mapping 'ACCOUNT_ID' in our system).'''
        return self._call_api('predictFraud', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def predict_class(self, deployment_token: str, deployment_id: str, query_data: dict = {}, threshold: float = None, threshold_class: str = None, explain_predictions: bool = False, fixed_features: list = None, nested: str = None) -> Dict:
        '''Returns a prediction for regression classification'''
        return self._call_api('predictClass', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'threshold': threshold, 'thresholdClass': threshold_class, 'explainPredictions': explain_predictions, 'fixedFeatures': fixed_features, 'nested': nested})

    def predict_target(self, deployment_token: str, deployment_id: str, query_data: dict = {}, explain_predictions: bool = False, fixed_features: list = None, nested: str = None) -> Dict:
        '''Returns a prediction from a classification or regression model. Optionally, includes explanations.'''
        return self._call_api('predictTarget', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'explainPredictions': explain_predictions, 'fixedFeatures': fixed_features, 'nested': nested})

    def get_anomalies(self, deployment_token: str, deployment_id: str, threshold: float = None, histogram: bool = False) -> io.BytesIO:
        '''Returns a list of anomalies from the training dataset'''
        return self._call_api('getAnomalies', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'threshold': threshold, 'histogram': histogram})

    def is_anomaly(self, deployment_token: str, deployment_id: str, query_data: dict = None) -> Dict:
        '''Returns a list of anomaly attributes based on login information for a specified account. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'account_name' mapped to mapping 'ACCOUNT_ID' in our system).'''
        return self._call_api('isAnomaly', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def get_forecast(self, deployment_token: str, deployment_id: str, query_data: dict, future_data: dict = None, num_predictions: int = None, prediction_start: str = None) -> Dict:
        '''Returns a list of forecasts for a given entity under the specified project deployment. Note that the inputs to the deployed model will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'holiday_yn' mapped to mapping 'FUTURE' in our system).'''
        return self._call_api('getForecast', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'futureData': future_data, 'numPredictions': num_predictions, 'predictionStart': prediction_start})

    def get_k_nearest(self, deployment_token: str, deployment_id: str, vector: list, k: int = None, distance: str = None, include_score: bool = False) -> Dict:
        '''Returns the k nearest neighbors for the provided embedding vector.'''
        return self._call_api('getKNearest', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'vector': vector, 'k': k, 'distance': distance, 'includeScore': include_score})

    def get_multiple_k_nearest(self, deployment_token: str, deployment_id: str, queries: list):
        '''Returns the k nearest neighbors for the queries provided'''
        return self._call_api('getMultipleKNearest', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queries': queries})

    def get_labels(self, deployment_token: str, deployment_id: str, query_data: dict, threshold: float = 0.5) -> Dict:
        '''Returns a list of scored labels from'''
        return self._call_api('getLabels', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'threshold': threshold})

    def get_recommendations(self, deployment_token: str, deployment_id: str, query_data: dict, num_items: int = 50, page: int = 1, exclude_item_ids: list = [], score_field: str = '', scaling_factors: list = [], restrict_items: list = [], exclude_items: list = [], explore_fraction: float = 0.0) -> Dict:
        '''Returns a list of recommendations for a given user under the specified project deployment. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'time' mapped to mapping 'TIMESTAMP' in our system).'''
        return self._call_api('getRecommendations', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'numItems': num_items, 'page': page, 'excludeItemIds': exclude_item_ids, 'scoreField': score_field, 'scalingFactors': scaling_factors, 'restrictItems': restrict_items, 'excludeItems': exclude_items, 'exploreFraction': explore_fraction})

    def get_personalized_ranking(self, deployment_token: str, deployment_id: str, query_data: dict, preserve_ranks: list = [], scaling_factors: list = []) -> Dict:
        '''Returns a list of items with personalized promotions on them for a given user under the specified project deployment. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'item_code' mapped to mapping 'ITEM_ID' in our system).'''
        return self._call_api('getPersonalizedRanking', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'preserveRanks': preserve_ranks, 'scalingFactors': scaling_factors})

    def get_ranked_items(self, deployment_token: str, deployment_id: str, query_data: dict, preserve_ranks: list = [], scaling_factors: list = []) -> Dict:
        '''Returns a list of re-ranked items for a selected user when a list of items is required to be reranked according to the user's preferences. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'item_code' mapped to mapping 'ITEM_ID' in our system).'''
        return self._call_api('getRankedItems', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'preserveRanks': preserve_ranks, 'scalingFactors': scaling_factors})

    def get_related_items(self, deployment_token: str, deployment_id: str, query_data: dict, num_items: int = 50, page: int = 1, scaling_factors: list = [], restrict_items: list = [], exclude_items: list = []) -> Dict:
        '''Returns a list of related items for a given item under the specified project deployment. Note that the inputs to this method, wherever applicable, will be the column names in your dataset mapped to the column mappings in our system (e.g. column 'item_code' mapped to mapping 'ITEM_ID' in our system).'''
        return self._call_api('getRelatedItems', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data, 'numItems': num_items, 'page': page, 'scalingFactors': scaling_factors, 'restrictItems': restrict_items, 'excludeItems': exclude_items})

    def get_feature_group_rows(self, deployment_token: str, deployment_id: str, query_data: dict):
        ''''''
        return self._call_api('getFeatureGroupRows', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def get_search_results(self, deployment_token: str, deployment_id: str, query_data: dict) -> Dict:
        '''TODO'''
        return self._call_api('getSearchResults', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data})

    def get_sentiment(self, deployment_token: str, deployment_id: str, document: str) -> Dict:
        '''TODO'''
        return self._call_api('getSentiment', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'document': document}, parse_type=NlpSentimentPrediction)

    def predict_language(self, deployment_token: str, deployment_id: str, query_data: str) -> Dict:
        '''TODO'''
        return self._call_api('predictLanguage', 'POST', query_params={'deploymentToken': deployment_token, 'deploymentId': deployment_id}, body={'queryData': query_data}, parse_type=LanguageDetectionPrediction)

    def create_batch_prediction(self, deployment_id: str, table_name: str = None, name: str = None, global_prediction_args: dict = None, explanations: bool = False, output_format: str = None, output_location: str = None, database_connector_id: str = None, database_output_config: dict = None, refresh_schedule: str = None, csv_input_prefix: str = None, csv_prediction_prefix: str = None, csv_explanations_prefix: str = None) -> BatchPrediction:
        '''Creates a batch prediction job description for the given deployment.'''
        return self._call_api('createBatchPrediction', 'POST', query_params={'deploymentId': deployment_id}, body={'tableName': table_name, 'name': name, 'globalPredictionArgs': global_prediction_args, 'explanations': explanations, 'outputFormat': output_format, 'outputLocation': output_location, 'databaseConnectorId': database_connector_id, 'databaseOutputConfig': database_output_config, 'refreshSchedule': refresh_schedule, 'csvInputPrefix': csv_input_prefix, 'csvPredictionPrefix': csv_prediction_prefix, 'csvExplanationsPrefix': csv_explanations_prefix}, parse_type=BatchPrediction)

    def start_batch_prediction(self, batch_prediction_id: str) -> BatchPredictionVersion:
        '''Creates a new batch prediction version job for a given batch prediction job description'''
        return self._call_api('startBatchPrediction', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id}, parse_type=BatchPredictionVersion)

    def download_batch_prediction_result_chunk(self, batch_prediction_version: str, offset: int = 0, chunk_size: int = 10485760) -> io.BytesIO:
        '''Returns a stream containing the batch prediction results'''
        return self._call_api('downloadBatchPredictionResultChunk', 'GET', query_params={'batchPredictionVersion': batch_prediction_version, 'offset': offset, 'chunkSize': chunk_size}, streamable_response=True)

    def get_batch_prediction_connector_errors(self, batch_prediction_version: str) -> io.BytesIO:
        '''Returns a stream containing the batch prediction database connection write errors, if any writes failed to the database connector'''
        return self._call_api('getBatchPredictionConnectorErrors', 'GET', query_params={'batchPredictionVersion': batch_prediction_version}, streamable_response=True)

    def list_batch_predictions(self, project_id: str) -> List[BatchPrediction]:
        '''Retrieves a list for the batch predictions in the project'''
        return self._call_api('listBatchPredictions', 'GET', query_params={'projectId': project_id}, parse_type=BatchPrediction)

    def describe_batch_prediction(self, batch_prediction_id: str) -> BatchPrediction:
        '''Describes the batch prediction'''
        return self._call_api('describeBatchPrediction', 'GET', query_params={'batchPredictionId': batch_prediction_id}, parse_type=BatchPrediction)

    def list_batch_prediction_versions(self, batch_prediction_id: str, limit: int = 100, start_after_version: str = None) -> List[BatchPredictionVersion]:
        '''Retrieves a list of versions of a given batch prediction'''
        return self._call_api('listBatchPredictionVersions', 'GET', query_params={'batchPredictionId': batch_prediction_id, 'limit': limit, 'startAfterVersion': start_after_version}, parse_type=BatchPredictionVersion)

    def describe_batch_prediction_version(self, batch_prediction_version: str) -> BatchPredictionVersion:
        '''Describes a batch prediction version'''
        return self._call_api('describeBatchPredictionVersion', 'GET', query_params={'batchPredictionVersion': batch_prediction_version}, parse_type=BatchPredictionVersion)

    def update_batch_prediction(self, batch_prediction_id: str, deployment_id: str = None, global_prediction_args: dict = None, explanations: bool = None, output_format: str = None, csv_input_prefix: str = None, csv_prediction_prefix: str = None, csv_explanations_prefix: str = None) -> BatchPrediction:
        '''Updates a batch prediction job description'''
        return self._call_api('updateBatchPrediction', 'POST', query_params={'deploymentId': deployment_id}, body={'batchPredictionId': batch_prediction_id, 'globalPredictionArgs': global_prediction_args, 'explanations': explanations, 'outputFormat': output_format, 'csvInputPrefix': csv_input_prefix, 'csvPredictionPrefix': csv_prediction_prefix, 'csvExplanationsPrefix': csv_explanations_prefix}, parse_type=BatchPrediction)

    def set_batch_prediction_file_connector_output(self, batch_prediction_id: str, output_format: str = None, output_location: str = None) -> BatchPrediction:
        '''Updates the file connector output configuration of the batch prediction'''
        return self._call_api('setBatchPredictionFileConnectorOutput', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id, 'outputFormat': output_format, 'outputLocation': output_location}, parse_type=BatchPrediction)

    def set_batch_prediction_database_connector_output(self, batch_prediction_id: str, database_connector_id: str = None, database_output_config: dict = None) -> BatchPrediction:
        '''Updates the database connector output configuration of the batch prediction'''
        return self._call_api('setBatchPredictionDatabaseConnectorOutput', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id, 'databaseConnectorId': database_connector_id, 'databaseOutputConfig': database_output_config}, parse_type=BatchPrediction)

    def set_batch_prediction_feature_group_output(self, batch_prediction_id: str, table_name: str) -> BatchPrediction:
        '''Creates a feature group and sets it to be the batch prediction output'''
        return self._call_api('setBatchPredictionFeatureGroupOutput', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id, 'tableName': table_name}, parse_type=BatchPrediction)

    def set_batch_prediction_output_to_console(self, batch_prediction_id: str) -> BatchPrediction:
        '''Sets the batch prediction output to the console, clearing both the file connector and database connector config'''
        return self._call_api('setBatchPredictionOutputToConsole', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id}, parse_type=BatchPrediction)

    def set_batch_prediction_dataset(self, batch_prediction_id: str, dataset_type: str, dataset_id: str = None) -> BatchPrediction:
        '''[Deprecated] Sets the batch prediction input dataset. Only applicable for legacy dataset-based projects'''
        return self._call_api('setBatchPredictionDataset', 'POST', query_params={'datasetId': dataset_id}, body={'batchPredictionId': batch_prediction_id, 'datasetType': dataset_type}, parse_type=BatchPrediction)

    def set_batch_prediction_feature_group(self, batch_prediction_id: str, feature_group_type: str, feature_group_id: str = None) -> BatchPrediction:
        '''Sets the batch prediction input feature group.'''
        return self._call_api('setBatchPredictionFeatureGroup', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id, 'featureGroupType': feature_group_type, 'featureGroupId': feature_group_id}, parse_type=BatchPrediction)

    def set_batch_prediction_dataset_remap(self, batch_prediction_id: str, dataset_id_remap: dict) -> BatchPrediction:
        '''For the purpose of this batch prediction, will swap out datasets in the input feature groups'''
        return self._call_api('setBatchPredictionDatasetRemap', 'POST', query_params={}, body={'batchPredictionId': batch_prediction_id, 'datasetIdRemap': dataset_id_remap}, parse_type=BatchPrediction)

    def delete_batch_prediction(self, batch_prediction_id: str):
        '''Deletes a batch prediction'''
        return self._call_api('deleteBatchPrediction', 'DELETE', query_params={'batchPredictionId': batch_prediction_id})

    def add_user_item_interaction(self, streaming_token: str, dataset_id: str, timestamp: int, user_id: str, item_id: list, event_type: str, additional_attributes: dict):
        '''Adds a user-item interaction record (data row) to a streaming dataset.'''
        return self._call_api('addUserItemInteraction', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'timestamp': timestamp, 'userId': user_id, 'itemId': item_id, 'eventType': event_type, 'additionalAttributes': additional_attributes})

    def upsert_user_attributes(self, streaming_token: str, dataset_id: str, user_id: str, user_attributes: dict):
        '''Adds a user attributes record (data row) to a streaming dataset.

        Either the streaming dataset ID or the project ID is required.
        '''
        return self._call_api('upsertUserAttributes', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'userId': user_id, 'userAttributes': user_attributes})

    def upsert_item_attributes(self, streaming_token: str, dataset_id: str, item_id: str, item_attributes: dict):
        '''Adds an item attributes record (data row) to a streaming dataset.

        Either the streaming dataset ID or the project ID is required.
        '''
        return self._call_api('upsertItemAttributes', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'itemId': item_id, 'itemAttributes': item_attributes})

    def add_multiple_user_item_interactions(self, streaming_token: str, dataset_id: str, interactions: list):
        '''Adds a user-item interaction record (data row) to a streaming dataset.'''
        return self._call_api('addMultipleUserItemInteractions', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'interactions': interactions})

    def upsert_multiple_user_attributes(self, streaming_token: str, dataset_id: str, upserts: list):
        '''Adds multiple user attributes records (data row) to a streaming dataset.

        The streaming dataset ID is required.
        '''
        return self._call_api('upsertMultipleUserAttributes', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'upserts': upserts})

    def upsert_multiple_item_attributes(self, streaming_token: str, dataset_id: str, upserts: list):
        '''Adds multiple item attributes records (data row) to a streaming dataset.

        The streaming dataset ID is required.
        '''
        return self._call_api('upsertMultipleItemAttributes', 'POST', query_params={'streamingToken': streaming_token, 'datasetId': dataset_id}, body={'upserts': upserts})

    def upsert_item_embeddings(self, streaming_token: str, model_id: str, item_id: str, vector: list, catalog_id: str = None):
        '''Upserts an embedding vector for an item id for a model_id.'''
        return self._call_api('upsertItemEmbeddings', 'POST', query_params={'streamingToken': streaming_token}, body={'modelId': model_id, 'itemId': item_id, 'vector': vector, 'catalogId': catalog_id})

    def delete_item_embeddings(self, streaming_token: str, model_id: str, item_ids: list, catalog_id: str = None):
        '''Deletes knn embeddings for a list of item ids for a model_id.'''
        return self._call_api('deleteItemEmbeddings', 'POST', query_params={'streamingToken': streaming_token}, body={'modelId': model_id, 'itemIds': item_ids, 'catalogId': catalog_id})

    def upsert_multiple_item_embeddings(self, streaming_token: str, model_id: str, upserts: list, catalog_id: str = None):
        '''Upserts a knn embedding for multiple item ids for a model_id.'''
        return self._call_api('upsertMultipleItemEmbeddings', 'POST', query_params={'streamingToken': streaming_token}, body={'modelId': model_id, 'upserts': upserts, 'catalogId': catalog_id})

    def upsert_data(self, feature_group_id: str, streaming_token: str, data: dict):
        '''Updates new data into the feature group for a given lookup key recordId if the recordID is found otherwise inserts new data into the feature group.'''
        return self._call_api('upsertData', 'POST', query_params={'streamingToken': streaming_token}, body={'featureGroupId': feature_group_id, 'data': data})

    def append_data(self, feature_group_id: str, streaming_token: str, data: dict):
        '''Appends new data into the feature group for a given lookup key recordId.'''
        return self._call_api('appendData', 'POST', query_params={'streamingToken': streaming_token}, body={'featureGroupId': feature_group_id, 'data': data})
