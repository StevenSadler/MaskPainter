class Utils:

    @staticmethod
    def is_hex_color(string):
        if string[0] == '#':
            string = string[1:]
        if len(string) == 3 or len(string) == 6:
            try:
                _ = int(string, 16)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def do_nothing():
        print("do nothing")
