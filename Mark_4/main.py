import sys
from Mark_4.core.router import CoreRouter

def main():
    print("="*60)
    print("🤖  MARK_4 : AUTONOMOUS ANDROID AI OPERATING LAYER")
    print("    Type your prompt in short Hinglish / English.")
    print("    Type 'exit' or 'quit' to close the terminal.")
    print("="*60)

    try:
        router = CoreRouter()
    except Exception as e:
        print(f"❌ [Boot Error]: Could not initialize CoreRouter: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\n👤 [You] > ").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "stop"]:
                print("\n⚡ [MARK_4]: Safely shutting down... Milte hain bhai! 😎👋\n")
                break

            response = router.process_user_prompt(user_input)
            print("\n" + response)
            print("-"*60)

        except KeyboardInterrupt:
            print("\n\n⚡ [MARK_4]: Keyboard interrupt detected. Shutting down... 👋")
            break
        except Exception as e:
            print(f"\n❌ [Runtime Error]: {str(e)}")

if __name__ == "__main__":
    main()
