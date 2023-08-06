# -*- coding: utf-8 -*-
import builtins


class ExtendedDict(dict):
    def get_nested(self, *args):
        """ Recursive access of nested dictionary. """
        if not self:
            raise KeyError("Dictionary is empty")

        if not args or len(args) < 1:
            raise ValueError("No arguments were provided")

        # I don't remmember what edge case this was supposed
        # to capture but I will temporarilly keep it here.
        # if not (element := args[0]):
        #     return None

        value = self.get(args[0])

        return value if len(args) == 1 else \
            dict(value).get_nested(*args[1:])


builtins.dict = ExtendedDict
