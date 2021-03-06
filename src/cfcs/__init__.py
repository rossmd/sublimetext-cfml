from .cfcs import build_project_cfcs
from .completions import get_dot_completions
from .documentation import get_inline_documentation, get_goto_cfml_file
from .di import CfmlDiPropertyCommand
from .. import completions, inline_documentation, goto_cfml_file, model_index

completions.add_completion_source('dot', get_dot_completions)
inline_documentation.add_documentation_source(get_inline_documentation)
goto_cfml_file.add_goto_source(get_goto_cfml_file)
model_index.subscribe(build_project_cfcs)
