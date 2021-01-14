def main():
    import logging
    from flockwave.logger import install, log, log_hexdump

    install(style="json")

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

    log_hexdump(log, b"\xde\xad\xbe\xef", address="123", direction="out")
    log_hexdump(
        log,
        b"\x0b\xad\xca\xfe\x0b\xad\xca\xfe\x0b\xad\xca\xfe\x0b\xad\xca\xfe\x0b\xad\xca\xfe",
        address="123",
        direction="in",
    )


if __name__ == "__main__":
    main()
