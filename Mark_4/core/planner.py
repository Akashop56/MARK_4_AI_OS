"""Multi-step task decomposition & reasoning."""
import json



class Planner:


    @staticmethod
    def create_plan(ai_response):

        try:

            if isinstance(ai_response, dict):
                return ai_response


            return json.loads(ai_response)


        except Exception:


            return {

                "task":"chat",

                "parameters":{

                    "text":ai_response

                }

            }
