# config.py

config = {
    "OpenAI": {
        "url": "https://api.openai.com/v1/chat/completions",
        "api_key": "OPENAI_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"Content-Type": "application/json", "Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}",
            "messages":
              [ {%  if model == "o1-preview" or model == "o1-mini" %}
                {"role": "user","content": "Return a command for {{ os_system }} that can be executed by the user. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS, NO QUOTES. For example 'Change directory to my home dir'"},
                {% else %}
                {"role": "system","content": "Help the user working on {{ os_system }} create a command. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS."},
                {"role": "user","content": "Change directory to my home dir"},
                {% endif %}
                {"role": "assistant","content": "cd"},
                {"role": "user","content": "{{ user_input }}"}
              ]}''',
        "models": ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini", "gpt-4-turbo"],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "XAI": {
        "url": "https://api.x.ai/v1/chat/completions",
        "api_key": "X_AI_API_KEY",
        "response_text_is_json": False,
        "tplHeader": '''{"Content-Type": "application/json","Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}",
                "messages":[
                    {"role": "system",
                     "content": "Help the user working on {{ os_system }} create a command. JUST COMMAND. NO COMMENTS, NO EXPLANATIONS."},
                    {"role": "user", "content": "Change directory to my home dir"},
                    {"role": "assistant", "content": "cd"},
                    {"role": "user", "content": "{{ user_input }}"}
                ]}''',
        "models": ["grok-beta"],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "Mistralai": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "api_key": "MISTRAL_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer {{ API_KEY }}"}''',
        "tplData": '''{ "model": "{{ model }}",
            "messages":
              [ {"role": "system","content": "You are helping a user on {{ os_system }} execute commands. Return the command only. NO QUOTES, NO COMMENTS, NO EXPLANATIONS"},
                {"role": "user","content": "{{ user_input }}"}
              ]}''',
        "models": ["mistral-large-latest", "mistral-small-latest", "mistral-large-2407",
                   "mistral-small-2409", "codestral-2405", "mistral-embed", "ministral-3b-latest", "ministral-8b-latest",
                   "pixtral-12b", "mistral-nemo", "open-mistral-7b", "open-mixtral-8x7b", "open-mixtral-8x22b"
                   ],
        'response_keys': ['choices', 0, 'message', 'content']
    },
    "Anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "api_key": "ANTHROPIC_API_KEY",
        "response_text_is_json": True,
        "tplHeader": '''{"x-api-key": "{{ API_KEY }}", "Content-Type": "application/json","anthropic-version": "2023-06-01"}''',
        "tplData": '''{ "model": "{{ model }}",
             "system": "You are an operator working on {{ os_system }}. List a single command that the user can execute.",
             "max_tokens": 1024,
             "messages":
              [ {"role": "user","content": "Change directory to my home dir"},
                {"role": "assistant","content": "cd"},
                {"role": "user","content": "{{ user_input }}"}
              ]}''',
        "models": ["claude-3-5-sonnet-latest", "claude-3-opus-latest", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        'response_keys': ['content', 0, 'text']
    }
}
