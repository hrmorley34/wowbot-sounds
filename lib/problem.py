from typing import List, Optional


class Problem:
    def __init__(self, problem: str, context: Optional[str] = None):
        self.problem = problem
        self.context = context
        print(f"{context}: {problem}")

    problem: str
    context: Optional[str]


Problems = List[Problem]
