import tempfile
import time

from syne_tune import Tuner, StoppingCriterion
from syne_tune.backend.python_backend.python_backend import PythonBackend
from syne_tune.backend.trial_status import Status
from syne_tune.config_space import randint, uniform
from syne_tune.optimizer.baselines import ASHA


def f(x):
    import logging
    from syne_tune import Reporter

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    reporter = Reporter()
    for i in range(5):
        reporter(step=i + 1, y=x + i)


def wait_until_all_trials_completed(backend):
    def status(backend, trial_ids):
        return [trial.status for trial in backend._all_trial_results(trial_ids)]

    i = 0
    while not all(
        [status == Status.completed for status in status(backend, backend.trial_ids)]
    ):
        time.sleep(0.1)
        assert i < 100, "backend trials did not finish after 10s"


def launch_backend():
    with tempfile.TemporaryDirectory() as local_path:
        backend = PythonBackend(f, config_space={"x": randint(0, 10)})
        backend.set_path(local_path)
        backend.start_trial({"x": 2})
        backend.start_trial({"x": 3})

        wait_until_all_trials_completed(backend)

        trials, metrics = backend.fetch_status_results([0, 1])

        metrics_first_trial = [metric["y"] for x, metric in metrics if x == 0]
        metrics_second_trial = [metric["y"] for x, metric in metrics if x == 1]
        assert metrics_first_trial == [2, 3, 4, 5, 6]
        assert metrics_second_trial == [3, 4, 5, 6, 7]


def launch_tuning():
    config_space = {"x": uniform(-10, 10)}
    backend = PythonBackend(f, config_space=config_space)
    tuner = Tuner(
        trial_backend=backend,
        scheduler=ASHA(
            config_space=config_space, metric="y", resource_attr="step", max_t=5
        ),
        stop_criterion=StoppingCriterion(max_wallclock_time=60),
        n_workers=4,
    )
    tuner.run()


if __name__ == "__main__":
    import logging

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    launch_backend()

    launch_tuning()
