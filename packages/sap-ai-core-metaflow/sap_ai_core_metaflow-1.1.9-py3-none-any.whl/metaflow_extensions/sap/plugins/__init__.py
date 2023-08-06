from .argowf.argo_decorator import ArgoStepDecorator, ArgoInternalStepDecorator


FLOW_DECORATORS = []
STEP_DECORATORS = [ArgoStepDecorator, ArgoInternalStepDecorator]


def get_plugin_cli():
    """Return list of click multi-commands to extend metaflow CLI with argo_workflows."""

    # it is important that CLIs are not imported when
    # __init__ is imported. CLIs may use e.g.
    # parameters.add_custom_parameters which requires
    # that the flow is imported first

    from .argowf.argo_cli import cli

    return [cli]
