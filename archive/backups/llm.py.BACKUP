import requests


def ask_llm(messages, models, api_key, headers):
    last_error = None

    for model in models:
        payload = {
            "model": model,
            "messages": messages
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("choices"):
                    return data["choices"][0]["message"]["content"]

                last_error = f"Empty response from {model}"

            else:
                last_error = f"{model}: HTTP {response.status_code}"

                if response.status_code in [429, 404, 503]:
                    continue

                return f"External error {response.status_code}"

        except Exception as e:
            last_error = str(e)

    return f"All models failed.\nLast error: {last_error}"
