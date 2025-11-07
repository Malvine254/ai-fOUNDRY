from .azure_service import client, DEPLOYMENT_NAME

def classify_intent(message):
    """Return intent: chat, document, weather, time, or general."""
    try:
        res = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": (
                    "You are an intent classifier. Respond with one of: "
                    "'chat', 'document', 'weather', 'time', 'general'."
                )},
                {"role": "user", "content": message}
            ],
            temperature=0,
            max_tokens=2
        )
        intent = res.choices[0].message.content.strip().lower()
        if intent not in ["chat", "document", "weather", "time", "general"]:
            intent = "general"
        return intent
    except Exception as e:
        print("⚠️ Intent classification failed:", e)
        return "general"
