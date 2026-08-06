import os
import stat
import time
import sys
import pwd
import grp
from datetime import datetime

class FileInfoTool:
    """
    A tool that returns metadata for a given file or directory path.
    """

    def __init__(self):
        self.name = "get_file_info"
        self.description = (
            "Returns file metadata (size, modification time, permissions, "
            "type, ownership, symlink info, etc.) for a given path."
        )

    def execute(self, action: str, **kwargs) -> dict:
        """
        Execute the requested action.

        :param action: Action name. Supported: 'info', 'get', 'get_file_info'
        :param kwargs: Must contain 'path' (str) for the target file system object.
        :return: Dictionary with 'success' and 'data' or 'error'.
        """
        if action.lower() not in ("info", "get", "get_file_info"):
            return {
                "success": False,
                "error": f"Unsupported action: '{action}'. Use 'info' or 'get_file_info'.",
            }

        path = kwargs.get("path")
        if not path or not isinstance(path, str) or not path.strip():
            return {"success": False, "error": "Missing or invalid 'path' argument."}

        path = os.path.expanduser(path.strip())

        if not os.path.exists(path) and not os.path.islink(path):
            return {"success": False, "error": f"Path does not exist: {path}"}

        try:
            # Use lstat to detect symlinks themselves, not their targets
            st = os.lstat(path)

            # Basic type detection
            file_type = None
            if stat.S_ISDIR(st.st_mode):
                file_type = "directory"
            elif stat.S_ISREG(st.st_mode):
                file_type = "regular_file"
            elif stat.S_ISLNK(st.st_mode):
                file_type = "symbolic_link"
            elif stat.S_ISCHR(st.st_mode):
                file_type = "character_device"
            elif stat.S_ISBLK(st.st_mode):
                file_type = "block_device"
            elif stat.S_ISFIFO(st.st_mode):
                file_type = "fifo"
            elif stat.S_ISSOCK(st.st_mode):
                file_type = "socket"
            else:
                file_type = "unknown"

            # Permission string like rwxr-xr-x
            permissions_symbolic = stat.filemode(st.st_mode)
            # Octal permission string like 755
            permissions_octal = oct(stat.S_IMODE(st.st_mode))[2:]

            # Owner/group names
            try:
                owner_name = pwd.getpwuid(st.st_uid).pw_name
            except (KeyError, ImportError):
                owner_name = str(st.st_uid)

            try:
                group_name = grp.getgrgid(st.st_gid).gr_name
            except (KeyError, ImportError):
                group_name = str(st.st_gid)

            # Symlink target
            symlink_target = None
            if stat.S_ISLNK(st.st_mode):
                try:
                    symlink_target = os.readlink(path)
                except OSError:
                    symlink_target = "<unreadable>"

            # Human-readable size
            size_bytes = st.st_size
            size_human = self._human_size(size_bytes)

            data = {
                "path": os.path.abspath(path),
                "file_type": file_type,
                "size_bytes": size_bytes,
                "size_human": size_human,
                "permissions_symbolic": permissions_symbolic,
                "permissions_octal": permissions_octal,
                "owner_uid": st.st_uid,
                "owner_name": owner_name,
                "group_gid": st.st_gid,
                "group_name": group_name,
                "modified_time_unix": st.st_mtime,
                "modified_time_iso": datetime.fromtimestamp(st.st_mtime).isoformat(),
                "accessed_time_unix": st.st_atime,
                "accessed_time_iso": datetime.fromtimestamp(st.st_atime).isoformat(),
                "created_time_unix": st.st_ctime,
                "created_time_iso": datetime.fromtimestamp(st.st_ctime).isoformat(),
                "is_symlink": stat.S_ISLNK(st.st_mode),
            }

            if symlink_target is not None:
                data["symlink_target"] = symlink_target

            return {"success": True, "data": data}

        except (OSError, ValueError) as exc:
            return {"success": False, "error": f"Could not read file info: {exc}"}

    @staticmethod
    def _human_size(num: int) -> str:
        """Return a human-readable file size string."""
        if num < 0:
            return "0 B"
        for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
            if abs(num) < 1024.0 or unit == "PB":
                if unit == "B":
                    return f"{num} {unit}"
                return f"{num:.2f} {unit}"
            num /= 1024.0
        return f"{num} B"

if __name__ == "__main__":
    # Simple test: pass a path as CLI arg, or use this file as default
    test_path = sys.argv[1] if len(sys.argv) > 1 else __file__
    tool = FileInfoTool()
    result = tool.execute("info", path=test_path)
    print(f"Tool name: {tool.name}")
    print(f"Description: {tool.description}")
    print("Result:")
    if result["success"]:
        for key, value in result["data"].items():
            print(f"  {key}: {value}")
    else:
        print(f"  Error: {result['error']}")