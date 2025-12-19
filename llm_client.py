class LLMAssistant:
    def __init__(self):
        # later: put API key, model name, etc. here
        pass

    def ask(self, prompt: str) -> str:
        """
        Take a prompt string and return a category string.
        For now this is a fake implementation so the pipeline works.
        """
        # TODO: replace this with a real API call later
        return "Food"


if __name__ == "__main__":
    assistant = LLMAssistant()
    print(assistant.ask("test prompt"))
