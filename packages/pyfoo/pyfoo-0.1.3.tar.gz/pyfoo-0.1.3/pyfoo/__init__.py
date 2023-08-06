import juliacall; jl = juliacall.newmodule("PyFoo")
jl.seval("using FooBase: FooBase")


def py_say_hello(jlstruct):
    jl.FooBase.say_hello(jlstruct)
    return None


def py_eat(jlstruct):
    jl.FooBase.eat(jlstruct)
    return None
