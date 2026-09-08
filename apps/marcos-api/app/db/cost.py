"""Estimated USD cost per agent invocation, from token counts.

Deliberately a static lookup table, not a live pricing API call — pricing
changes rarely enough that a hardcoded table checked into the repo (and
updated when it drifts) is simpler than a network dependency for every
invocation. See docs/TOKEN_EFFICIENCY.md for the audit process that catches
drift.

Anthropic prices below were verified against the current published rate
card as of this table's last update (see PRICING_VERIFIED_AT). OpenAI
prices are NOT yet verified against a live source -- they are unused
placeholders until TASK-0004/TASK-0006 actually wire up an OpenAI
invocation, at which point they must be verified before real cost
accounting depends on them (see docs/TOKEN_EFFICIENCY.md).
"""

from decimal import Decimal

PRICING_VERIFIED_AT = "2026-09-08"

# provider -> model -> (input $ per 1M tokens, output $ per 1M tokens)
_PRICING_PER_MILLION_TOKENS: dict[str, dict[str, tuple[Decimal, Decimal]]] = {
    "anthropic-api": {
        "claude-fable-5": (Decimal("10.00"), Decimal("50.00")),
        "claude-opus-4-8": (Decimal("5.00"), Decimal("25.00")),
        "claude-opus-4-7": (Decimal("5.00"), Decimal("25.00")),
        "claude-sonnet-5": (Decimal("3.00"), Decimal("15.00")),
        "claude-sonnet-4-6": (Decimal("3.00"), Decimal("15.00")),
        "claude-haiku-4-5": (Decimal("1.00"), Decimal("5.00")),
    },
    # 'claude-code' invocations bill through the same Anthropic API pricing
    # as 'anthropic-api' -- same models, same rate card, different
    # invocation mechanism (headless CLI vs. direct API call).
    "claude-code": {
        "claude-fable-5": (Decimal("10.00"), Decimal("50.00")),
        "claude-opus-4-8": (Decimal("5.00"), Decimal("25.00")),
        "claude-opus-4-7": (Decimal("5.00"), Decimal("25.00")),
        "claude-sonnet-5": (Decimal("3.00"), Decimal("15.00")),
        "claude-sonnet-4-6": (Decimal("3.00"), Decimal("15.00")),
        "claude-haiku-4-5": (Decimal("1.00"), Decimal("5.00")),
    },
    # UNVERIFIED -- placeholders only. Do not use for real cost accounting
    # until verified against OpenAI's current published pricing (no skill
    # equivalent to claude-api exists to auto-verify these). Required before
    # TASK-0006 (Architect/Chairman-assist) ships.
    "openai": {
        "gpt-5": (Decimal("0"), Decimal("0")),
        "gpt-5-mini": (Decimal("0"), Decimal("0")),
    },
}


def estimate_cost_usd(
    provider: str, model: str | None, input_tokens: int | None, output_tokens: int | None
) -> Decimal | None:
    """Return an estimated cost in USD, or None if the model/provider isn't
    in the pricing table (e.g. unrecognized model) or token counts are
    unavailable -- callers should record None rather than a fabricated
    zero, so a missing rate is visible in audits rather than silently
    undercounted."""
    if model is None or input_tokens is None or output_tokens is None:
        return None
    provider_rates = _PRICING_PER_MILLION_TOKENS.get(provider)
    if provider_rates is None:
        return None
    rates = provider_rates.get(model)
    if rates is None:
        return None
    input_rate, output_rate = rates
    cost = (Decimal(input_tokens) * input_rate + Decimal(output_tokens) * output_rate) / Decimal(
        "1000000"
    )
    return cost.quantize(Decimal("0.000001"))
