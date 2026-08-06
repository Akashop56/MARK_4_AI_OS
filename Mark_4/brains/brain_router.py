from Mark_4.brains.omniroute_brain import OmniRouteBrain
# Agar aapke paas groq_brain hai toh use bhi import kar sakte ho:
# from Mark_4.brains.groq_brain import GroqBrain

class BrainRouter:
    def __init__(self, api_key="sk-5f238e76072d7926-58ceae-48c364f1"):
        print("🧠 Initializing Mark_4 Brain Router...")
        self.coding_brain = OmniRouteBrain(api_key=api_key)
        # self.chat_brain = GroqBrain(...) # Future me link kar sakte ho

    def route_and_think(self, prompt, system_prompt="You are Mark_4, an autonomous AI assistant."):
        # Keywords check karo ki kya task coding/tools/automation se related hai
        coding_keywords = ["code", "python", "script", "error", "fix", "tool", "file", "app", "termux", "bug", "function"]
        
        is_coding_task = any(kw in prompt.lower() for kw in coding_keywords)
        
        if is_coding_task:
            print("⚡ [Router]: Coding/Tool task detected -> Routing to OmniRoute (DeepSeek/Felo)...")
            return self.coding_brain.think(prompt, system_prompt)
        else:
            print("💬 [Router]: General query -> Routing to OmniRoute...")
            # Abhi ke liye sab kuch OmniRoute se chala rahe hain, baad me Groq fallback laga sakte ho
            return self.coding_brain.think(prompt, system_prompt)

if __name__ == "__main__":
    router = BrainRouter()
    print("\n--- Testing Router ---")
    reply = router.route_and_think("Bhai ek Python script banao jo folder ke saare files list kare.")
    print("\n🤖 Mark_4 Final Output:\n" + reply)
