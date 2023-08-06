import backspace


class KV:
    def __init__(self, k="", v=""):
        self.k = str(k)
        v_list = [v]
        self.v = v_list

    def add(self, v_add):
        self.v.append(v_add)

    def print(self):
        print(self.k + ":", end="")
        backspace.printl(self.v)
