
def SomeClass(some_number: int):

    class _SomeClass:

        def __init__(self, other_number: int) -> None:
            self._other_number = other_number
            return

        def Print(self):
            print(some_number + self._other_number)
            return

    return _SomeClass

some_templated_class = SomeClass(5)(10)
some_templated_class.Print()




