import re
from collections import Counter
from typing import Any, Dict

class TextStatsTool:
    """
    A production-ready utility for performing common text operations and
    computing statistical summaries over a given string.
    """

    def __init__(self) -> None:
        self.name = "new_tool"
        self.description = (
            "Provides text statistics (word/char/sentence counts) and "
            "simple string transformations (reverse, uppercase, lowercase, word list)."
        )

    def execute(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a supported text operation.

        Supported actions:
            - "stats": Return word, character, sentence counts and frequency of words.
                      Requires text (str).
            - "reverse": Return the reversed text. Requires text (str).
            - "upper": Return text converted to uppercase. Requires text (str).
            - "lower": Return text converted to lowercase. Requires text (str).
            - "words": Return list of words extracted from text. Requires text (str).

        All actions accept the keyword argument `text`.

        Returns:
            dict with keys:
                success: bool
                data: dict or list containing the result
                error (only on failure): string
        """
        if action not in {"stats", "reverse", "upper", "lower", "words"}:
            return {
                "success": False,
                "data": None,
                "error": f"Unsupported action: {action}. Supported: stats, reverse, upper, lower, words",
            }

        text = kwargs.get("text", None)
        if not isinstance(text, str) or text.strip() == "":
            return {
                "success": False,
                "data": None,
                "error": "The 'text' keyword argument must be a non-empty string.",
            }

        try:
            if action == "stats":
                return self._stats(text)
            elif action == "reverse":
                return {"success": True, "data": {"reversed": text[::-1]}}
            elif action == "upper":
                return {"success": True, "data": {"upper": text.upper()}}
            elif action == "lower":
                return {"success": True, "data": {"lower": text.lower()}}
            elif action == "words":
                words = self._extract_words(text)
                return {"success": True, "data": {"words": words}}
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "data": None,
                "error": f"Unexpected error during action '{action}': {exc}",
            }

        # Should never reach here, but keep return path complete.
        return {"success": False, "data": None, "error": "Unknown execution path."}

    @staticmethod
    def _extract_words(text: str) -> list[str]:
        """Extract lowercase alphabetic words from a string."""
        return re.findall(r"[a-zA-Z]+", text)

    @classmethod
    def _stats(cls, text: str) -> Dict[str, Any]:
        """Compute statistics for a text string."""
        words = cls._extract_words(text)

        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        word_count = len(words)

        # Sentence splitting: ., !, ? are considered sentence boundaries.
        sentences = re.split(r"[.!?]+", text.strip())
        sentence_count = len([s for s in sentences if s.strip()])

        word_frequency = Counter(words)

        # Most common words (top 5)
        most_common = word_frequency.most_common(5)

        return {
            "success": True,
            "data": {
                "text_length": char_count,
                "text_length_no_spaces": char_count_no_spaces,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "word_frequency": dict(word_frequency),
                "most_common_words": most_common,
            },
        }

if __name__ == "__main__":
    tool = TextStatsTool()
    sample_text = (
        "The quick brown fox jumps over the lazy dog. The dog barks, "
        "but the fox runs away! Is this a test? Yes."
    )

    result = tool.execute("stats", text=sample_text)

    print(f"Tool name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Result success: {result['success']}")
    print("Stats data:")
    if result["success"]:
        data = result["data"]
        print(f"  Word count: {data['word_count']}")
        print(f"  Sentence count: {data['sentence_count']}")
        print(f"  Character count: {data['text_length']}")
        print(f"  Most common words: {data['most_common_words']}")
    else:
        print("Error:", result.get("error"))