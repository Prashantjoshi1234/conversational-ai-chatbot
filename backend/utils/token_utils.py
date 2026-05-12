import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

MODEL_MAX_TOKENS = 4096
RESERVED_OUTPUT_TOKENS = 700   # answer space
TOKENIZER_MARGIN = 200

SAFE_MAX_INPUT_TOKENS = (
    MODEL_MAX_TOKENS
    - RESERVED_OUTPUT_TOKENS
    - TOKENIZER_MARGIN
)

def count_tokens(text : str | None) -> int:
    if not text:
        return 0
    return len(encoding.encode(str(text)))

def is_prompt_safe(token_count: int, include_margin: bool = True):
    if include_margin:
        safe_limit = SAFE_MAX_INPUT_TOKENS + TOKENIZER_MARGIN
    else:
        safe_limit = SAFE_MAX_INPUT_TOKENS
    return token_count <= safe_limit

