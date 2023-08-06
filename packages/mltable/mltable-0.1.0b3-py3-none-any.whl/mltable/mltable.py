# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality to create and interact with MLTable objects
"""
import os
import yaml

from azureml.dataprep.api._loggerfactory import track, _LoggerFactory
from azureml.dataprep.api._dataframereader import get_dataframe_reader
from azureml.dataprep.api.mltable._mltable_helper import _read_yaml, _validate, _download_mltable_yaml, \
    _parse_path_format, _PathType, _make_all_paths_absolute
from ._aml_utilities._aml_rest_client_helper import _get_data_asset_by_id

_PUBLIC_API = 'PublicApi'
_INTERNAL_API = 'InternalCall'
_logger = None
_PATHS_SECTION_KEY = 'paths'

_RUNTIME_NEEDED_PROPS = ['query_source', 'paths', 'transformations']


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _remove_properties_not_runtime_needed(mltable_yaml_dict):
    filtered_mltable_yaml_dict = {k: v for k, v in mltable_yaml_dict.items() if k in _RUNTIME_NEEDED_PROPS and v}
    return filtered_mltable_yaml_dict


@track(_get_logger, custom_dimensions={'app_name': 'MLTable'})
def load(uri, storage_options: dict=None):
    """
    Loads the MLTable file(YAML) present at the given uri.

    .. remarks::

        There must be a valid MLTable file(YAML) with the name 'MLTable' present at the given uri.

        .. code-block:: python

            # load mltable from local folder
            from mltable import load
            tbl = load('.\\samples\\mltable_sample')

            # load mltable from azureml datastore uri
            from mltable import load
            tbl = load(
                'azureml://subscriptions/<subscription-id>/
                resourcegroups/<resourcegroup-name>/workspaces/<workspace-name>/
                datastores/<datastore-name>/paths/<mltable-path-on-datastore>/')

    :param uri: uri supports long-form datastore uri, storage uri or local path.
    :type uri: str
    :param storage_options: optional to specify aml workspace information when uri is an aml asset.
        it supports keys of 'subscription', 'resource_group', 'workspace', 'location'.
        All of these are required to locate an azure machine learning workspace.
    :type storage_options: dict[str, str]
    :return: MLTable object representing the MLTable file(YAML) at uri.
    :rtype: mltable.MLTable
    """
    path_type, local_path, _ = _parse_path_format(uri)
    local_path = os.path.normpath(local_path)
    if path_type == _PathType.local:
        if not os.path.isabs(local_path):
            local_path = os.path.join(os.getcwd(), local_path)
        mltable_dict = _read_yaml(local_path)
        _validate(mltable_dict)
    elif path_type == _PathType.cloud:
        local_path = _download_mltable_yaml(uri)
        mltable_dict = _read_yaml(local_path)
        _validate(mltable_dict)
    elif path_type == _PathType.legacy_dataset:
        # skip mltable yaml validation for v1 legacy dataset because of some legacy schema generated in converter
        mltable_dict = _load_mltable_from_asset(uri, storage_options)
    else:
        raise ValueError('The uri should be a valid path to a local or cloud directory which contains an '
                         'MLTable file.')
    mltable_yaml_dict = _remove_properties_not_runtime_needed(mltable_dict)
    mltable_yaml_dict = _make_all_paths_absolute(mltable_yaml_dict, local_path)
    return MLTable._create(mltable_dict=mltable_yaml_dict, original_mltable_dict=mltable_dict)


class MLTable:
    """
    Represent MLTable.

    A MLTable defines a series of lazily-evaluated, immutable operations to load data from the
    data source. Data is not loaded from the source until MLTable
    is asked to deliver data.
    """

    def __init__(self):
        """
        Initialize a new MLTable object

        This constructor is not supposed to be invoked directly. MLTable is intended to be created using
        :func:`mltable.load`
        """
        self.__original_mltable_dict = None
        self.__mltable_dict = None

    @track(_get_logger, custom_dimensions={'app_name': 'MLTable'})
    def to_pandas_dataframe(self):
        """
        Load all records from the paths specified in the MLTable file into a pandas DataFrame.

        .. remarks::

            The following code snippet shows how to use the to_pandas_dataframe api to obtain a pandas dataframe
            corresponding to the provided MLTable.

            .. code-block:: python

                from mltable import load
                tbl = load('.\\samples\\mltable_sample')
                pdf = tbl.to_pandas_dataframe()
                print(pdf.shape)

        :return: pandas.DataFrame object containing the records from the paths in the MLTable.
        :rtype: pandas.DataFrame
        """
        dataframe_reader = get_dataframe_reader()
        return dataframe_reader._to_pandas_arrow_rslex(self.__mltable_yaml_string)

    @property
    @track(_get_logger, custom_dimensions={'app_name': 'MLTable'})
    def paths(self):
        """
        Returns a list of dicts containing paths specified in the MLTable.

        :return: A list of dicts containing paths specified in the MLTable
        :rtype: list[dict]
        """
        return self.__original_mltable_dict[_PATHS_SECTION_KEY]

    @classmethod
    @track(_get_logger, custom_dimensions={'app_name': 'MLTable'})
    def _create(cls, mltable_dict=None, original_mltable_dict=None):
        mltable = MLTable()
        mltable.__original_mltable_dict = original_mltable_dict
        mltable.__mltable_dict = mltable_dict
        if mltable_dict is not None:
            mltable.__mltable_yaml_string = yaml.dump(mltable_dict)

        return mltable


def _load_mltable_from_asset(asset_id, storage_options=None):
    import yaml
    asset = _get_data_asset_by_id(asset_id, storage_options)
    mltable_string = asset.legacy_dataflow
    if not mltable_string or mltable_string == '':
        raise SystemError(f'Data asset service returned invalid MLTable yaml for asset {asset_id}')

    return yaml.safe_load(mltable_string)
