from abc import ABC, abstractmethod
from schemas import ValidationResult
from pydantic_ai import Agent
import os
import asyncio


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

        # Initialize Pydantic AI agent with OpenRouter
        self.agent = Agent(
            os.getenv("OPENROUTER_MODEL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

        # Initialize validation results - will be computed asynchronously
        self._density_result = None
        self._logical_validity_result = None

    async def initialize_validations(self):
        """Initialize the LLM-based validations asynchronously"""
        # Run both validations in a single LLM call
        self._density_result, self._logical_validity_result = await self._validate_density_and_logical_validity()

    async def _validate_density_and_logical_validity(self) -> tuple[ValidationResult, ValidationResult]:
        prompt = f"""
        Analyze this essay for both information density and logical validity.

        Essay Title: {self._title}
        Essay Body: {self._body[:2000]}...  # Truncated for analysis

        For information density, evaluate if this essay has sufficient substantive content relative to its length. Consider:
        - Does it provide substantial content beyond filler words?
        - Is there meaningful analysis or discussion?
        - Does it avoid excessive repetition or fluff?

        For logical validity, evaluate if the arguments are coherent, consistent, and logically sound. Consider:
        - Are the arguments coherent and consistent?
        - Is there logical flow between ideas?
        - Are there any contradictions or logical fallacies?

        Respond with only a JSON object in this exact format:
        {{
            "density": {{
                "rationale": "Brief explanation of the density assessment",
                "isValid": true/false
            }},
            "logical_validity": {{
                "rationale": "Brief explanation of the logical validity assessment",
                "isValid": true/false
            }}
        }}
        """

        try:
            result = await self.agent.run(prompt)
            response = result.data
            density_result = ValidationResult(
                rationale=response["density"]["rationale"],
                isValid=response["density"]["isValid"]
            )
            logical_result = ValidationResult(
                rationale=response["logical_validity"]["rationale"],
                isValid=response["logical_validity"]["isValid"]
            )
            return density_result, logical_result
        except Exception as e:
            error_result = ValidationResult(
                isValid=False,
                rationale=f"Error during validation: {str(e)}"
            )
            return error_result, error_result

    @property
    def length(self) -> ValidationResult:
        return self._length_result

    @property
    def density(self) -> ValidationResult:
        return self._density_result

    @property
    def logical_validity(self) -> ValidationResult:
        return self._logical_validity_result