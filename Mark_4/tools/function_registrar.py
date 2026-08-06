import importlib
import inspect
import sys

class FunctionRegistrar:
    """
    A tool that automatically discovers and registers all available functions
    and tool classes within a specified module or across the entire loaded system.
    """

    def __init__(self):
        self.name = "function_registrar"
        self.description = (
            "Automatically discovers and registers available functions/tools "
            "in the system."
        )
        self.registry = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _is_eligible(self, obj, module_name):
        """Return True if obj is a public function/class defined in module_name."""
        if hasattr(obj, "__module__") and obj.__module__ != module_name:
            return False
        return inspect.isfunction(obj) or inspect.isclass(obj)

    def _record(self, name, obj, module_name):
        """Build a metadata entry for a discovered object."""
        entry = {
            "name": name,
            "type": "function" if inspect.isfunction(obj) else "class",
            "module": module_name,
            "doc": inspect.getdoc(obj) or "",
        }
        if inspect.isclass(obj) and hasattr(obj, "execute"):
            entry["tool"] = True
        return entry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def discover(self, module=None, force=True):
        """
        Scan a module / the main module and register all public functions
        and classes defined there.

        :param module: Module object, name string, or None (uses __main__).
        :param force: If True, replace the current registry. If False, merge.
        """
        if module is None:
            import __main__ as mod
            module_name = "__main__"
        elif isinstance(module, str):
            try:
                mod = importlib.import_module(module)
            except ImportError as exc:
                return {"success": False, "data": {"error": str(exc)}}
            module_name = module
        else:
            mod = module
            module_name = getattr(mod, "__name__", "unknown")

        found = {}
        for obj_name, obj in inspect.getmembers(mod):
            if obj_name.startswith("_"):
                continue
            if self._is_eligible(obj, module_name):
                found[obj_name] = self._record(obj_name, obj, module_name)

        if force or not self.registry:
            self.registry = found
        else:
            self.registry.update(found)

        return {
            "success": True,
            "data": {
                "discovered": len(found),
                "registered": len(self.registry),
                "functions": found,
            },
        }

    def discover_system(self):
        """
        Scan all modules currently loaded in sys.modules and register every
        public function/class whose defining module matches the module where
        it was found.
        """
        found = {}
        for mod_name, mod in list(sys.modules.items()):
            if mod_name.startswith("_"):
                continue
            if mod is None or not hasattr(mod, "__dict__"):
                continue
            if getattr(mod, "__name__", "") != mod_name:
                continue

            try:
                members = inspect.getmembers(mod)
            except (ImportError, TypeError):
                continue

            for obj_name, obj in members:
                if obj_name.startswith("_"):
                    continue
                if self._is_eligible(obj, mod_name):
                    fq_name = f"{mod_name}.{obj_name}"
                    found[fq_name] = self._record(obj_name, obj, mod_name)

        self.registry.update(found)
        return {
            "success": True,
            "data": {
                "discovered": len(found),
                "total_registered": len(self.registry),
                "functions": found,
            },
        }

    def list(self):
        """Return a summary of all registered functions/tools."""
        summary = {
            name: {
                "type": meta.get("type"),
                "module": meta.get("module"),
            }
            for name, meta in self.registry.items()
        }
        return {"success": True, "data": {"registered": summary}}

    def get(self, name):
        """Return metadata for a single registered function/tool."""
        if name in self.registry:
            return {"success": True, "data": self.registry[name]}
        return {"success": False, "data": {"error": f"'{name}' is not registered"}}

    def register(self, name, func):
        """Manually register a callable object."""
        if not callable(func):
            return {"success": False, "data": {"error": "Object is not callable"}}
        if name.startswith("_"):
            return {"success": False, "data": {"error": "Cannot register private names"}}

        self.registry[name] = {
            "name": name,
            "type": "function" if inspect.isfunction(func) else "callable",
            "module": getattr(func, "__module__", "unknown"),
            "doc": inspect.getdoc(func) or "",
        }
        return {"success": True, "data": {"registered": name}}

    # ------------------------------------------------------------------
    # Required execute() method
    # ------------------------------------------------------------------
    def execute(self, action: str, **kwargs) -> dict:
        """
        Execute an action against the registrar.

        Supported actions:
            - discover         : scan a module (use `module` kwarg)
            - discover_system  : scan all loaded modules
            - list             : summary of registered items
            - get              : metadata for one item (use `name` kwarg)
            - register         : manually register a callable
                                 (use `name` and `func` kwargs)
        """
        if action == "discover":
            return self.discover(kwargs.get("module"), kwargs.get("force", True))
        elif action == "discover_system":
            return self.discover_system()
        elif action == "list":
            return self.list()
        elif action == "get":
            name = kwargs.get("name")
            if not name:
                return {"success": False, "data": {"error": "Missing 'name' argument"}}
            return self.get(name)
        elif action == "register":
            name = kwargs.get("name")
            func = kwargs.get("func")
            if not name or not func:
                return {
                    "success": False,
                    "data": {"error": "Missing 'name' or 'func' argument"},
                }
            return self.register(name, func)
        else:
            return {
                "success": False,
                "data": {"error": f"Unknown action '{action}'"},
            }

if __name__ == "__main__":
    tool = FunctionRegistrar()

    # Simple test: discover the main module
    result = tool.execute("discover")
    print(result)

    # List what was registered
    result = tool.execute("list")
    print(result)

    # Fetch metadata for this tool class
    result = tool.execute("get", name="FunctionRegistrar")
    print(result)