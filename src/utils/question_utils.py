class QuestionUtility:
    @staticmethod
    def ask_yes_no(question: str) -> bool:
        """Ask a yes/no question and return boolean result."""
        answer = input(f"{question} (y/n): ").lower().strip()
        return answer in ["y", "yes"]
