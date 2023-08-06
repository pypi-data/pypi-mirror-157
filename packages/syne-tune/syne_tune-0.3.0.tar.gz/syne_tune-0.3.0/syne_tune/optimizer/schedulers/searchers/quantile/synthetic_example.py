from syne_tune.optimizer.schedulers.transfer_learning import (
    TransferLearningTaskEvaluations,
)
from syne_tune.optimizer.schedulers import HyperbandScheduler, FIFOScheduler
from syne_tune.optimizer.schedulers.searchers.quantile.quantile_searcher import (
    QuantileSearcher,
)
import logging

from syne_tune.blackbox_repository import add_surrogate, UserBlackboxBackend
from syne_tune.blackbox_repository.blackbox_tabular import BlackboxTabular

from syne_tune.backend.simulator_backend.simulator_callback import SimulatorCallback
from syne_tune.optimizer.baselines import ASHA
from syne_tune import StoppingCriterion, Tuner
from syne_tune.experiments import load_experiment

from syne_tune.config_space import uniform, randint
from syne_tune.blackbox_repository.blackbox_tabular import BlackboxTabular
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

logging.getLogger().setLevel(logging.INFO)

mode = "min"

do_transfer_learning = True
n_workers = 4
n = 200
x = np.random.rand(n)
x.sort()

y1 = (x - 1 / 4) ** 2
y2 = (x - 3 / 4) ** 2
y = y1 * (x <= 0.5) + y2 * (x > 0.5)

if mode == "max":
    y *= -1

plt.plot(x, y)
plt.show()
num_epochs = 50
y_t = np.zeros((n, num_epochs))
for i in range(n):
    alpha = 0.5
    beta = y[i]
    noise = np.random.normal(size=num_epochs) * np.mean(y)
    y_t[i] = -alpha * np.log1p(np.arange(num_epochs)) + 20 * beta + noise

#     if i < 10:
#         plt.plot(y_t[i])
# plt.show()


configuration_space = {"x": uniform(0, 1)}
fidelity_space = {"epoch": randint(1, num_epochs)}
df_hyperparameters = pd.DataFrame(x, columns=["x"])

# (n_samples, n_seeds, n_fidelities, 1)
objective_evaluations = y_t.reshape((n, 1, num_epochs, 1))

# (n_samples, n_fidelities)
time_evaluations = np.ones((n, 1)) * np.arange(1, num_epochs + 1).reshape(1, -1)
# (n_samples, n_seeds, n_fidelities, 1)
time_evaluations = time_evaluations.reshape(n, 1, num_epochs, 1)

# (n_samples, n_seeds, n_fidelities, 2)
objective_evaluations = np.concatenate(
    [objective_evaluations, time_evaluations], axis=-1
)

error_metric = "error"
time_metric = "time"
blackbox = BlackboxTabular(
    hyperparameters=df_hyperparameters,
    configuration_space=configuration_space,
    fidelity_space=fidelity_space,
    objectives_evaluations=objective_evaluations,
    fidelity_values=np.arange(1, num_epochs + 1),
    objectives_names=[error_metric, time_metric],
)

# # Random search without stopping
# scheduler = ASHA(
#     blackbox.configuration_space,
#     max_t=max(blackbox.fidelity_values),
#     resource_attr=next(iter(blackbox.fidelity_space.keys())),
#     mode='min',
#     metric=error_metric,
#     random_seed=1
# )
searcher = QuantileSearcher(
    metric=error_metric,
    mode=mode,
    config_space=blackbox.configuration_space,
    transfer_learning_evaluations={
        "task": TransferLearningTaskEvaluations(
            hyperparameters=blackbox.hyperparameters,
            configuration_space=blackbox.configuration_space,
            objectives_evaluations=blackbox.objectives_evaluations[..., 0:1],
            objectives_names=[error_metric],
        )
    }
    if do_transfer_learning
    else None,
)
searcher.plot = True
scheduler = HyperbandScheduler(
    config_space=blackbox.configuration_space,
    searcher=searcher,
    mode=mode,
    metric=error_metric,
    max_t=max(blackbox.fidelity_values),
    type="stopping",
    resource_attr=next(iter(blackbox.fidelity_space.keys())),
    random_seed=1,
)

# scheduler = FIFOScheduler(
#     config_space=blackbox.configuration_space,
#     searcher=searcher,
#     mode=mode,
#     metric=error_metric,
#     random_seed=1,
# )

stop_criterion = StoppingCriterion(max_wallclock_time=2000)
trial_backend = UserBlackboxBackend(
    blackbox=add_surrogate(blackbox),
    elapsed_time_attr="time",
)

tuner = Tuner(
    trial_backend=trial_backend,
    scheduler=scheduler,
    stop_criterion=stop_criterion,
    n_workers=n_workers,
    sleep_time=0,
    callbacks=[SimulatorCallback()],
)
tuner.run()


load_experiment(tuner.name).plot()
