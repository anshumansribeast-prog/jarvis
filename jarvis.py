"""
Jarvis compatibility shim — launches AnshuX while preserving the old entry point.
"""

from ansux.core.assistant import main

if __name__ == "__main__":
    main()
