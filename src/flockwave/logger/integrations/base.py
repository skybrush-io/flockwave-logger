from abc import ABC, abstractmethod
from contextlib import contextmanager
from importlib import import_module
from typing import ClassVar, Iterator

__all__ = ("Integration",)


class Integration(ABC):
    """Object that knows how to integrate our logger with third-party packages."""

    @abstractmethod
    def requirements_met(self) -> bool:
        """Returns whether the requirements are met to execute this integration."""
        ...

    @abstractmethod
    def install(self, level: int) -> None:
        """Installs the integration."""
        ...

    def uninstall(self) -> None:
        """Uninstalls the integration."""
        raise NotImplementedError

    @contextmanager
    def use(self, level: int) -> Iterator[None]:
        """Installs the integration when the execution is in the context and
        uninstalls it upon exiting the context.
        """
        try:
            self.install(level)
            yield
        finally:
            self.uninstall()


class PackageIntegration(Integration):
    """Integration that is provided for a single Python package."""

    package_name: ClassVar[str]

    def requirements_met(self) -> bool:
        try:
            import_module(self.package_name)
        except ImportError:
            return False
        else:
            return True
