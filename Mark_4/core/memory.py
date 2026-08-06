import json
import os
from datetime import datetime


class MemoryManager:

    def __init__(self):
        self.fact_file = "memory/facts.json"
        self.exp_file = "memory/experiences.json"
        self.chat_file = "memory/conversations.json"
        self.setup()
        self.clean_facts()

    def setup(self):
        os.makedirs("memory", exist_ok=True)

        for file in [self.fact_file, self.exp_file, self.chat_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f)

    def read(self, file):
        with open(file, "r") as f:
            return json.load(f)

    def write(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    # =====================
    # FACT MEMORY
    # =====================

    def save_fact(self, key, value):
        facts = self.read(self.fact_file)
        updated = False

        for fact in facts:
            if fact["key"] == key:
                fact["value"] = value
                fact["time"] = str(datetime.now())
                updated = True

        if not updated:
            facts.append(
                {"key": key, "value": value, "time": str(datetime.now())}
            )

        self.write(self.fact_file, facts)

    def get_fact(self, key):
        facts = self.read(self.fact_file)

        for fact in facts:
            if fact["key"] == key:
                return fact["value"]

        return None

    # =====================
    # EXPERIENCE MEMORY
    # =====================

    def save_experience(self, problem, solution):
        data = self.read(self.exp_file)

        data.append(
            {
                "problem": problem,
                "solution": solution,
                "verified": False,
                "time": str(datetime.now()),
            }
        )

        self.write(self.exp_file, data)

    # =====================
    # CHAT MEMORY
    # =====================

    def save_conversation(self, user, assistant):
        data = self.read(self.chat_file)

        data.append(
            {
                "user": user,
                "assistant": assistant,
                "time": str(datetime.now()),
            }
        )

        self.write(self.chat_file, data)

    def clean_facts(self):
        facts = self.read(self.fact_file)
        unique = {}

        for fact in facts:
            unique[fact["key"]] = fact

        self.write(self.fact_file, list(unique.values()))
