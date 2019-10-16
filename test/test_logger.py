def main():
    import logging
    from flockwave.logger import install, log

    install()

    log.setLevel(logging.DEBUG)

    log.debug("test debug")
    log.info("test info")
    log.warning("test warning")
    log.error("test error")
    log.fatal("test fatal error")

    log.info("test entry with ID", extra={"id": "spam"})

    log.info("test success", extra={"semantics": "success"})
    log.info("test failure", extra={"semantics": "failure"})
    log.info("test request", extra={"semantics": "request"})
    log.info("test successful response", extra={"semantics": "response_success"})
    log.info("test error response", extra={"semantics": "response_error"})
    log.info("test notification", extra={"semantics": "notification"})


if __name__ == "__main__":
    main()
