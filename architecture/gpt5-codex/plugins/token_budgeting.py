"""Token-budget utilities and model wrappers for Concordia experiments.

This module lives under `architecture/` so we can experiment with better max
token governance without touching Concordia core.  It can be imported from
notebooks or custom prefabs to:

1. load a central JSON configuration that enumerates every place where we want
   to clamp `max_tokens`;
2. wrap any `LanguageModel` with `MaxTokenGuardLanguageModel` so that requests
   are clamped and failures emit actionable logs;
3. inspect call sites to understand which component is exhausting the budget.
"""

from __future__ import annotations

import dataclasses
import inspect
import json
import logging
from pathlib import Path
from typing import Iterable, Mapping

from concordia.language_model import language_model

_LOGGER = logging.getLogger(__name__)


class TokenBudgetError(RuntimeError):
  """Raised when a request exceeds the configured token budget."""


@dataclasses.dataclass(frozen=True)
class TokenBudgetRule:
  """A single rule to override `max_tokens` for matching call sites."""

  name: str
  match: str  # substring or dotted module path to match.
  max_tokens: int

  def matches(self, callsite: str) -> bool:
    return self.match in callsite


class TokenBudgetRegistry:
  """Loads and serves token-budget rules for arbitrary call sites."""

  def __init__(
      self,
      *,
      rules: Iterable[TokenBudgetRule],
      default_max_tokens: int,
      global_context_window: int,
      safety_margin: int = 0,
  ) -> None:
    self._rules = tuple(rules)
    self._default = default_max_tokens
    self._global = global_context_window
    self._safety_margin = safety_margin

  @classmethod
  def from_json(cls, path: str | Path) -> "TokenBudgetRegistry":
    config = json.loads(Path(path).read_text())
    rules = [
        TokenBudgetRule(
            name=entry.get("name", entry["match"]),
            match=entry["match"],
            max_tokens=entry["max_tokens"],
        )
        for entry in config.get("rules", [])
    ]
    return cls(
        rules=rules,
        default_max_tokens=config["default_max_tokens"],
        global_context_window=config["global_context_window"],
        safety_margin=config.get("safety_margin", 0),
    )

  def describe(self) -> Mapping[str, str | int]:
    """Returns a summary that can be logged for debugging."""
    return {
        "default_max_tokens": self._default,
        "global_context_window": self._global,
        "safety_margin": self._safety_margin,
        "rules": [
            dataclasses.asdict(rule) for rule in self._rules
        ],
    }

  def resolve(self, *, requested: int | None, callsite: str) -> int:
    """Returns the final `max_tokens` after clamping by rules."""
    budget = requested or self._default
    for rule in self._rules:
      if rule.matches(callsite):
        budget = min(budget, rule.max_tokens)
    max_allowed = max(1, self._global - self._safety_margin)
    return min(budget, max_allowed)


def _infer_callsite() -> str:
  """Best-effort dotted path for the Concordia module issuing a request."""
  for frame in inspect.stack():
    module = inspect.getmodule(frame.frame)
    if not module:
      continue
    name = module.__name__
    if name.startswith("concordia"):
      return f"{name}.{frame.function}"
  return "unknown"


class MaxTokenGuardLanguageModel(language_model.LanguageModel):
  """Wraps a LanguageModel with budget enforcement and richer logging."""

  def __init__(
      self,
      base_model: language_model.LanguageModel,
      registry: TokenBudgetRegistry,
      *,
      logger: logging.Logger | None = None,
  ) -> None:
    self._base = base_model
    self._registry = registry
    self._logger = logger or _LOGGER

  def _adjust(
      self,
      *,
      requested: int | None,
      prompt: str,
  ) -> tuple[int, str]:
    callsite = _infer_callsite()
    budget = self._registry.resolve(requested=requested, callsite=callsite)
    self._logger.debug(
        "Resolved max_tokens",
        extra={
            "callsite": callsite,
            "requested_max_tokens": requested,
            "resolved_max_tokens": budget,
            "prompt_prefix": prompt[:200],
        },
    )
    return budget, callsite

  def sample_text(
      self,
      prompt: str,
      *,
      max_tokens: int = language_model.DEFAULT_MAX_TOKENS,
      terminators: Iterable[str] = language_model.DEFAULT_TERMINATORS,
      temperature: float = language_model.DEFAULT_TEMPERATURE,
      top_p: float = language_model.DEFAULT_TOP_P,
      top_k: int = language_model.DEFAULT_TOP_K,
      timeout: float = language_model.DEFAULT_TIMEOUT_SECONDS,
      seed: int | None = None,
  ) -> str:
    resolved, callsite = self._adjust(requested=max_tokens, prompt=prompt)
    try:
      return self._base.sample_text(
          prompt,
          max_tokens=resolved,
          terminators=terminators,
          temperature=temperature,
          top_p=top_p,
          top_k=top_k,
          timeout=timeout,
          seed=seed,
      )
    except Exception as exc:  # pylint: disable=broad-except
      self._logger.error(
          "LLM request failed after token guard adjustment",
          extra={
              "callsite": callsite,
              "resolved_max_tokens": resolved,
              "requested_max_tokens": max_tokens,
              "prompt_length_chars": len(prompt),
          },
      )
      raise TokenBudgetError(
          f"Callsite {callsite} exceeded token budget {resolved}"
      ) from exc

  def sample_choice(
      self,
      prompt: str,
      responses: Iterable[str],
      *,
      seed: int | None = None,
  ):
    # sample_choice does not accept max_tokens; we just forward the call.
    return self._base.sample_choice(prompt, responses, seed=seed)
