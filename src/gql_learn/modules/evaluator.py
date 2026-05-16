"""Answer evaluation logic for learning modules."""

from __future__ import annotations


def evaluate_answer(user_answer: str, acceptable_answers: list[str]) -> bool:
    """Evaluate if user answer matches acceptable answers.

    Args:
        user_answer: The user's answer
        acceptable_answers: List of acceptable answer variations

    Returns:
        True if answer is correct, False otherwise
    """
    if not user_answer or not user_answer.strip():
        return False

    normalized_user = user_answer.strip().lower()
    normalized_acceptable = [ans.lower() for ans in acceptable_answers]

    return normalized_user in normalized_acceptable
