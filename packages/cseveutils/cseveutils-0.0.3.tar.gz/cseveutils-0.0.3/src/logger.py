class Logger:
    def info(self, message):
        print("INFO" + message)

    def error(self, message):
        print("ERROR" + message)

    def debug(self, message):
        print("DEBUG" + message)

    def warning(self, message):
        print("WARNING" + message)

    def critical(self, message):
        print("CRITICAL" + message)


