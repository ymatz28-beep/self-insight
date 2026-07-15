"""Section helpers for generate_dashboard.

Modules are split by responsibility. Because the original generator used one shared
global namespace, the package initializer mirrors those globals into each module
after import so moved functions can keep their original bodies unchanged.
"""
from importlib import import_module as _import_module

_MODULE_NAMES = ['utils', 'core_identity', 'navigation', 'monthly', 'divination_forecast', 'ui', 'charts', 'styles', 'glossary', 'eto_cross']
_MODULES = [_import_module(f'.{name}', __name__) for name in _MODULE_NAMES]

def _is_export(name, value):
    if name.startswith('__'):
        return False
    if name in {'json', '_date', 'yaml', '_sys', '_Path', '_get_nav_html'}:
        return False
    return True

_EXPORTS = {}
for _module in _MODULES:
    for _name, _value in vars(_module).items():
        if _is_export(_name, _value):
            _EXPORTS[_name] = _value

for _module in _MODULES:
    vars(_module).update(_EXPORTS)

globals().update(_EXPORTS)
__all__ = sorted(_EXPORTS)
