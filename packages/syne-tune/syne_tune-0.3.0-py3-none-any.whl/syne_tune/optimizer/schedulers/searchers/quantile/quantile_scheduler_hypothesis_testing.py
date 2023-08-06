from collections import defaultdict
from typing import Dict, Optional, List
import numpy as np
import scipy
import xgboost
from sklearn.model_selection import train_test_split

from syne_tune.backend.trial_status import Trial
from syne_tune.blackbox_repository.blackbox_surrogate import BlackboxSurrogate
from syne_tune.config_space import Domain, uniform
from syne_tune.constants import ST_TUNER_TIME
from syne_tune.experiments import load_experiment
from syne_tune.optimizer.scheduler import (
    TrialScheduler,
    SchedulerDecision,
    TrialSuggestion,
)
from syne_tune.optimizer.schedulers.searchers import impute_points_to_evaluate
from syne_tune.optimizer.schedulers.searchers.bayesopt.datatypes.hp_ranges_factory import (
    make_hyperparameter_ranges,
)
from syne_tune.optimizer.schedulers.searchers.quantile.quantile_streaming import (
    QuantileStreaming,
)
from syne_tune.util import catchtime

"""
TODO:
o fit mean model
o exploit mean model
x probabilistic decision
"""


def fit_model(
    X,
    y,
    max_fit_samples: int,
    random_state,
    model=None,
):
    if model is None:
        model = xgboost.XGBRegressor()
    # with catchtime("time to fit the model"):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.1, random_state=random_state
    )
    X_train, y_train = subsample(
        X_train, y_train, max_samples=max_fit_samples, random_state=random_state
    )
    model.fit(X_train, y_train)

    # compute residuals (num_metrics,)
    sigma_train = eval_model(model, X_train, y_train)

    # compute residuals (num_metrics,)
    sigma_val = eval_model(model, X_test, y_test)

    return model, sigma_train, sigma_val


def eval_model(model_pipeline, X, y):
    # compute residuals (num_metrics,)
    mu_pred = model_pipeline.predict(X)
    if mu_pred.ndim == 1:
        mu_pred = mu_pred.reshape(-1, 1)
    res = np.std(y - mu_pred, axis=0)
    return res.mean()


def subsample(
    X_train,
    z_train,
    max_samples: int = 10000,
    random_state: np.random.RandomState = None,
):
    assert len(X_train) == len(z_train)
    if max_samples is not None and max_samples < len(X_train):
        if random_state is None:
            random_indices = np.random.permutation(len(X_train))[:max_samples]
        else:
            random_indices = random_state.permutation(len(X_train))[:max_samples]
        X_train = X_train.loc[random_indices]
        z_train = z_train[random_indices]
    return X_train, z_train


class QuantileScheduler(TrialScheduler):
    def __init__(
        self,
        config_space: Dict,
        metric: str,
        mode: str = "min",
        random_seed: int = None,
        surrogate: bool = False,
        points_to_evaluate: Optional[List[Dict]] = None,
    ):
        super(QuantileScheduler, self).__init__(config_space=config_space)
        self.mode = mode
        self.metric = metric
        self.random_state = np.random.RandomState(seed=random_seed)
        self.trial_results = defaultdict(list)  # list of results for each trials
        self.time_to_rank = defaultdict(lambda: QuantileStreaming())
        self.pending_trials = set()
        self.trial_configs = {}
        self.hp_ranges = make_hyperparameter_ranges(config_space=config_space)
        self.grace_period = 1
        self._points_to_evaluate = impute_points_to_evaluate(
            points_to_evaluate, config_space
        )
        self.surrogate = surrogate

        self.best_rank_trial = None
        self.best_rank = 1
        self.best_ranks = None

    def _suggest(self, trial_id: int) -> Optional[TrialSuggestion]:
        if self._points_to_evaluate:
            config = self._points_to_evaluate.pop(0)
        else:
            if self.surrogate and len(self.trial_results) > 10:
                trial_ranks = self.ranks()
                X = np.array(
                    [
                        self.hp_ranges.to_ndarray(self.trial_configs[trial_id])
                        for trial_id in trial_ranks.keys()
                    ]
                )
                z = np.array(
                    [np.mean(ranks) for trial_id, ranks in trial_ranks.items()]
                )
                model_pipeline, sigma_train, sigma_val = fit_model(
                    X=X,
                    y=z,
                    random_state=self.random_state,
                    max_fit_samples=10000,
                )
                if sigma_val < 1:
                    config_test = [self.sample_random() for _ in range(1000)]
                    X_test = np.array(
                        [self.hp_ranges.to_ndarray(config) for config in config_test]
                    )
                    mu_pred = model_pipeline.predict(X_test)
                    sigma_pred = np.ones_like(mu_pred) * sigma_val
                    samples = np.random.normal(mu_pred, sigma_pred)
                    if self.mode == "max":
                        samples *= -1
                    config_idx = np.argmin(samples)
                    config = config_test[config_idx]
                else:
                    self.sample_random()
            else:
                config = self.sample_random()

        self.trial_configs[trial_id] = config
        return TrialSuggestion.start_suggestion(config=config)

    def sample_random(self) -> Dict:
        return {
            k: v.sample(random_state=self.random_state) if isinstance(v, Domain) else v
            for k, v in self.config_space.items()
        }

    @staticmethod
    def stat_test_worse_than_top_distribution(sample_ranks: np.array, quantile: float):
        """
        Checks that the values provided are worse than best configurations by performing a
        statistical test that the distribution mean of `Phi{-1}(u), u \in sample_ranks` is above
        than `Phi{-1}(quantile)`.
        :param sample_ranks:
        :param quantile:
        :return:
        """
        assert len(sample_ranks) > 1
        assert 0 < quantile < 1
        assert np.min(sample_ranks) >= 0
        assert np.max(sample_ranks) <= 1
        z_value = scipy.stats.norm.ppf(quantile)

        # Winsorized cutoff
        delta = 1.0 / (
            4.0 * len(sample_ranks) ** 0.25 * np.sqrt(np.pi * np.log(len(sample_ranks)))
        )

        z_samples = scipy.stats.norm.ppf(
            np.clip(sample_ranks, min(delta, quantile), 1 - delta)
        )

        _, pvalue = scipy.stats.mstats.ttest_1samp(
            z_samples,
            popmean=z_value,
            alternative="greater",
        )
        # print(z_value, z_samples, pvalue)
        if np.isnan(pvalue):
            return False, pvalue
        else:
            return pvalue < 0.05, pvalue

    def on_trial_result(self, trial: Trial, result: Dict) -> str:
        trial_id = trial.trial_id
        y = result[self.metric]
        if self.mode == "max":
            y *= -1
        t = len(self.trial_results[trial_id])
        self.time_to_rank[t].add(y)
        self.trial_results[trial_id].append(y)

        enough_observations = t >= self.grace_period
        if enough_observations:
            trial_ranks = self.trial_ranks(trial_id=trial_id)
            if len(trial_ranks) > enough_observations:
                (
                    worse_than_top_configs,
                    pvalue,
                ) = self.stat_test_worse_than_top_distribution(
                    sample_ranks=trial_ranks,
                    quantile=0.5,
                )
                if worse_than_top_configs:
                    # print(f"trial {trial_id} worse than top config: {pvalue}")
                    # print(f"ranks: {list(self.trial_ranks(trial_id=trial_id))}")
                    return SchedulerDecision.STOP
            return SchedulerDecision.CONTINUE
        else:
            if self.time_to_rank[t].rank(y) > 0.5:
                return SchedulerDecision.STOP
            else:
                return SchedulerDecision.CONTINUE

    def ranks(self) -> Dict[int, List]:
        return {
            trial_id: self.trial_ranks(trial_id=trial_id)
            for trial_id in self.trial_results.keys()
        }

    def trial_ranks(self, trial_id: int) -> np.array:
        ranks = []
        min_rank_population = 1
        for t, y in enumerate(self.trial_results[trial_id]):
            if len(self.time_to_rank[t]) > min_rank_population:
                ranks.append(self.time_to_rank[t].rank(y, normalized=True))
        ranks = np.array(ranks)
        # Les derniers seront les premiers
        return ranks

    def fit_model(self, X, z):
        pass

    def predict(self, X):
        pass

    def metric_names(self) -> List[str]:
        return [self.metric]

    def metric_mode(self) -> str:
        return self.mode


def check_quantile_scheduler():
    config_space = {"x": uniform(0, 1), "y": uniform(0, 1)}
    sch = QuantileScheduler(config_space=config_space, metric="error", random_seed=0)

    configs = []
    n_trials = 8
    n_steps = 3
    for i in range(n_trials):
        configs.append(sch.suggest(i))

    for t in range(n_steps):
        for i in range(n_trials):
            decision = sch.on_trial_result(
                Trial(i, config=configs[i], creation_time=None), result={"error": i - t}
            )
            print(i, t, decision)
    for t in range(n_steps, n_steps * 2):

        decision = sch.on_trial_result(
            Trial(0, config=configs[0], creation_time=None), result={"error": 0 - t}
        )

    print(sch.trial_results)
    #
    ranks = sch.ranks()
    print(ranks)
    # # assert {0: [0.25] * n_steps, 1: [0.5] * n_steps, 2: [0.75] * n_steps, 3: [1.] * n_steps} == ranks
    #
    for vec, expected in [
        ([0.0, 0.0, 0.0], False),
        ([0.0, 0.1, 0.3], False),
        ([0.51, 0.52], True),
        ([0.1, 0.05, 0.2, 0.1], False),
        ([0.6, 0.55, 0.62], True),
    ]:
        is_worse, pvalue = QuantileScheduler.stat_test_worse_than_top_distribution(
            sample_ranks=np.array(vec), quantile=0.1
        )
        print(vec, is_worse)
        print("--")
        assert is_worse == expected


def run():
    import matplotlib.pyplot as plt
    from benchmarking.nursery.benchmark_automl.benchmark_main import run

    method = "QHB"
    # benchmark = 'lcbench-airlines'
    benchmark = "nas201-cifar10"
    num_seeds = 1
    exp_names = run(
        method_names=[method],
        benchmark_names=[benchmark],
        seeds=list(range(num_seeds)),
        experiment_tag="yo",
    )

    exp = load_experiment(exp_names[0])
    df = exp.results
    metric = exp.metric_names()[0]
    fig, ax = plt.subplots()
    for trial_id in sorted(df.trial_id.unique()):
        df_trial = df.loc[df.trial_id == trial_id]
        ax.plot(df_trial[ST_TUNER_TIME], df_trial[metric], label=trial_id)
    plt.show()
    # if log_scale:
    #   ax.set_yscale("log")


if __name__ == "__main__":
    check_quantile_scheduler()

    # run()
