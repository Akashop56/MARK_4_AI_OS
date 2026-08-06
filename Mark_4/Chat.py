# chat.py


from ai_manager import AIManager



def main():

    print(
        "Mark_4 AI Manager Started"
    )


    ai = AIManager()


    while True:

        try:

            user = input("\nYou: ")


            if user.lower() in [
                "exit",
                "quit"
            ]:
                print(
                    "Goodbye"
                )
                break


            answer = ai.process(user)


            print(
                "\nAI:",
                answer
            )


        except KeyboardInterrupt:

            print(
                "\nStopped"
            )
            break



if __name__ == "__main__":

    main()