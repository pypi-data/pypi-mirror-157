# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import functools
import traceback

from fsc.export import export


@export
def check_workchain_step(func):
    """
    Decorator for workchain steps that logs (and re-raises) errors occuring within that step.
    """

    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.report(
                f"{type(e).__name__} in {func.__name__}: {e}.\nTraceback:\n{traceback.format_exc()}"
            )
            raise e

    return inner
