class IconFontMeta(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict):
        assert "__font_file__" in namespace, "Font must have a `__font_file__` attr!"
        # update all values to be `key.unicode`
        namespace.update(
            {
                k: f"{name.lower()}.{chr(v) if isinstance(v, int) else v}"
                for k, v in namespace.items()
                if not k.startswith("__")
            }
        )
        namespace["__slots__"] = ()
        return super().__new__(cls, name, bases, namespace)

    def __setattr__(self, key, value):
        raise TypeError("{self!r} is a frozen class")


class IconFont(metaclass=IconFontMeta):
    __font_file__ = "..."
