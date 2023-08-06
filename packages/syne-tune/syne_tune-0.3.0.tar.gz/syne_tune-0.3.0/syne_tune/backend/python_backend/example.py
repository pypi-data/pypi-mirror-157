def f(x):
    import logging
    from syne_tune import Reporter

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    reporter = Reporter()
    for i in range(5):
        reporter(step=i + 1, y=x + i)


from syne_tune.backend.python_backend.python_backend import PythonBackend
from syne_tune.config_space import uniform

config_space = {"x": uniform(-10, 10)}
backend = PythonBackend(tune_function=f, config_space=config_space)
