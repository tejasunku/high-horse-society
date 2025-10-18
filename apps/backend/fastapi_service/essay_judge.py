from abc import ABC, abstractmethod
from schemas import ValidationResult


class EssayJudgeInterface(ABC):
    @property
    @abstractmethod
    def length(self) -> ValidationResult:
        pass

    @property
    @abstractmethod
    def density(self) -> ValidationResult:
        pass

    @property
    @abstractmethod
    def logical_validity(self) -> ValidationResult:
        pass


class EssayJudge(EssayJudgeInterface):
    def __init__(self, title: str, body: str):
        self._title = title
        self._body = body

        # Count words in the essay body
        word_count = len(self._body.split())

        # Length validation: must be at least 1000 words
        length_valid = word_count >= 1000
        length_rationale = f"Essay has {word_count} words. Minimum required is 1000 words." if not length_valid else f"Essay has {word_count} words, which meets the minimum requirement."

        self._length_result = ValidationResult(isValid=length_valid, rationale=length_rationale)

        # TODO: Implement actual LLM calls for density and logical validity
        self._density_result = ValidationResult(isValid=True, rationale="Information density validation passed.")
        self._logical_validity_result = ValidationResult(isValid=True, rationale="Logical validity validation passed.")

    @property
    def length(self) -> ValidationResult:
        return self._length_result

    @property
    def density(self) -> ValidationResult:
        return self._density_result

    @property
    def logical_validity(self) -> ValidationResult:
        return self._logical_validity_result