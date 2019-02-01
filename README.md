# parso utils
Misc utility functions to work with parso ASTs

- is_function_call(node)
- full_function_name(node): Simplifies the case of "foo()" and "foo.bar()" so it's easy to get "foo" and "foo.bar" from the node
- function_call_arguments(node):  Given a function call node returns a dict with:
    - positional: list of positional arguments. These are the argument nodes.
    - kwargs: dict with keyword arguments
    - arg_unpacks: stuff like *foo
    - kwarg_unpacks: stuff like **foo
- walk_code: walk the ASTs of all code in a given directory (defaults to . and ignores some dirs like venv by default), 
  this takes care of recursing through the AST for you, but you can also stop recursion of a node by returning False from your callback
