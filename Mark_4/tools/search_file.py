import os
from typing import List, Optional

class SearchFileTool:
    """Tool to search for a file by name in the filesystem."""

    def __init__(self):
        self.name = "search_file"
        self.description = "Search for a file by name in the filesystem"

    def execute(self, action: str, **kwargs) -> dict:
        """
        Executes the requested action.

        Supported action:
            - "search": Search for a file by name.
                Required kwargs:
                    - filename (str): The name of the file to search for.
                Optional kwargs:
                    - path (str): Directory to start the search from (default: ".").
                    - case_sensitive (bool): Whether the match is case-sensitive (default: False).

        Returns:
            dict: {"success": bool, "data": ...}
        """
        if action != "search":
            return {"success": False, "data": f"Unsupported action: {action}"}

        filename = kwargs.get("filename") or kwargs.get("name")
        if not filename:
            return {"success": False, "data": "Missing required parameter: filename"}

        start_path = kwargs.get("path", ".")
        case_sensitive = kwargs.get("case_sensitive", False)

        if not os.path.isdir(start_path):
            return {"success": False, "data": f"Search path is not a directory: {start_path}"}

        matches: List[str] = []

        # Normalise filename for case-insensitive comparison
        target_name = filename if case_sensitive else filename.lower()

        for root, dirs, files in os.walk(start_path):
            # Modify dirs in-place to ignore permission errors when walking
            dirs[:] = [d for d in dirs if os.access(os.path.join(root, d), os.R_OK)]

            for file in files:
                if case_sensitive:
                    if file == filename:
                        matches.append(os.path.abspath(os.path.join(root, file)))
                else:
                    if file.lower() == target_name:
                        matches.append(os.path.abspath(os.path.join(root, file)))

        return {"success": True, "data": matches}

if __name__ == "__main__":
    tool = SearchFileTool()
    # Simple test: search for a file that almost certainly does not exist
    result = tool.execute("search", filename="__no_such_file__name_12345.txt", path=".")
    print(result)