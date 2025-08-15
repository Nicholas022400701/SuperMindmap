import openai
import json
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    def generate_mindmap(self, keyword: str) -> dict:
        """
        Generates a mind map using the AI model.
        """
        prompt = f"""
        Please generate a mind map based on the keyword '{keyword}'.
        The generation should be based on explanatory, divergent, and associative thinking.
        The output must be a JSON object representing a tree structure with the keyword as the root.
        Each node in the tree should have a "title" and a "children" array.
        For example:
        {{
          "title": "{keyword}",
          "children": [
            {{
              "title": "Sub-topic 1",
              "children": []
            }},
            {{
              "title": "Sub-topic 2",
              "children": [
                {{
                  "title": "Sub-sub-topic 2.1",
                  "children": []
                }}
              ]
            }}
          ]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates mind maps in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            mind_map_str = response.choices[0].message.content
            return json.loads(mind_map_str)
        except Exception as e:
            print(f"Error generating mind map for '{keyword}': {e}")
            return None

ai_service = AIService()
