from .base import Integration

__all__ = ("Integration", "install_integrations")


def install_integrations(level: int) -> None:
    from .flockwave_conn import FlockwaveConnIntegration

    integrations: list[Integration] = [FlockwaveConnIntegration()]

    for integration in integrations:
        if integration.requirements_met():
            integration.install(level)
