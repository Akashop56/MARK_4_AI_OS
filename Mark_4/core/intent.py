class IntentDetector:


    @staticmethod
    def detect(command):

        text = command.lower().strip()


        # Battery

        if any(word in text for word in [
            "battery",
            "charge",
            "बैटरी"
        ]):

            return {
                "task":"battery",
                "parameters":{}
            }



        # Open app

        if (
            text.startswith("open ")
            or
            text.startswith("launch ")
            or
            text.startswith("start ")
        ):

            name = (
                text
                .replace("open ","")
                .replace("launch ","")
                .replace("start ","")
            )


            return {

                "task":"open_app",

                "parameters":{
                    "name":name
                }

            }



        return {

            "task":"chat",

            "parameters":{

                "text":command

            }

        }
