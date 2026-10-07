"""Command-line entry point for security evaluation."""

import json

from security.evaluation import run_security_evaluation


if __name__ == "__main__":
    print(json.dumps(run_security_evaluation(), indent=2))
