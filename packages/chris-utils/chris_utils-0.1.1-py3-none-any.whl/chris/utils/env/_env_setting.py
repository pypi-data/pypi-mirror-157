import os
from typing import Any, Optional


class EnvSetting:
    """Setting backed by an environment variable."""

    def __init__(self, variable: str, default: Optional[Any] = None, optional: bool = True):
        """Construct an EnvSetting."""
        self._variable = variable
        self._default = default
        self._optional = optional

    @property
    def var(self):
        """Get the variable name property."""
        return self._variable

    @property
    def default(self):
        """Get the default variable value property."""
        return self._default

    @property
    def value(self):
        """Get the variable value property."""
        variable_value = os.getenv(self._variable, self._default)
        if variable_value is None and not self._optional:
            raise EnvironmentError(
                f"Environment variable {self.var} is not set")
        return variable_value
