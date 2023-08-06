
def foo(template_var: int):
    """Some function description.

    Parameters
    ----------
    template_var : int
        Some template variable.
    """

    def bar(input_var: int) -> int:
        """Some templated function description.

        Parameters
        ----------
        input_var : int
            Some input variable.

        Returns
        -------
        int
            Output value.
        """
        return template_var + input_var

    return bar


# Yields no docstring popup
foo(5)()
# But if you store the result into a var...
a = foo(5)
# it does show up
a()


