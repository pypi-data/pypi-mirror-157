import numpy as np
import xgboost
from xgboost import XGBRegressor

from syne_tune.blackbox_repository import load
from syne_tune.optimizer.schedulers.searchers.bayesopt.datatypes.hp_ranges_factory import (
    make_hyperparameter_ranges,
)
from syne_tune.optimizer.schedulers.transfer_learning import (
    TransferLearningTaskEvaluations,
)
from syne_tune.optimizer.schedulers.transfer_learning.quantile_based.normalization_transforms import (
    GaussianTransform,
)
from syne_tune.optimizer.schedulers.transfer_learning.quantile_based.quantile_based_searcher import (
    fit_model,
    extract_input_output,
    eval_model,
)
from syne_tune.util import catchtime

bb_dict = load("fcnet")
max_fit_samples = 10000
config_space = next(iter(bb_dict.values())).configuration_space


with catchtime("fit1"):
    transfer_learning_evaluations = {
        task: TransferLearningTaskEvaluations(
            hyperparameters=blackbox.hyperparameters,
            configuration_space=blackbox.configuration_space,
            objectives_evaluations=blackbox.objectives_evaluations[..., 0:1],
            objectives_names=blackbox.objectives_names[0:1],
        )
        for task, blackbox in bb_dict.items()
    }

    X, y = extract_input_output(
        transfer_learning_evaluations=transfer_learning_evaluations,
        normalization="gaussian",
        random_state=None,
    )
    model_pipeline, sigma_train, sigma_val = fit_model(
        config_space=config_space,
        X=X,
        y=y,
        max_fit_samples=max_fit_samples,
        model=xgboost.XGBRegressor(),
        random_state=np.random.RandomState(0),
    )
    print(sigma_train, sigma_val)


## approach 2
with catchtime("featurize"):
    hp_ranges = make_hyperparameter_ranges(config_space=config_space)
    Xs = []
    ys = []
    for task_name, transfer_evals in transfer_learning_evaluations.items():
        # (n_samples, n_seeds, n_fidelities, n_objectives)
        y_evals = transfer_evals.objectives_evaluations

        # (n_samples, n_fidelities) by taking average over seeds and first objective
        y_evals = y_evals.mean(axis=1)[..., -1]

        # (n_samples, ) takes average over all fidelities
        z_evals = (
            GaussianTransform(random_state=None, y=y_evals)
            .transform(y_evals)
            .mean(axis=-1)
        )

        hp_df = transfer_evals.hyperparameters[list(config_space.keys())]

        for hp, z in zip(hp_df.values, z_evals):
            hp_dict = dict(zip(hp_df.columns, hp))
            Xs.append(hp_ranges.to_ndarray(hp_dict))
            ys.append(z)
    X = np.stack(Xs)
    y = np.stack(ys)
    y = y.reshape(-1, 1)
random_indices = np.random.permutation(len(X))[:max_fit_samples]
X = X[random_indices]
y = y[random_indices]

model = XGBRegressor()
with catchtime("fit"):
    model.fit(X, y)

with catchtime("pred"):
    # compute residuals (num_metrics,)
    sigma_train = eval_model(model, X, y)

print(sigma_train)
