import openai
import google.generativeai as genai
import os

class AISummarizer:
    def __init__(self, provider, api_key, model):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        if self.provider == "openai" and self.api_key:
            openai.api_key = self.api_key
        elif self.provider == "gemini" and self.api_key:
            genai.configure(api_key=self.api_key)

    def summarize(self, news_items, current_date=None, part_of_day="napközben"):
        if not self.api_key:
            return None

        if not news_items:
            return "Nincsenek hírek az összefoglaláshoz."

        # Prepare the prompt
        news_list = ""
        for i, item in enumerate(news_items[:50]): # Limit to 50 items
            news_list += f"{i+1}. {item['title']} ({item['source']})\n"

        date_prompt = f"Ma {current_date} van." if current_date else ""
        
        prompt = (
            f"Te egy intelligens hírszerkesztő vagy. {date_prompt} Most éppen '{part_of_day}' van.\n"
            "A feladatod, hogy az alábbi hírlistából válaszd ki a naximum 5 legfontosabb "
            "hírt, és foglald össze őket egy rövid, olvasmányos napi tájékoztató formájában magyarul.\n"
            f"FONTOS: A válaszodat az napszaknak megfelelő köszönéssel kezdd (pl. '{part_of_day}' esetén: Jó reggelt/Jó napot/Jó estét), majd mondd a pontos dátumot és a mai névnapot!\n"
            "Példa: 'Jó reggelt! Ma 2024. május 1. van, Jakab névnapja.'\n"
            "A stílus legyen tárgyilagos, de barátságos. "
            "Ne csak felsorolj, és ne sorszámozz, hanem kerek mondatokban fogalmazz!.\n"
            f"Hírek:\n{news_list}"
        )

        try:
            if self.provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful news assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
                
            elif self.provider == "gemini":
                try:
                    model = genai.GenerativeModel(self.model)
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    print(f"Error calling Gemini: {e}")
                    print("DEBUG: Listing available models...")
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            print(f" - {m.name}")
                    return None
                
            else:
                print(f"Unknown AI provider: {self.provider}")
                return None
                
        except Exception as e:
            print(f"Error calling AI provider ({self.provider}): {e}")
            return None
