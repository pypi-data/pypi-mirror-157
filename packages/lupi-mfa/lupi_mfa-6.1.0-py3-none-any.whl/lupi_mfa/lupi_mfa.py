from typing import Tuple
from numpy import ndarray
from collections import OrderedDict
import os
import numpy
import typing

from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.kernel_ridge import KernelRidge

from d3m.container import DataFrame as d3m_dataframe
from d3m.metadata import hyperparams, params, base as metadata_base
from d3m import utils, container
from d3m.base import utils as base_utils
from d3m.primitive_interfaces.base import CallResult
from d3m.primitive_interfaces import base, unsupervised_learning

from sklearn.impute import SimpleImputer as Imputer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import math

import logging
import warnings


log = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


__author__ = 'VencoreLabs'
__version__ = "6.1.0"
D3M_API_VERSION = '2022.5.5'


Inputs = d3m_dataframe
Outputs = d3m_dataframe


class Hyperparams(hyperparams.Hyperparams):
    regressor_type = hyperparams.Enumeration[str](
        semantic_types=["https://metadata.datadrivendiscovery.org/types/TuningParameter"],
        values=['linear', 'kernelridge', 'none', 'all'],
        default='linear',
        description='Specifies the regression type to be used in the algorithm.'
    )

    dataframe_resource = hyperparams.Hyperparameter[typing.Union[str, None]](
        default=None,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Resource ID of a DataFrame to extract if there are multiple tabular resources inside a Dataset and none is a dataset entry point.",
    )

    use_input_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to force primitive to use as training input. If any specified column cannot be parsed, it is skipped.",
    )
    use_output_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to force primitive to use as training target. If any specified column cannot be parsed, it is skipped.",
    )
    exclude_input_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to not use as training inputs. Applicable only if \"use_columns\" is not provided.",
    )
    exclude_output_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to not use as training target. Applicable only if \"use_columns\" is not provided.",
    )
    return_result = hyperparams.Enumeration(
        values=['append', 'replace', 'new'],
        default='new',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Should parsed columns be appended, should they replace original columns, or should only parsed columns be returned? This hyperparam is ignored if use_semantic_types is set to false.",
    )
    use_semantic_types = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Controls whether semantic_types metadata will be used for filtering columns in input dataframe. Setting this to false makes the code ignore return_result and will produce only the output dataframe"
    )
    use_scree = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Controls whether to use Scree to filter argumented features"
    )
    add_index_columns = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Also include primary index columns if input data has them. Applicable only if \"return_result\" is set to \"new\".",
    )
    gamma_gridsearch = hyperparams.Hyperparameter[Tuple[float, float, float]](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
        default=(-1.0, 6.5, 3.4),
        description='Specifiy the range and step for the primitive internal grid search on gamma parameter. Expecting a tuple (lower bound, upper bound, step)'
    )
    C_gridsearch = hyperparams.Hyperparameter[Tuple[float, float, float]](
        semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
        default=(-1.0, 6.5, 3.4),
        description='Specifiy the range and step for the primitive internal grid search on C parameter. Expecting a tuple (lower bound, upper bound, step)'
    )
    n_jobs = hyperparams.Union(
        configuration=OrderedDict({
            'limit': hyperparams.Bounded[int](
                default=4,
                lower=1,
                upper=None,
                semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
            ),
            'all_cores': hyperparams.Constant(
                default=-1,
                semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'],
            )
        }),
        default='limit',
        description='The number of jobs to run in parallel for both `fit` and `predict`. If -1, then the number of jobs is set to the number of cores.',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ResourcesUseParameter']
    )

class Params(params.Params):
    target_name: typing.Optional[str]
    privileged_features: typing.List[str]
    augmented_regrs: typing.Optional[typing.Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]]
    prifeature_to_regressor: typing.Dict[str, typing.Any]
    num_of_std: typing.Optional[int]

class LupiMFA(unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
    Perspecta D3M Lupi Mutual Feature Augmentation primitive learn privileged features which are available in the training dataset
    from the standard features by regression and then apply the regressors on the test dataset.
    
    """
    __git_commit__ = utils.current_git_commit(os.path.dirname(__file__))
    __author__ = "VencoreLabs"
    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '5361ebf6-9e5a-4ce5-b73c-3babf12f1941',
            'version':  __version__,
            'name': "lupi_mfa.lupi_mfa.LupiMFA",
            'python_path': 'd3m.primitives.data_preprocessing.lupi_mfa.lupi_mfa.LupiMFA',
            'source': {
                'name': __author__,
                'contact': 'mailto:plin@perspectalabs.com',
                'uris': [
                    'https://gitlab.com/datadrivendiscovery/contrib/lupi_mfa/-/blob/master/lupi_mfa/lupi_mfa.py',
                    'https://gitlab.com/datadrivendiscovery/contrib/lupi_mfa.git'
                ],
            },
            'installation': [{
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'lupi_mfa',
                'version': __version__,
            }],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.DATA_CONVERSION,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_PREPROCESSING,
        },
    )

    def __init__(self, *,
                 hyperparams: Hyperparams,
                 random_seed: int = 0) -> None:

        super().__init__(hyperparams=hyperparams)

        self._C_gridsearch = hyperparams['C_gridsearch']
        self._gamma_gridsearch = hyperparams['gamma_gridsearch']
        self._regressor_type = hyperparams['regressor_type']
        self._use_scree = hyperparams['use_scree']
        self._prifeature_to_regressor = {}
        self._nJobs = hyperparams['n_jobs']
        C_list = self._C_gridsearch
        gamma_list = self._gamma_gridsearch
        C_range = 2.0 ** np.arange(C_list[0], C_list[1], C_list[2])
        gamma_range = 1.0 / (2 * ((2 ** np.arange(gamma_list[0], gamma_list[1], gamma_list[2])) ** 2))
        alpha_range = [1. / (2. * c) for c in C_range]
        self._regr_param_grid = dict(alpha=alpha_range, gamma=gamma_range)
        self._augmented_regrs = None
        self.num_of_std = None

    def get_params(self) -> Params:
        return Params(dict(
            target_name=self._target_name,
            privileged_features=self.privileged_features,
            augmented_regrs=self._augmented_regrs,
            prifeature_to_regressor=self._prifeature_to_regressor,
            num_of_std=self.num_of_std,
        ))

    def set_params(self, *, params: Params):
        self._target_name = params['target_name']
        self.privileged_features = params['privileged_features']
        self._augmented_regrs = params['augmented_regrs']
        self._prifeature_to_regressor = params['prifeature_to_regressor']
        self.num_of_std = params['num_of_std']

    def set_training_data(self, *, inputs: Inputs) -> None:
        """
        Sets training data of this primitive.
        """
        
        privileged_features = self._get_privileged_features(inputs)

        # get the training inputs by exclude columns such as D3mindex, target, etc
        training_inputs  = self._get_columns_to_fit(inputs, self.hyperparams)
        
        if len(privileged_features) > 0:
            self._target_name = self._get_target_name(inputs)
        else:
            self._target_name = None

        training_inputs = self._data_imputer(training_inputs)
        
        self._training_inputs = training_inputs

        self.privileged_features = privileged_features
        self._fitted = False

    def _get_privileged_features(self, inputs):
        privileged_features = []
        privileged_semantic_type = 'https://metadata.datadrivendiscovery.org/types/PrivilegedData'
        col_length = inputs.metadata.query((metadata_base.ALL_ELEMENTS,))['dimension']['length']
        for col in range(col_length):
            semantic_types = inputs.metadata.query((metadata_base.ALL_ELEMENTS, col))['semantic_types']
            col_name = inputs.metadata.query((metadata_base.ALL_ELEMENTS, col))['name']
            if privileged_semantic_type in semantic_types:
                #                print("col {} {} is privileged".format(col, col_name))
                privileged_features.append(col_name)

        return privileged_features

    def _data_imputer(self, inputs):
        inputData = inputs.copy()
        df = inputData.apply(pd.to_numeric, args=('coerce',))
        isallnull = df.isnull().all()
        allnull_columns = isallnull.index[isallnull].tolist()
        # set all nan columns to value 0 so that the whole column will not be imputed
        df.loc[:, allnull_columns] = 0
        imputer = Imputer(missing_values=np.nan, strategy='mean')
        imputer.fit(df)
        imputed_df = pd.DataFrame(imputer.transform(df))
        imputed_df.columns = df.columns
        imputed_df.index = df.index
        return imputed_df

    def _data_prep(self, inputs, privileged_features):
        inputData = self._data_imputer(inputs)
        inputData = inputData.fillna('0').replace('', '0')
        inputData = d3m_dataframe(inputData)

        categoricaldata_semantic_type = "https://metadata.datadrivendiscovery.org/types/CategoricalData"
        attribute_semantic_type = "https://metadata.datadrivendiscovery.org/types/Attribute"
        truetarget_semantic_type = "https://metadata.datadrivendiscovery.org/types/TrueTarget"

        col_length = inputData.shape[1]
        if len(privileged_features):
            for col_index in range(col_length):
                col_metadata = inputs.metadata.query((metadata_base.ALL_ELEMENTS, col_index))
                name = col_metadata['name']
                semantic_types = col_metadata['semantic_types']

                if truetarget_semantic_type in semantic_types:
                    targetCatLabel = name
                    # self._target_names = targetCatLabel
        else:
            targetCatLabel = None
        return (inputData, targetCatLabel)

    def _get_target_name(self, inputs):
        inputData = d3m_dataframe(inputs)
        categoricaldata_semantic_type = "https://metadata.datadrivendiscovery.org/types/CategoricalData"
        attribute_semantic_type = "https://metadata.datadrivendiscovery.org/types/Attribute"
        truetarget_semantic_type = "https://metadata.datadrivendiscovery.org/types/TrueTarget"
        targetCatLabel = None

        col_length = inputData.shape[1]
        for col_index in range(col_length):
            col_metadata = inputs.metadata.query((metadata_base.ALL_ELEMENTS, col_index))
            name = col_metadata['name']
            semantic_types = col_metadata['semantic_types']

            if truetarget_semantic_type in semantic_types:
                targetCatLabel = name
                # self._target_names = targetCatLabel
        return targetCatLabel

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs is None:
            raise ValueError("Missing training data.")

        pri_features_names = self.privileged_features
        pri_features = [self._training_inputs.columns.get_loc(x) for x in pri_features_names]


        if len(pri_features_names) > 0:  # dataset has privileged features
            self._regressor_fit()
        else:  # datasett has no privileged feature
            self._selregressor_fit()

        return CallResult(None)

    def _get_pri_std_data(self, training_inputs):
        # prepare X
        pri_features = self.privileged_features

        if self._target_name in training_inputs.columns:
            X_train = training_inputs.drop([self._target_name], axis=1)
        else:
            X_train = training_inputs
        #X = check_array(X_train)

        if not isinstance(X_train, pd.DataFrame):
            X_train = pd.DataFrame(X_train)

        if pri_features == []:
            log.info("pri_features is empty!!")
            X_pri = []
        else:
            X_pri = X_train.loc[:, pri_features]

        X_std = X_train.drop(columns=pri_features)

        return X_pri, X_std

    def _selregressor_fit(self):
        #
        train_data = self._training_inputs

        if self._target_name:
            X_train = train_data.drop([self._target_name], axis=1)
            y_train = train_data[self._target_name]
        else:
            X_train = train_data
            y_train = np.random.randint(low=2, size=(X_train.shape[0]))
        all_augmented_regrs = self._train_regr(X_train)
        # SCREE filter to select important augmented features
        nregrs, good_indices, good_scree_indices = self._get_im_regrs_by_scree(X_train, y_train, all_augmented_regrs, ntree=1000)
        self._augmented_regrs =  (nregrs, good_indices, good_scree_indices)

    def _regressor_fit(self):
        """Fit the model to data.
        """

        X_pri, X_std = self._get_pri_std_data(self._training_inputs)

        supported_regressor_types = ['kernelridge', 'linear', 'none', 'all']
        if self._regressor_type not in supported_regressor_types:
            log.error("not supported regr_type{}".format(self._regressor_type))
            sys.exit(1)
        if self._regressor_type == 'kernelridge':
            regr_type_list = ['kernelridge']
        elif self._regressor_type == 'linear':
            regr_type_list = ['linear']
        elif self._regressor_type == 'all':
            regr_type_list = ['kernelridge', 'linear']
        else:
            regr_type_list = []

        prifeature_to_regrtype = {}  # dictionary mapping  priv feature to its regrtype
        prifeature_to_regressor = {} # dictionary mapping  priv feature to its regressor

        for ft in self.privileged_features:
            y_true_ft = X_pri.loc[:,ft]
            r2score_list = []  # list to store R2 values of regr_type_list
            regr_candidate_list = []  # list to store regr candidates for j th priv feature
            for regr_type in regr_type_list:
                if regr_type == 'kernelridge':
                    regr = GridSearchCV(KernelRidge(kernel='rbf'),
                                        param_grid=self._regr_param_grid,
                                        scoring='r2', cv=5,
                                        n_jobs=self._nJobs)
                    regr.fit(X_std, y_true_ft)
                    best_cvscore = regr.best_score_
                    r2score_list.append(best_cvscore)
                    regr_candidate_list.append(regr)
                else:
                    regr = LinearRegression(fit_intercept=1)
                    regr.fit(X_std, y_true_ft)
                    r2_score = regr.score(X_std, y_true_ft)
                    r2score_list.append(r2_score)
                    regr_candidate_list.append(regr)
                    ##############################
            maxR2_index = r2score_list.index(max(r2score_list))  # index of the max R2 list
            best_regr = regr_candidate_list[maxR2_index]
            prifeature_to_regrtype[ft] = regr_type_list[maxR2_index]
            prifeature_to_regressor[ft] = best_regr # the best regressor for each priviledged feature

        self._prifeature_to_regressor = prifeature_to_regressor

    def _train_regr(self, X_train):
        # train regressor for feature augmentation
        # total number of standard features
        num_of_std = X_train.shape[1]
        self.num_of_std = num_of_std
        X_std = X_train.values

        ## now, fit the lupi regressors
        regr_list_aug = []
        supported_regr_types = ['kernelridge', 'linear']

        if self._regressor_type not in supported_regr_types:
            log.error("not supported regr_type{}".format(self._regressor_type))
            sys.exit(1)

        regrs=[]
        for j in np.arange(num_of_std):
            y_true_j = X_std[:, j]
            X_stds_noj = np.delete(X_std, [j], axis = 1)

            if self._regressor_type == 'kernelridge':
                regr = GridSearchCV(KernelRidge(kernel='rbf'),
                                    param_grid=self._regr_param_grid,
                                    scoring='r2', cv=5,
                                    n_jobs = self._nJobs)
                regr.fit(X_stds_noj, y_true_j)
                regrs.append(regr)
            elif self._regressor_type == 'linear':
                regr = LinearRegression(fit_intercept=1)
                regr.fit(X_stds_noj, y_true_j)
                regrs.append(regr)

        regr_list_aug.extend(list(regrs))
        return regr_list_aug

    def _calc_importance_all(self, X, y, ntree=2000):
        forest = RandomForestClassifier(n_estimators=ntree, criterion='entropy', class_weight='balanced',
                                        random_state=0)
        forest.fit(X, y)
        importances = forest.feature_importances_
        return importances

    def _g_scree(self, values):
        # values = np.asarray(values)
        p = len(values)
        lq_value = np.zeros(p)
        for q in range(1, p):
            mu1 = np.mean(values[0:q])
            sigma1 = np.var(values[0:q])

            mu2 = np.mean(values[q:p])
            sigma2 = np.var(values[q:p])

            sigma = (sigma1 * q + sigma2 * (p - q)) / (p - 2)

            for j in range(0, p):
                for i in range(0, q):
                    lq_value[q] = lq_value[q] \
                                  + math.log(
                        (1 / math.sqrt(2 * math.pi * sigma)) * math.exp(-((values[i] - mu1) ** 2) / (2 * sigma)))

                for i in range(q, p):
                    lq_value[q] = lq_value[q] \
                                  + math.log(
                        (1 / math.sqrt(2 * math.pi * sigma)) * math.exp(-((values[i] - mu2) ** 2) / (2 * sigma)))

        print("    lq_value {}".format(lq_value))
        index_best = np.argmax(lq_value)
        return index_best

    def _get_im_regrs_by_scree(self, X_stds, y_train, regrs, ntree=500):
        #apply SCREE filter to get important mutual feature augmented regressors
        num_of_std = X_stds.shape[1]
        num_of_features = num_of_std + len(regrs)
        augmented_feature_list = list(range(num_of_std, num_of_features, 1))
        X2 = X_stds.copy()
        lupi_feat = np.empty([X_stds.shape[0], len(regrs)])
        X2 = np.concatenate((X2, lupi_feat), axis=1)
        for j in np.arange(len(regrs)):
            X_stds_noj = X_stds.drop(X_stds.columns[j], axis=1)
            X2[:, num_of_std + j] = regrs[j].predict(X_stds_noj)
        # importances of all features
        importances = self._calc_importance_all(X2, y_train, ntree=ntree)
        indices = np.argsort(importances)[::-1]
        # importances of augmented_ features
        im_augmented = importances[augmented_feature_list]
        im_augmented_indices = np.argsort(im_augmented)[::-1]
        # find best scree index
        # sorted array
        #use SCREE to select from autmented features
        scree_index = self._g_scree(im_augmented[im_augmented_indices])
        good_scree_indices = im_augmented_indices[0:scree_index]
        #most important indices
        im_indices = indices[0:num_of_std]
        #find the indices of the good argumented features
        t_indices = im_indices - num_of_std
        good_indices = t_indices[t_indices >=0]
        nregrs = np.asarray(regrs)
        #sel_scree_regrs = nregrs[list(good_scree_indices)]
        # nregrs is np list of mfa regressors
        # good_indices is the list of indices of good mfa_regressor
        # good_scree_indices is the list of indices of good mfa_regressor with scree filter
        return nregrs, good_indices, good_scree_indices

    def _wrap_predictions(self, inputs: Inputs, predictions: ndarray, target_columns_metadata) -> Outputs:
        outputs = d3m_dataframe(predictions, generate_metadata=False)
        outputs.metadata = self._update_predictions_metadata(inputs.metadata, outputs, target_columns_metadata)
        return outputs

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        training_inputs = self._get_columns_to_fit(inputs, self.hyperparams)
        training_inputs = self._data_imputer(training_inputs)
        X_pri, X_std = self._get_pri_std_data(training_inputs)

        transformed = inputs.copy()
        for cln in training_inputs.columns:
            if cln != self._target_name:
                transformed[cln] = training_inputs[cln]

        if len(X_pri) > 0 :
            regressors = self._prifeature_to_regressor
            for pf in regressors.keys():
                transformed[pf] = regressors[pf].predict(X_std)
            transformed.metadata = inputs.metadata
        else:
            num_of_std = self.num_of_std
            (nregrs, good_indices, good_scree_indices) = self._augmented_regrs
            if self._use_scree:
                mfa_indices = good_scree_indices
            else:
                mfa_indices = good_indices

            if len(mfa_indices) > 0:
                for mf in mfa_indices:
                    cln = X_std.columns[mf]
                    X_std_noj = X_std.drop(cln, axis=1)
                    transformed[cln] = nregrs[mf].predict(X_std_noj)

            #transformed.metadata = inputs.metadata
        assert isinstance(transformed, container.DataFrame), type(transformed)

        return base.CallResult(transformed)

    @classmethod
    def _update_metadata(cls, metadata: metadata_base.DataMetadata, resource_id: metadata_base.SelectorSegment) -> metadata_base.DataMetadata:
        resource_metadata = dict(metadata.query((resource_id,)))

        if 'structural_type' not in resource_metadata or not issubclass(resource_metadata['structural_type'], container.DataFrame):
            raise TypeError("The Dataset resource is not a DataFrame, but \"{type}\".".format(
                type=resource_metadata.get('structural_type', None),
            ))

        resource_metadata.update(
            {
                'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            },
        )

        new_metadata = metadata_base.DataMetadata(resource_metadata)

        new_metadata = metadata.copy_to(new_metadata, (resource_id,))

        # Resource is not anymore an entry point.
        new_metadata = new_metadata.remove_semantic_type((), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint')

        return new_metadata

    @classmethod
    def can_accept(cls, *, method_name: str, arguments: typing.Dict[str, typing.Union[metadata_base.Metadata, type]],
                   hyperparams: Hyperparams) -> typing.Optional[metadata_base.DataMetadata]:
        output_metadata = super().can_accept(method_name=method_name, arguments=arguments, hyperparams=hyperparams)

        # If structural types didn't match, don't bother.
        if output_metadata is None:
            return None

        if method_name != 'produce':
            return output_metadata

        if 'inputs' not in arguments:
            return output_metadata

        inputs_metadata = typing.cast(metadata_base.DataMetadata, arguments['inputs'])

        dataframe_resource_id = base_utils.get_tabular_resource_metadata(inputs_metadata, hyperparams['dataframe_resource'])

        return cls._update_metadata(inputs_metadata, dataframe_resource_id)

    @classmethod
    def _get_columns_to_fit(cls, inputs: Inputs, hyperparams: Hyperparams):
        if not hyperparams['use_semantic_types']:
            return inputs, list(range(len(inputs.columns)))

        all_columns = list(range(inputs.metadata.query_field((metadata_base.ALL_ELEMENTS,), 'dimension')['length']))

        # And remove those in "exclude_columns".
        training_columns = [column_index for column_index in all_columns if column_index not in hyperparams['exclude_input_columns']]

        return inputs.iloc[:, training_columns]
        # return columns_to_produce


    @classmethod
    def _can_produce_column(cls, inputs_metadata: metadata_base.DataMetadata, column_index: int,
                            hyperparams: Hyperparams) -> bool:
        column_metadata = inputs_metadata.query((metadata_base.ALL_ELEMENTS, column_index))

        accepted_structural_types = (int, float, numpy.integer, numpy.float64)
        accepted_semantic_types = set()
        accepted_semantic_types.add("https://metadata.datadrivendiscovery.org/types/Attribute")
        if not issubclass(column_metadata['structural_type'], accepted_structural_types):
            return False

        semantic_types = set(column_metadata.get('semantic_types', []))

        if len(semantic_types) == 0:
            cls.logger.warning("No semantic types found in column metadata")
            return False
        # Making sure all accepted_semantic_types are available in semantic_types
        if len(accepted_semantic_types - semantic_types) == 0:
            return True

        return False

    @classmethod
    def _get_targets(cls, data: d3m_dataframe, hyperparams: Hyperparams):
        if not hyperparams['use_semantic_types']:
            return data, list(data.columns), list(range(len(data.columns)))

        metadata = data.metadata

        def can_produce_column(column_index: int) -> bool:
            accepted_semantic_types = set()
            accepted_semantic_types.add("https://metadata.datadrivendiscovery.org/types/TrueTarget")
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = set(column_metadata.get('semantic_types', []))
            if len(semantic_types) == 0:
                cls.logger.warning("No semantic types found in column metadata")
                return False
            # Making sure all accepted_semantic_types are available in semantic_types
            if len(accepted_semantic_types - semantic_types) == 0:
                return True
            return False

        target_column_indices, target_columns_not_to_produce = base_utils.get_columns_to_use(metadata,
                                                                                               use_columns=hyperparams[
                                                                                                   'use_output_columns'],
                                                                                               exclude_columns=
                                                                                               hyperparams[
                                                                                                   'exclude_output_columns'],
                                                                                               can_use_column=can_produce_column)
        targets = []
        if target_column_indices:
            targets = data.select_columns(target_column_indices)
        target_column_names = []
        for idx in target_column_indices:
            target_column_names.append(data.columns[idx])
        return targets, target_column_names, target_column_indices

if __name__ == '__main__':
    import logging
    import pprint
    import sys

    logging.basicConfig()
    #dataset_file_path = "seed_datasets_current/uu4_SPECT/uu4_SPECT_dataset/datasetDoc.json"
    for dataset_file_path in sys.argv[1:]:
        try:
            dataset = container.Dataset.load('file://{dataset_doc_path}'.format(dataset_doc_path=os.path.abspath(dataset_file_path)))
        except Exception as error:
            raise Exception("Unable to load dataset: {dataset_doc_path}".format(dataset_doc_path=dataset_file_path)) from error

        primitive = LupiMFA(hyperparams=Hyperparams.defaults().replace({
            'regressor_type': 'linear',
        }))

        try:
            lupilearned_dataset = primitive.produce(inputs=dataset).value

            pprint.pprint(lupilearned_dataset)
            lupilearned_dataset.metadata.pretty_print()
        except Exception as error:
            raise Exception("Unable to transform dataset: {dataset_doc_path}".format(dataset_doc_path=dataset_file_path)) from error
