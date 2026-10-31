# llm/

One way to talk to an AI model, whatever company provides it.

```python
client.ask(system: str, user: str, ReplyModel) -> ReplyModel   # a checked pydantic object
```

Every step of the marking pipeline calls only this. The reply is converted into the pydantic model
you pass in, and the call is retried if the reply is malformed. The number of tokens used is
recorded.

| File | What it is | Needs |
|---|---|---|
| `base.py` | The `LLMClient` interface, retries and usage counting | |
| `openrouter.py` | The `openrouter` backend: any model OpenRouter serves (DeepSeek, Claude and others) | `OPENROUTER_API_KEY` |
| `mock.py` | The `mock` backend: works offline, gives the same answer every time | nothing |
| `__init__.py` | `build_client(config)` picks the backend named in the config | |

Choose the backend with `llm.backend` in the config file. The other files in this folder
(`claude_cli.py`, `anthropic_api.py` and `gemini.py`) are backends used during development. They
are not part of a deployment.

Keys are read from the environment or from the git-ignored `.env` file (copy `.env.example`). They
are never written to a log. `client.name` combines the backend, model and effort, and it names the
folder that holds the saved marking schemes. A different model therefore never reuses another
model's schemes.

The **mock** backend splits the model answer into sentences to make a scheme, and marks by counting
shared words. It exists so the whole pipeline and the test suite can run without a network. It is
not a real grader.

## Adding a backend

1. Subclass `LLMClient` and implement `_complete(system, user, schema) -> (dict, Usage)`.
2. Add a branch to `build_client` and add the name to the `Backend` type in `config.py`.
3. Add a test with scripted replies, next to `tests/test_pipeline.py`.
