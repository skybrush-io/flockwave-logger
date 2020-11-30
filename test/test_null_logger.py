def main():
    import logging
    from flockwave.logger import NullLogger

    log = NullLogger()

    log.setLevel(logging.DEBUG)

    log.debug("test debug")
    log.info("test info")
    log.warning("test warning")
    log.error("test error")
    log.fatal("test fatal error")


if __name__ == "__main__":
    main()
