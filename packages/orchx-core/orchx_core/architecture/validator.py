import os
import ast
import inspect
import importlib
import pkgutil
import typing
from collections import defaultdict
from typing import List, Dict, Set, Any, Type, Optional

class ArchitectureError(Exception):
    pass

class ArchitectureConsistencyValidator:
    def __init__(self, core_pkg: str = "orchx_core.interfaces", runtime_pkg: str = "orchx_runtime"):
        self.core_pkg = core_pkg
        self.runtime_pkg = runtime_pkg
        self.errors: List[str] = []

    def validate_all(self) -> bool:
        self.errors = []
        self._validate_circular_dependencies()
        self._validate_implementations()
        return len(self.errors) == 0

    def _validate_circular_dependencies(self):
        """Builds a dependency graph and checks for cycles."""
        import importlib.util
        try:
            spec = importlib.util.find_spec(self.runtime_pkg)
            if not spec or not spec.submodule_search_locations:
                return
            base_dir = spec.submodule_search_locations[0]
        except Exception:
            return

        graph = defaultdict(list)
        
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, base_dir)
                    module_name = self.runtime_pkg + '.' + rel_path.replace(os.sep, '.')[:-3]
                    if module_name.endswith('.__init__'):
                        module_name = module_name[:-9]

                    with open(path, 'r', encoding='utf-8') as f:
                        try:
                            tree = ast.parse(f.read(), filename=path)
                        except SyntaxError:
                            continue

                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    if alias.name.startswith(self.runtime_pkg):
                                        graph[module_name].append(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module and node.module.startswith(self.runtime_pkg):
                                    graph[module_name].append(node.module)
                                elif node.level > 0:
                                    # relative imports
                                    # this is a simple approximation
                                    parts = module_name.split('.')
                                    if len(parts) >= node.level:
                                        base_mod = '.'.join(parts[:-node.level])
                                        if node.module:
                                            dep_mod = base_mod + '.' + node.module
                                        else:
                                            dep_mod = base_mod
                                        graph[module_name].append(dep_mod)

        # cycle detection
        visited = set()
        stack = set()
        
        def visit(node: str, path: List[str]):
            visited.add(node)
            stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor in stack:
                    cycle = path[path.index(neighbor):] + [neighbor]
                    self.errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
                elif neighbor not in visited:
                    visit(neighbor, path)
            
            stack.remove(node)
            path.pop()

        for node in list(graph.keys()):
            if node not in visited:
                visit(node, [])

    def _validate_implementations(self):
        """Validate that all runtime classes inheriting from core ABCs implement them properly."""
        try:
            core_mod = importlib.import_module(self.core_pkg)
            runtime_mod = importlib.import_module(self.runtime_pkg)
        except ImportError as e:
            self.errors.append(f"Could not import modules: {e}")
            return
            
        core_classes = {}
        # load all submodules of core_pkg
        for importer, modname, ispkg in pkgutil.walk_packages(core_mod.__path__, core_mod.__name__ + "."):
            try:
                mod = importlib.import_module(modname)
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if obj.__module__ == modname:
                        core_classes[obj] = modname
            except Exception:
                pass
                
        # find implementations in runtime
        runtime_classes = []
        for importer, modname, ispkg in pkgutil.walk_packages(runtime_mod.__path__, runtime_mod.__name__ + "."):
            try:
                mod = importlib.import_module(modname)
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if obj.__module__ == modname:
                        runtime_classes.append(obj)
            except Exception:
                pass
                
        for r_cls in runtime_classes:
            for base in r_cls.__bases__:
                if base in core_classes:
                    self._check_class_compliance(base, r_cls)
                    
    def _check_class_compliance(self, abc_cls: Type, impl_cls: Type):
        if inspect.isabstract(impl_cls):
            return

        # ABC abstract methods check
        if getattr(impl_cls, "__abstractmethods__", None):
            missing = list(impl_cls.__abstractmethods__)
            self.errors.append(f"{impl_cls.__name__} fails to implement abstract methods from {abc_cls.__name__}: {missing}")
            
        # check type hints for overridden methods
        for name, method in inspect.getmembers(abc_cls, inspect.isfunction):
            if hasattr(impl_cls, name):
                impl_method = getattr(impl_cls, name)
                
                try:
                    abc_sig = inspect.signature(method)
                    impl_sig = inspect.signature(impl_method)
                except ValueError:
                    continue
                    
                # check parameter count (simple check)
                if len(abc_sig.parameters) != len(impl_sig.parameters):
                    self.errors.append(f"{impl_cls.__name__}.{name} signature mismatch with {abc_cls.__name__}.{name}")
