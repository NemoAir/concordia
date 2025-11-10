"""Language detection and routing helpers for Concordia."""

from __future__ import annotations

import contextlib
import contextvars
import dataclasses
import logging
import re
from typing import Iterable, Sequence

from concordia.agents import entity_agent_with_logging
from concordia.language_model import language_model
from concordia.typing import entity as entity_lib

_LOGGER = logging.getLogger(__name__)
_CJK_PATTERN = re.compile(r'[\u4e00-\u9fff]+')
_LATIN_PATTERN = re.compile(r'[A-Za-z]+')
_LANGUAGE_NAMES = {
    'en': 'English',
    'zh': 'Chinese',
}


def detect_language(sample: str) -> str:
  """Naive detector that distinguishes Chinese vs English text."""
  cjk = sum(len(match.group()) for match in _CJK_PATTERN.finditer(sample))
  latin = sum(len(match.group()) for match in _LATIN_PATTERN.finditer(sample))
  if cjk > latin:
    return 'zh'
  return 'en'


@dataclasses.dataclass
class LanguagePolicy:
  world_language: str = 'en'
  fallback_language: str = 'en'


class LanguagePolicyStore:
  """Stores world language plus per-entity overrides."""

  def __init__(self, policy: LanguagePolicy | None = None):
    self._policy = policy or LanguagePolicy()
    self._entity_overrides: dict[str, str] = {}
    self._current_entity = contextvars.ContextVar(
        'concordia_language_entity', default=None)

  def update_world_language(self, shared_memories: Sequence[str]) -> None:
    sample = ' '.join(shared_memories).strip()
    if not sample:
      return
    detected = detect_language(sample)
    _LOGGER.info('Detected world language', extra={'language': detected})
    self._policy.world_language = detected

  def override_for_entity(self, entity_name: str, language_code: str) -> None:
    self._entity_overrides[entity_name] = language_code

  @contextlib.contextmanager
  def activate_entity(self, entity_name: str):
    token = self._current_entity.set(entity_name)
    try:
      yield
    finally:
      self._current_entity.reset(token)

  def active_language(self) -> str:
    entity_name = self._current_entity.get()
    if entity_name and entity_name in self._entity_overrides:
      return self._entity_overrides[entity_name]
    return self._policy.world_language or self._policy.fallback_language


class LanguageRoutingModel(language_model.LanguageModel):
  """Wraps a LanguageModel and enforces the active language."""

  def __init__(
      self,
      base_model: language_model.LanguageModel,
      policy_store: LanguagePolicyStore,
      *,
      instruction_template: str | None = None,
  ):
    self._base = base_model
    self._policy_store = policy_store
    self._instruction_template = (
        instruction_template or 'Please respond in {language}.'
    )

  def _inject_language_instruction(self, prompt: str, language_code: str) -> str:
    if not language_code:
      return prompt
    language_name = _LANGUAGE_NAMES.get(language_code, language_code)
    instruction = self._instruction_template.format(language=language_name)
    if instruction in prompt:
      return prompt
    return f'{prompt.rstrip()}\n\n{instruction}\n'

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
    language_code = self._policy_store.active_language()
    prompt_with_instruction = self._inject_language_instruction(
        prompt, language_code)
    return self._base.sample_text(
        prompt_with_instruction,
        max_tokens=max_tokens,
        terminators=terminators,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        timeout=timeout,
        seed=seed,
    )

  def sample_choice(
      self,
      prompt: str,
      responses: Iterable[str],
      *,
      seed: int | None = None,
  ):
    language_code = self._policy_store.active_language()
    prompt_with_instruction = self._inject_language_instruction(
        prompt, language_code)
    return self._base.sample_choice(
        prompt_with_instruction,
        responses,
        seed=seed,
    )


class LanguageAwareEntityAgent(entity_agent_with_logging.EntityAgentWithLogging):
  """EntityAgent variant that propagates language context via contextvars."""

  def __init__(
      self,
      *args,
      language_policy_store: LanguagePolicyStore,
      **kwargs,
  ):
    super().__init__(*args, **kwargs)
    self._language_policy_store = language_policy_store

  def act(
      self,
      action_spec: entity_lib.ActionSpec = entity_lib.DEFAULT_ACTION_SPEC,
  ):
    with self._language_policy_store.activate_entity(self.name):
      return super().act(action_spec)

  def observe(self, observation: str) -> None:
    with self._language_policy_store.activate_entity(self.name):
      super().observe(observation)
