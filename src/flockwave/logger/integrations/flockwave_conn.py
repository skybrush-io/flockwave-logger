from functools import partial

import logging

from .base import PackageIntegration


class FlockwaveConnIntegration(PackageIntegration):
    package_name = "flockwave.connections"

    def install(self, level: int = logging.INFO):
        """Installs a logging middleware in ``flockwave.connections.create_connection``
        if the ``flockwave-conn`` package is installed.
        """
        from flockwave.connections import create_connection
        from flockwave.connections.middleware import LoggingMiddleware
        from flockwave.logger.utils import create_extra_args_for_logging_traffic

        logger = logging.getLogger("flockwave.connections.conn_log")

        in_extra = create_extra_args_for_logging_traffic(direction="in")
        out_extra = create_extra_args_for_logging_traffic(direction="out")

        in_writer = partial(logger.log, level, extra=in_extra)
        out_writer = partial(logger.log, level, extra=out_extra)

        middleware = LoggingMiddleware.create(writer=(in_writer, out_writer))
        create_connection.register_middleware("log", middleware)
