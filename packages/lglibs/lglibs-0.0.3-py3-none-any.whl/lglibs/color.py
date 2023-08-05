class color:
    class __black:
        def __str__(self):
            return "\033[90m"
        normal = "\033[30m"
        dark = "\033[2;30m"
    class __red:
        def __str__(self):
            return "\033[91m"
        normal = "\033[31m"
        dark = "\033[2;31m"
    class __green:
        def __str__(self):
            return "\033[92m"
        normal = "\033[32m"
        dark = "\033[2;32m"
    class __yellow:
        def __str__(self):
            return "\033[93m"
        normal = "\033[33m"
        dark = "\033[2;33m"
    class __blue:
        def __str__(self):
            return "\033[94m"
        normal = "\033[34m"
        dark = "\033[2;34m"
    class __purple:
        def __str__(self):
            return "\033[95m"
        normal = "\033[35m"
        dark = "\033[2;35m"
    class __cyan:
        def __str__(self):
            return "\033[96m"
        normal = "\033[36m"
        dark = "\033[2;36m"
    class __white:
        def __str__(self):
            return "\033[97m"
        normal = "\033[37m"
        dark = "\033[2;37m"
        
    off = "\033[0m"
    black = __black()
    red = __red()
    green = __green()
    yellow = __yellow()
    blue = __blue()
    purple = __purple()
    cyan = __cyan()
    white = __white()
    def toning(R:int = 0, G:int = 0, B:int = 0):
        return f"\033[38;2;{R};{G};{B}m"

    def string_addtoning():
        import builtins
        class toningit(str):
            def toning(self, R:int = 0, G:int = 0, B:int = 0):
                return f"\033[38;2;{R};{G};{B}m" + self + "\033[0m"
        builtins.str = toningit







