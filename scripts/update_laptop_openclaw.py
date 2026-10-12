import json

config_path = r"C:\Users\natsa\.openclaw\openclaw.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# Add loom-fabric provider pointing to Desktop Loom Gateway
config["models"]["providers"]["loom-fabric"] = {
    "baseUrl": "http://192.168.99.1:8002/v1",
    "api": "openai-completions",
    "apiKey": "loom-fabric",
    "timeoutSeconds": 300,
    "models": [
        {
            "id": "qwen2.5:32b",
            "name": "Loom Fabric - Qwen 2.5 32B (Distributed Dual-GPU + Host RAM)",
            "contextWindow": 131072,
            "contextTokens": 65536,
            "params": {
                "temperature": 0.35,
                "top_p": 0.95,
                "num_ctx": 65536
            }
        },
        {
            "id": "deepseek-r1:14b",
            "name": "Loom Fabric - DeepSeek R1 14B (Sovereign Reasoning Engine)",
            "contextWindow": 131072,
            "contextTokens": 65536,
            "params": {
                "temperature": 0.6,
                "top_p": 0.95,
                "num_ctx": 65536
            }
        },
        {
            "id": "qwen2.5:7b",
            "name": "Loom Fabric - Qwen 2.5 7B (Pure RTX 3060 CUDA)",
            "contextWindow": 131072,
            "contextTokens": 65536,
            "params": {
                "temperature": 0.35,
                "top_p": 0.95,
                "num_ctx": 65536
            }
        },
        {
            "id": "qwen2.5:3b",
            "name": "Loom Fabric - Qwen 2.5 3B (Fast Speculative Drafter)",
            "contextWindow": 32768,
            "contextTokens": 32768,
            "params": {
                "temperature": 0.35,
                "top_p": 0.95,
                "num_ctx": 32768
            }
        }
    ]
}

config["agents"]["defaults"]["model"]["primary"] = "loom-fabric/qwen2.5:32b"
fallbacks = config["agents"]["defaults"]["model"].get("fallbacks", [])
new_fallbacks = [
    "loom-fabric/deepseek-r1:14b",
    "loom-fabric/qwen2.5:7b",
    "loom-fabric/qwen2.5:3b",
    "ollama/qwen2.5:32b",
    "ollama/qwen2.5:7b"
]
for fb in reversed(new_fallbacks):
    if fb in fallbacks:
        fallbacks.remove(fb)
    fallbacks.insert(0, fb)

config["agents"]["defaults"]["model"]["fallbacks"] = fallbacks

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print("Laptop openclaw.json successfully updated with loom-fabric provider.")
