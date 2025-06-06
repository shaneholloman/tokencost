#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables for ANTHROPIC_API_KEY
load_dotenv()

from tokencost.costs import (
    count_message_tokens,
    count_string_tokens,
    calculate_cost_by_tokens,
    calculate_prompt_cost,
    calculate_completion_cost,
)

# 15 tokens
MESSAGES = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
]

MESSAGES_WITH_NAME = [
    {"role": "user", "content": "Hello", "name": "John"},
    {"role": "assistant", "content": "Hi there!"},
]

# 4 tokens
STRING = "Hello, world!"


# Chat models only, no embeddings (such as ada) since embeddings only does strings, not messages
@pytest.mark.parametrize(
    "model,expected_output",
    [
        ("gpt-3.5-turbo", 15),
        ("gpt-3.5-turbo-0301", 17),
        ("gpt-3.5-turbo-0613", 15),
        ("gpt-3.5-turbo-16k", 15),
        ("gpt-3.5-turbo-16k-0613", 15),
        ("gpt-3.5-turbo-1106", 15),
        ("gpt-3.5-turbo-instruct", 15),
        ("gpt-4", 15),
        ("gpt-4-0314", 15),
        ("gpt-4-0613", 15),
        ("gpt-4-32k", 15),
        ("gpt-4-32k-0314", 15),
        ("gpt-4-1106-preview", 15),
        ("gpt-4-vision-preview", 15),
        ("gpt-4o", 15),
        ("azure/gpt-4o", 15),
        pytest.param("claude-3-opus-latest", 11,
                     marks=pytest.mark.skipif(
                         bool(os.getenv("ANTHROPIC_API_KEY")),
                         reason="ANTHROPIC_API_KEY environment variable not set"
                     )),
    ],
)
def test_count_message_tokens(model, expected_output):
    print(model)
    assert count_message_tokens(MESSAGES, model) == expected_output


# Chat models only, no embeddings
@pytest.mark.parametrize(
    "model,expected_output",
    [
        ("gpt-3.5-turbo", 17),
        ("gpt-3.5-turbo-0301", 17),
        ("gpt-3.5-turbo-0613", 17),
        ("gpt-3.5-turbo-1106", 17),
        ("gpt-3.5-turbo-instruct", 17),
        ("gpt-3.5-turbo-16k", 17),
        ("gpt-3.5-turbo-16k-0613", 17),
        ("gpt-4", 17),
        ("gpt-4-0314", 17),
        ("gpt-4-0613", 17),
        ("gpt-4-32k", 17),
        ("gpt-4-32k-0314", 17),
        ("gpt-4-1106-preview", 17),
        ("gpt-4-vision-preview", 17),
        ("gpt-4o", 17),
        ("azure/gpt-4o", 17),
        # ("claude-3-opus-latest", 4), # NOTE: Claude only supports messages without extra inputs
    ],
)
def test_count_message_tokens_with_name(model, expected_output):
    """Notice: name 'John' appears"""

    assert count_message_tokens(MESSAGES_WITH_NAME, model) == expected_output


def test_count_message_tokens_empty_input():
    """Empty input should raise a KeyError"""
    with pytest.raises(KeyError):
        count_message_tokens("", "")


def test_count_message_tokens_invalid_model():
    """Invalid model should raise a KeyError"""

    with pytest.raises(KeyError):
        count_message_tokens(MESSAGES, model="invalid_model")


@pytest.mark.parametrize(
    "model,expected_output",
    [
        ("gpt-3.5-turbo", 4),
        ("gpt-3.5-turbo-0301", 4),
        ("gpt-3.5-turbo-0613", 4),
        ("gpt-3.5-turbo-16k", 4),
        ("gpt-3.5-turbo-16k-0613", 4),
        ("gpt-3.5-turbo-1106", 4),
        ("gpt-3.5-turbo-instruct", 4),
        ("gpt-4-0314", 4),
        ("gpt-4", 4),
        ("gpt-4-32k", 4),
        ("gpt-4-32k-0314", 4),
        ("gpt-4-0613", 4),
        ("gpt-4-1106-preview", 4),
        ("gpt-4-vision-preview", 4),
        ("text-embedding-ada-002", 4),
        ("gpt-4o", 4),
        # ("claude-3-opus-latest", 4), # NOTE: Claude only supports messages
    ],
)
def test_count_string_tokens(model, expected_output):
    """Test that the string tokens are counted correctly."""

    # 4 tokens
    assert count_string_tokens(STRING, model=model) == expected_output

    # empty string
    assert count_string_tokens("", model=model) == 0


def test_count_string_invalid_model():
    """Test that the string tokens are counted correctly."""

    assert count_string_tokens(STRING, model="invalid model") == 4


# Costs from https://openai.com/pricing
# https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
@pytest.mark.parametrize(
    "prompt,model,expected_output",
    [
        (MESSAGES, "gpt-3.5-turbo", Decimal("0.0000225")),
        (MESSAGES, "gpt-3.5-turbo-0301", Decimal("0.0000255")),
        (MESSAGES, "gpt-3.5-turbo-0613", Decimal("0.0000225")),
        (MESSAGES, "gpt-3.5-turbo-16k", Decimal("0.000045")),
        (MESSAGES, "gpt-3.5-turbo-16k-0613", Decimal("0.000045")),
        (MESSAGES, "gpt-3.5-turbo-1106", Decimal("0.000015")),
        (MESSAGES, "gpt-3.5-turbo-instruct", Decimal("0.0000225")),
        (MESSAGES, "gpt-4", Decimal("0.00045")),
        (MESSAGES, "gpt-4-0314", Decimal("0.00045")),
        (MESSAGES, "gpt-4-32k", Decimal("0.00090")),
        (MESSAGES, "gpt-4-32k-0314", Decimal("0.00090")),
        (MESSAGES, "gpt-4-0613", Decimal("0.00045")),
        (MESSAGES, "gpt-4-1106-preview", Decimal("0.00015")),
        (MESSAGES, "gpt-4-vision-preview", Decimal("0.00015")),
        (MESSAGES, "gpt-4o", Decimal("0.0000375")),
        (MESSAGES, "azure/gpt-4o", Decimal("0.0000375")),
        pytest.param(MESSAGES, "claude-3-opus-latest", Decimal("0.000165"),
                     marks=pytest.mark.skipif(
                         bool(os.getenv("ANTHROPIC_API_KEY")),
                         reason="ANTHROPIC_API_KEY environment variable not set"
                     )),
        (STRING, "text-embedding-ada-002", Decimal("0.0000004")),
    ],
)
def test_calculate_prompt_cost(prompt, model, expected_output):
    """Test that the cost calculation is correct."""

    cost = calculate_prompt_cost(prompt, model)
    assert cost == expected_output


def test_invalid_prompt_format():
    with pytest.raises(TypeError):
        calculate_prompt_cost(
            {"role": "user", "content": "invalid message type"}, model="gpt-3.5-turbo"
        )


@pytest.mark.parametrize(
    "prompt,model,expected_output",
    [
        (STRING, "gpt-3.5-turbo", Decimal("0.000008")),
        (STRING, "gpt-3.5-turbo-0301", Decimal("0.000008")),
        (STRING, "gpt-3.5-turbo-0613", Decimal("0.000008")),
        (STRING, "gpt-3.5-turbo-16k", Decimal("0.000016")),
        (STRING, "gpt-3.5-turbo-16k-0613", Decimal("0.000016")),
        (STRING, "gpt-3.5-turbo-1106", Decimal("0.000008")),
        (STRING, "gpt-3.5-turbo-instruct", Decimal("0.000008")),
        (STRING, "gpt-4", Decimal("0.00024")),
        (STRING, "gpt-4-0314", Decimal("0.00024")),
        (STRING, "gpt-4-32k", Decimal("0.00048")),
        (STRING, "gpt-4-32k-0314", Decimal("0.00048")),
        (STRING, "gpt-4-0613", Decimal("0.00024")),
        (STRING, "gpt-4-1106-preview", Decimal("0.00012")),
        (STRING, "gpt-4-vision-preview", Decimal("0.00012")),
        (STRING, "gpt-4o", Decimal("0.00004")),
        (STRING, "azure/gpt-4o", Decimal("0.00004")),
        # (STRING, "claude-3-opus-latest", Decimal("0.000096")), # NOTE: Claude only supports messages
        (STRING, "text-embedding-ada-002", 0),
    ],
)
def test_calculate_completion_cost(prompt, model, expected_output):
    """Test that the completion cost calculation is correct."""

    cost = calculate_completion_cost(prompt, model)
    assert cost == expected_output


def test_calculate_cost_invalid_model():
    """Invalid model should raise a KeyError"""

    with pytest.raises(KeyError):
        calculate_prompt_cost(STRING, model="invalid_model")


def test_calculate_invalid_input_types():
    """Invalid input type should raise a KeyError"""

    with pytest.raises(KeyError):
        calculate_prompt_cost(STRING, model="invalid_model")

    with pytest.raises(KeyError):
        calculate_completion_cost(STRING, model="invalid_model")

    with pytest.raises(KeyError):
        # Message objects not allowed, must be list of message objects.
        calculate_prompt_cost(MESSAGES[0], model="invalid_model")


@pytest.mark.parametrize(
    "num_tokens,model,token_type,expected_output",
    [
        (10, "gpt-3.5-turbo", "input", Decimal("0.0000150")),  # Example values
        (5, "gpt-4", "output", Decimal("0.00030")),  # Example values
        (10, "ai21.j2-mid-v1", "input", Decimal("0.0001250")),  # Example values
        (100, "gpt-4o", "cached", Decimal("0.000125")),  # Cache tokens test
    ],
)
def test_calculate_cost_by_tokens(num_tokens, model, token_type, expected_output):
    """Test that the token cost calculation is correct."""
    cost = calculate_cost_by_tokens(num_tokens, model, token_type)
    assert cost == expected_output


def test_calculate_cached_tokens_cost():
    """Test that cached tokens cost calculation works correctly."""
    # Basic test for cache token cost calculation
    model = "gpt-4o"
    num_tokens = 1000
    token_type = "cached"

    # Get the expected cost from the TOKEN_COSTS dictionary
    from tokencost.constants import TOKEN_COSTS
    cache_cost_per_token = TOKEN_COSTS[model]["cache_read_input_token_cost"]
    expected_cost = Decimal(str(cache_cost_per_token)) * Decimal(num_tokens)

    # Calculate the actual cost
    actual_cost = calculate_cost_by_tokens(num_tokens, model, token_type)

    # Assert that the costs match
    assert actual_cost == expected_cost
    assert actual_cost > 0, "Cache token cost should be greater than zero"
