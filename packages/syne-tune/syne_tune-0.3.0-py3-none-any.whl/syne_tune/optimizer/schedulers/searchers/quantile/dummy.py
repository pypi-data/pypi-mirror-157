import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from syne_tune.optimizer.schedulers.searchers.quantile.quantile_searcher import (
    XGBoostModel,
)
import xgboost
from syne_tune.optimizer.schedulers.transfer_learning.quantile_based.quantile_based_searcher import (
    extract_input_output,
    fit_model,
    subsample,
)
from syne_tune.optimizer.schedulers.transfer_learning import (
    TransferLearningTaskEvaluations,
)
from syne_tune.blackbox_repository import load

benchmark = "fcnet"
task = "protein_structure"

# load blackbox and convert to data format
bb_dict = load(benchmark)
assert task in bb_dict
config_space = next(iter(bb_dict.values())).configuration_space

transfer_learning_evaluations = {
    task: TransferLearningTaskEvaluations(
        hyperparameters=blackbox.hyperparameters,
        configuration_space=blackbox.configuration_space,
        objectives_evaluations=blackbox.objectives_evaluations[..., 0:1],
        objectives_names=blackbox.objectives_names[0:1],
    )
    for task, blackbox in bb_dict.items()
}

# todo keep only test task
task_evals = {k: v for k, v in transfer_learning_evaluations.items() if k == task}
X, y = extract_input_output(
    transfer_learning_evaluations=task_evals,
    normalization="gaussian",
    random_state=None,
)


def fit_eval_model(X, y, model_cls, max_samples: int):

    model = model_cls(config_space=bb_dict[task].configuration_space)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    X_train, y_train = subsample(
        X_train,
        y_train,
        max_samples=max_samples,
    )
    model.fit(X_train, y_train)
    mu, sigma = model.predict(X_test)
    y_test = y_test.reshape(-1)
    assert mu.shape == y_test.shape

    rmse = np.sqrt(np.mean((y_test.reshape(-1) - mu) ** 2))
    calib = ...

    return {"rmse": rmse, "calib": rmse}


from syne_tune.optimizer.schedulers.searchers.quantile.quantile_searcher import GPModel
from syne_tune.util import catchtime

num_seeds = 5
models = {
    "GP": GPModel,
    "XGBoost": XGBoostModel,
}
list_max_samples = [
    1280,
]
rows = []
for seed in range(num_seeds):
    for max_samples in list_max_samples:
        for model_name, model_cls in models.items():
            print(model_name, max_samples)
            runtime_dict = {}
            with catchtime(model_name, runtime_dict):
                row = fit_eval_model(X, y, model_cls, max_samples=max_samples)
            row["max_samples"] = max_samples
            row["seed"] = seed
            row["model"] = model_name
            row["runtime"] = next(iter(runtime_dict.values()))
            rows.append(row)

df = pd.DataFrame(rows)
dd = df.groupby(["max_samples", "model"]).agg(["mean", "std"])["rmse"]
ax = dd["mean"].unstack().plot(kind="bar", yerr=dd["std"].unstack())
ax.set_title("RMSE in function of number of samples for different models")
ax.set_xlabel("Number of samples")
ax.set_ylabel("Runtime (s)")

dd = df.groupby(["max_samples", "model"]).agg(["mean", "std"])["runtime"]
ax = dd["mean"].unstack().plot(kind="bar", yerr=dd["std"].unstack())
ax.set_title("Runtime in function of number of samples for different models")
ax.set_xlabel("Number of samples")
ax.set_ylabel("Runtime (s)")
