import openai
import os

class AISummarizer:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        if self.api_key:
            openai.api_key = self.api_key

    def summarize(self, news_items):
        if not self.api_key:
            return None

        if not news_items:
            return "Nincsenek hírek az összefoglaláshoz."

        # Prepare the prompt
        news_list = ""
        for i, item in enumerate(news_items[:50]): # Limit to 50 items to avoid token limits
            news_list += f"{i+1}. {item['title']} ({item['source']})\n"

        prompt = (
            "Te egy intelligens hírszerkesztő vagy. A feladatod, hogy az alábbi hírlistából "
            "válaszd ki a 5-10 legfontosabb, legérdekesebb hírt, és foglald össze őket "
            "egy rövid, olvasmányos napi tájékoztató formájában magyarul. "
            "A stílus legyen tárgyilagos, de barátságos. "
            "Ne csak felsorolj, hanem kerek mondatokban fogalmazz.\n\n"
            f"Hírek:\n{news_list}"
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful news assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return None
