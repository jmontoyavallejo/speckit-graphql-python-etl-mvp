# Function Documentation Standards

All functions in production code MUST follow this documentation format for consistency, maintainability, and IDE support.

## Docstring Format

### Single-line Function

```python
def simple_function(arg: str) -> int:
    """Calculate and return the length of the input string."""
    return len(arg)
```

### Multi-line Function with Args, Returns, Raises

```python
def evaluate_answer(user_answer: str, acceptable_answers: list[str]) -> bool:
    """Evaluate if user answer matches acceptable answers.

    Args:
        user_answer: The user's answer (may contain whitespace)
        acceptable_answers: List of acceptable answer variations

    Returns:
        True if answer matches (case-insensitive), False otherwise

    Raises:
        ValueError: If user_answer is None
        TypeError: If acceptable_answers is not a list
    """
    if user_answer is None:
        raise ValueError("user_answer cannot be None")
    if not isinstance(acceptable_answers, list):
        raise TypeError("acceptable_answers must be a list")

    normalized = user_answer.strip().lower()
    return normalized in [ans.lower() for ans in acceptable_answers]
```

### Async Function

```python
async def load_progress_async(file_path: Path) -> ProgressSession:
    """Load progress from file asynchronously.

    Args:
        file_path: Path to progress JSON file

    Returns:
        ProgressSession object with user's learning progress

    Raises:
        FileNotFoundError: If progress file does not exist
        JSONDecodeError: If file contains invalid JSON
    """
    # Implementation
```

## Rules

1. **First line** (summary): Concise description of what function does, no longer than 79 characters
2. **Args section**: List each parameter with type annotation and description
3. **Returns section**: Describe what is returned and its type
4. **Raises section**: List exceptions raised, with conditions that trigger them
5. **Blank lines**: One blank line between sections
6. **No implementation details**: Docstring explains WHAT, not HOW
7. **No typos**: Use grammar check tools; unclear docs are worse than no docs

## Multi-line Args Example

```python
def create_learning_session(
    module_id: str,
    learner_name: str,
    difficulty: str = "beginner",
    skip_intro: bool = False,
) -> LearningSession:
    """Create and initialize a new learning session.

    Args:
        module_id: Identifier of the module to load
        learner_name: Name of the learner (for progress tracking)
        difficulty: Difficulty level (beginner/intermediate/advanced)
        skip_intro: If True, skip introductory content

    Returns:
        Initialized LearningSession ready for questions

    Raises:
        FileNotFoundError: If module_id module file not found
        ValueError: If difficulty not one of valid options
    """
    # Implementation
```

## Special Cases

### Properties

```python
@property
def progress_percentage(self) -> float:
    """Calculate completion percentage of current module."""
    # Implementation
```

### Class Methods

```python
@classmethod
def from_file(cls, file_path: Path) -> "ProgressSession":
    """Load progress from JSON file.

    Args:
        file_path: Path to progress.json file

    Returns:
        ProgressSession instance loaded from file

    Raises:
        FileNotFoundError: If file does not exist
    """
    # Implementation
```

### Private Methods

```python
def _normalize_answer(self, answer: str) -> str:
    """Normalize answer for case-insensitive comparison.

    Args:
        answer: Raw answer string from user

    Returns:
        Lowercase, whitespace-trimmed version of answer
    """
    return answer.strip().lower()
```

## Type Hints in Docstrings

Always match docstring type descriptions with actual type annotations:

```python
def process_data(items: list[dict[str, Any]]) -> tuple[int, str]:
    """Process data items and return summary.

    Args:
        items: List of dictionaries with key-value pairs

    Returns:
        Tuple of (count: int, status: str)

    Raises:
        ValueError: If items list is empty
    """
```

## Validation Checklist

Before committing code with functions:

- [ ] All public functions have docstrings
- [ ] All docstrings have summary line
- [ ] Args section lists all parameters
- [ ] Returns section describes return value
- [ ] Raises section lists exceptions (at least those explicitly raised)
- [ ] No typos or grammatical errors
- [ ] Docstring type descriptions match actual type annotations
- [ ] Lines wrap at 79 characters for readability
- [ ] Private methods (`_func`) have docstrings for complex logic
