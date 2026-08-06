"""
dynamic_tool_discovery
======================

MARK_4 ToolManager plugin that dynamically discovers tools from a directory or
a JSON registry and registers them at runtime without requiring code changes.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import logging
import os
import sys
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("mark4.dynamic_tool_discovery")

class BaseTool(ABC):
    """
    Defines the interface every MARK_4 tool should implement.

    Tools may also be plain duck-typed classes containing:
        - self.name: str
        - self.description: str
        - execute(action: str, **kwargs) -> dict
    """

    @abstractmethod
    def execute(self, action: str, **kwargs) -> dict:
        """Execute a tool action and return a JSON-compatible dictionary."""
        raise NotImplementedError

class DynamicToolDiscovery(BaseTool):
    """
    Dynamically discovers, loads, registers, and exposes MARK_4 tools at runtime.

    Supports scanning a directory for Python tool files or loading a JSON registry
    that points to tool modules.
    """

    def __init__(self, tools_dir: Optional[Union[str, Path]] = None):
        self.name = "dynamic_tool_discovery"
        self.description = (
            "Dynamically discovers, loads, registers, and manages MARK_4 tools "
            "from a directory or JSON registry at runtime."
        )
        self.tools: Dict[str, Any] = {}
        self._tool_sources: Dict[str, str] = {}
        self._lock = Lock()
        self.tools_dir = Path(tools_dir) if tools_dir else Path(
            os.getenv("MARK4_TOOLS_DIR", "./tools")
        )

    def execute(self, action: str, **kwargs) -> dict:
        """
        Main entry point for the DynamicToolDiscovery tool.

        Supported actions:
            - discover / scan / reload / rescan
            - list
            - invoke
            - register
            - unregister
            - status
        """
        action = (action or "list").strip().lower()
        try:
            if action in ("discover", "scan", "reload", "rescan"):
                directory = kwargs.get("directory") or self.tools_dir
                recursive = kwargs.get("recursive", True)
                force = kwargs.get("force", True)
                data = self._discover(directory, recursive=recursive, force=force)
                return {"success": True, "data": data}

            if action == "list":
                return {"success": True, "data": {"tools": self.list_tools()}}

            if action == "invoke":
                tool_name = kwargs.get("tool")
                tool_action = kwargs.get("tool_action", "execute")
                tool_kwargs = kwargs.get("kwargs", {})

                if not tool_name:
                    return {"success": False, "data": {"error": "Missing 'tool' argument."}}
                if not isinstance(tool_kwargs, dict):
                    return {"success": False, "data": {"error": "'kwargs' must be a dict."}}

                return self.invoke_tool(tool_name, tool_action, **tool_kwargs)

            if action == "register":
                path = kwargs.get("path")
                if not path:
                    return {"success": False, "data": {"error": "Missing 'path' to tool module."}}

                instance = self._load_tool_from_file(path, required=True)
                self._register_tool(
                    instance,
                    source_path=Path(path),
                    force=kwargs.get("force", True),
                )
                return {"success": True, "data": {"registered": instance.name}}

            if action == "unregister":
                tool_name = kwargs.get("tool")
                if not tool_name:
                    return {"success": False, "data": {"error": "Missing 'tool' to unregister."}}
                return self.unregister_tool(tool_name)

            if action == "status":
                return {
                    "success": True,
                    "data": {
                        "tools_dir": str(self.tools_dir),
                        "registered_tool_count": len(self.tools),
                        "tools": self.list_tools(),
                    },
                }

            return {
                "success": False,
                "data": {"error": f"Unknown action: {action}"},
            }

        except Exception as exc:
            logger.exception("Dynamic tool discovery action failed: %s", action)
            return {"success": False, "data": {"error": str(exc)}}

    def _discover(
        self,
        source: Union[str, Path],
        recursive: bool = True,
        force: bool = True,
    ) -> Dict[str, Any]:
        source_path = Path(source).expanduser().resolve()

        if not source_path.exists():
            raise FileNotFoundError(f"Discovery source does not exist: {source_path}")

        loaded: List[str] = []
        errors: List[Dict[str, str]] = []

        current_file = Path(__file__).resolve() if "__file__" in globals() else None

        if source_path.is_file():
            if source_path.suffix.lower() == ".json":
                entries = self._read_registry(source_path)
                registry_dir = source_path.parent

                for entry in entries:
                    if entry.get("enabled", True) is False:
                        continue

                    rel_path = entry.get("path") or entry.get("file")
                    if not rel_path:
                        errors.append({
                            "error": "Registry entry missing 'path' or 'file'",
                            "entry": str(entry),
                        })
                        continue

                    tool_path = Path(rel_path)
                    if not tool_path.is_absolute():
                        tool_path = registry_dir / tool_path

                    try:
                        instance = self._load_tool_from_file(tool_path, required=True)
                        self._register_tool(instance, source_path=tool_path, force=force)
                        loaded.append(instance.name)
                    except Exception as exc:
                        errors.append({"file": str(tool_path), "error": str(exc)})
            else:
                try:
                    instance = self._load_tool_from_file(source_path, required=True)
                    self._register_tool(instance, source_path=source_path, force=force)
                    loaded.append(instance.name)
                except Exception as exc:
                    errors.append({"file": str(source_path), "error": str(exc)})

        elif source_path.is_dir():
            pattern = "**/*.py" if recursive else "*.py"
            files = source_path.rglob("*.py") if recursive else source_path.glob("*.py")

            for file_path in files:
                file_path = file_path.resolve()

                if file_path.name.startswith("_"):
                    continue

                if current_file is not None and file_path == current_file:
                    continue

                try:
                    instance = self._load_tool_from_file(file_path, required=False)
                    if instance is not None:
                        self._register_tool(instance, source_path=file_path, force=force)
                        loaded.append(instance.name)
                    else:
                        logger.debug("Skipping non-tool module: %s", file_path)
                except Exception as exc:
                    errors.append({"file": str(file_path), "error": str(exc)})
        else:
            raise FileNotFoundError(f"Unsupported discovery source: {source_path}")

        return {
            "source": str(source_path),
            "loaded": loaded,
            "errors": errors,
            "total": len(self.tools),
        }

    @staticmethod
    def _read_registry(registry_path: Path) -> List[Dict[str, Any]]:
        with open(registry_path, "r", encoding="utf-8") as fp:
            payload = json.load(fp)

        if isinstance(payload, dict):
            entries = payload.get("tools", payload.get("registry", []))
        elif isinstance(payload, list):
            entries = payload
        else:
            entries = []

        if not isinstance(entries, list):
            raise ValueError("Registry entries must be a list")

        return [entry for entry in entries if isinstance(entry, dict)]

    def _load_tool_from_file(
        self,
        file_path: Union[str, Path],
        required: bool = False,
    ) -> Optional[BaseTool]:
        file_path = Path(file_path).expanduser().resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"Tool module not found: {file_path}")
        if file_path.suffix.lower() != ".py":
            raise ValueError(f"Tool module must be a Python file: {file_path}")

        module_hash = hashlib.md5(str(file_path).encode("utf-8")).hexdigest()[:10]
        module_name = f"mark4_tool_{file_path.stem}_{module_hash}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create import spec for {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise RuntimeError(f"Failed to import {file_path}: {exc}") from exc

        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate is BaseTool or candidate is DynamicToolDiscovery:
                continue
            if getattr(candidate, "__module__", None) != module_name:
                continue
            if inspect.isabstract(candidate):
                continue
            if not self._is_tool_class(candidate):
                continue

            try:
                instance = candidate()
            except Exception as exc:
                logger.debug("Could not instantiate %s: %s", candidate.__name__, exc)
                continue

            if self._is_tool_instance(instance):
                return instance

        if required:
            raise RuntimeError(f"No valid MARK_4 tool class found in {file_path}")

        return None

    @staticmethod
    def _is_tool_class(candidate: type) -> bool:
        if inspect.isabstract(candidate):
            return False
        return callable(getattr(candidate, "execute", None))

    @staticmethod
    def _is_tool_instance(instance: Any) -> bool:
        if not hasattr(instance, "name") or not isinstance(instance.name, str):
            return False
        if not instance.name.strip():
            return False
        if not hasattr(instance, "description") or not isinstance(instance.description, str):
            return False
        if not callable(getattr(instance, "execute", None)):
            return False
        return True

    def _register_tool(
        self,
        instance: BaseTool,
        source_path: Optional[Path] = None,
        force: bool = False,
    ) -> None:
        if instance is None or not self._is_tool_instance(instance):
            raise ValueError("Invalid tool instance.")

        name = instance.name

        with self._lock:
            if name in self.tools and not force and self.tools[name] is not instance:
                raise RuntimeError(
                    f"Tool '{name}' already registered. Use force=True to replace it."
                )

            self.tools[name] = instance
            self._tool_sources[name] = str(source_path) if source_path else None
            logger.info("Registered tool '%s' from %s", name, source_path)

    def list_tools(self) -> List[Dict[str, str]]:
        with self._lock:
            return [
                {
                    "name": name,
                    "description": getattr(tool, "description", ""),
                    "source": self._tool_sources.get(name, ""),
                }
                for name, tool in sorted(self.tools.items())
            ]

    def get_tool_names(self) -> List[str]:
        with self._lock:
            return sorted(self.tools.keys())

    def get_tool(self, tool_name: str) -> Optional[Any]:
        with self._lock:
            return self.tools.get(tool_name)

    def invoke_tool(self, tool_name: str, action: str, **kwargs) -> dict:
        with self._lock:
            tool = self.tools.get(tool_name)

        if tool is None:
            return {"success": False, "data": {"error": f"Tool '{tool_name}' is not registered."}}

        try:
            result = tool.execute(action, **kwargs)

            if not isinstance(result, dict):
                return {
                    "success": False,
                    "data": {
                        "error": f"Tool '{tool_name}' returned a non-dict result.",
                        "result": result,
                    },
                }

            return result

        except Exception as exc:
            logger.exception("Tool %s failed during action '%s'", tool_name, action)
            return {
                "success": False,
                "data": {
                    "tool": tool_name,
                    "action": action,
                    "error": str(exc),
                },
            }

    def unregister_tool(self, tool_name: str) -> dict:
        with self._lock:
            if tool_name in self.tools:
                del self.tools[tool_name]
                self._tool_sources.pop(tool_name, None)
                return {"success": True, "data": {"unregistered": tool_name}}

        return {"success": False, "data": {"error": f"Tool '{tool_name}' not found."}}

def main() -> None:
    manager = DynamicToolDiscovery()

    result = manager.execute("list")
    print("List empty:", result)
    assert result["success"] is True
    assert result["data"]["tools"] == []

    sample_tool_code = '''
class SampleTool:
    def __init__(self):
        self.name = "sample_tool"
        self.description = "A sample dynamically discovered tool"

    def execute(self, action: str, **kwargs) -> dict:
        if action == "greet":
            name = kwargs.get("name", "world")
            return {"success": True, "data": {"message": f"Hello, {name}!"}}
        return {"success": False, "data": {"error": f"Unknown action: {action}"}}
'''

    with tempfile.TemporaryDirectory() as tmpdir:
        sample_tool_path = Path(tmpdir) / "sample_tool.py"
        sample_tool_path.write_text(sample_tool_code, encoding="utf-8")

        discovered = manager.execute("discover", directory=str(tmpdir), recursive=False)
        print("Discovered:", discovered)
        assert discovered["success"] is True
        assert "sample_tool" in manager.get_tool_names()

        tools_list = manager.execute("list")
        print("List after discovery:", tools_list)
        assert tools_list["success"] is True
        assert any(t["name"] == "sample_tool" for t in tools_list["data"]["tools"])

        invoked = manager.execute(
            "invoke",
            tool="sample_tool",
            tool_action="greet",
            kwargs={"name": "MARK_4"},
        )
        print("Invoke result:", invoked)
        assert invoked["success"] is True
        assert invoked["data"]["message"] == "Hello, MARK_4!"

        unregistered = manager.execute("unregister", tool="sample_tool")
        print("Unregistered:", unregistered)
        assert unregistered["success"] is True

    print("DynamicToolDiscovery self-test passed.")

if __name__ == "__main__":
    main()