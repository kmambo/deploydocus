from io import StringIO
from typing import Any, Sequence

import yaml

from ..binutils import helm

# Note: Not yet threadsafe
helm_ver: str = helm["version"]()


def helm_template(
    name: str, chart: str, args: Sequence[str], as_str: bool = False
) -> str | dict[str, Any] | Sequence[dict[str, Any]]:
    """Render a helm chart using the `helm` CLI

    Args:
        args:
        as_str:
        name:
        chart:

    Returns:

    """
    rendered_str: str = helm["template"](name, chart, *args)

    if as_str:
        return rendered_str
    # Now  render as
    with StringIO(rendered_str) as f:
        chart_obj: list[dict[str, Any]] = list(yaml.safe_load_all(f))
    return chart_obj[0] if len(chart_obj) == 1 else chart_obj
