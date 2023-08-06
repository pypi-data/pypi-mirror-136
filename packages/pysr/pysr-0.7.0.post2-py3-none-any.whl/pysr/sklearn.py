from pysr import pysr, best_row, get_hof
from sklearn.base import BaseEstimator, RegressorMixin
import inspect
import pandas as pd
from copy import deepcopy as copy


class PySRRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, model_selection="accuracy", **params):
        """Initialize settings for pysr.pysr call.

        :param model_selection: How to select a model. Can be 'accuracy' or 'best'. 'best' will optimize a combination of complexity and accuracy.
        :type model_selection: str
        """
        super().__init__()
        self.model_selection = model_selection
        self.params = params

        # Stored equations:
        self.equations = None
        self._pysr_state = None 

    def __repr__(self):
        if self.equations is None:
            return "PySRRegressor.equations = None"

        equations = self.equations
        selected = ["" for _ in range(len(equations))]
        if self.model_selection == "accuracy":
            chosen_row = -1
        elif self.model_selection == "best":
            chosen_row = equations["score"].idxmax()
        else:
            raise NotImplementedError
        selected[chosen_row] = ">>>>"
        output = "PySRRegressor.equations = [\n"
        repr_equations = pd.DataFrame(
            dict(
                pick=selected,
                score=equations["score"],
                Equation=equations["Equation"],
                MSE=equations["MSE"],
                Complexity=equations["Complexity"],
            )
        )
        output += repr_equations.__repr__()
        output += "\n]"
        return output

    def set_params(self, **params):
        """Set parameters for pysr.pysr call or model_selection strategy."""
        for key, value in params.items():
            if key == "model_selection":
                self.model_selection = value
            self.params[key] = value

        return self

    def get_params(self, deep=True):
        del deep
        return {**self.params, "model_selection": self.model_selection}

    def get_best(self):
        if self.equations is None:
            return 0.0
        if self.model_selection == "accuracy":
            return self.equations.iloc[-1]
        elif self.model_selection == "best":
            return best_row(self.equations)
        else:
            raise NotImplementedError

    def fit(self, X, y, weights=None, variable_names=None):
        """Search for equations to fit the dataset.

        :param X: 2D array. Rows are examples, columns are features. If pandas DataFrame, the columns are used for variable names (so make sure they don't contain spaces).
        :type X: np.ndarray/pandas.DataFrame
        :param y: 1D array (rows are examples) or 2D array (rows are examples, columns are outputs). Putting in a 2D array will trigger a search for equations for each feature of y.
        :type y: np.ndarray
        :param weights: Optional. Same shape as y. Each element is how to weight the mean-square-error loss for that particular element of y.
        :type weights: np.ndarray
        :param variable_names: a list of names for the variables, other than "x0", "x1", etc.
        :type variable_names: list
        """
        if variable_names is None:
            if "variable_names" in self.params:
                variable_names = self.params["variable_names"]

        self.equations = pysr(
            X=X,
            y=y,
            weights=weights,
            variable_names=variable_names,
            **{k: v for k, v in self.params.items() if k != "variable_names"},
        )
        from .sr import global_state
        self._pysr_state = copy(global_state)

        return self

    def refresh(self):
        # Updates self.equations with any new options passed,
        # such as extra_sympy_mappings.
        params = copy(self.params)
        # params takes priority over self._pysr_state, but we still pass it
        # to avoid cases where pysr state gets re-defined.
        self._pysr_state.update(params)
        self.equations = get_hof(**self._pysr_state)

    def predict(self, X):
        self.refresh()
        np_format = self.get_best()["lambda_format"]
        return np_format(X)

    def sympy(self):
        self.refresh()
        return self.get_best()["sympy_format"]

    def latex(self):
        self.refresh()
        return self.sympy().simplify()

    def jax(self):
        self.set_params(output_jax_format=True)
        self.refresh()
        return self.get_best()["jax_format"]

    def pytorch(self):
        self.set_params(output_torch_format=True)
        self.refresh()
        return self.get_best()["torch_format"]


# Add the docs from pysr() to PySRRegressor():
_pysr_docstring_split = []
_start_recording = False
for line in inspect.getdoc(pysr).split("\n"):
    # Skip docs on "X" and "y"
    if ":param binary_operators:" in line:
        _start_recording = True
    if ":returns:" in line:
        _start_recording = False
    if _start_recording:
        _pysr_docstring_split.append(line)
_pysr_docstring = "\n\t".join(_pysr_docstring_split)

PySRRegressor.__init__.__doc__ += _pysr_docstring
