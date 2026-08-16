"""Core AnshuX tests (run on any platform)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ansux.core import greetings, memory, modes, planner
from ansux.security.command_classifier import RiskLevel, classify_command


class TestGreetings(unittest.TestCase):
    def test_startup_greeting_uses_names(self):
        text = greetings.startup_greeting()
        self.assertIn("Anshu", text)
        self.assertIn("AnshuX", text)


class TestModes(unittest.TestCase):
    def test_serious_mode_toggle(self):
        modes.set_mode(modes.AssistantMode.ASSISTANT)
        reply = modes.handle_mode_command("anshux serious mode")
        self.assertIsNotNone(reply)
        self.assertEqual(modes.current_mode(), modes.AssistantMode.SERIOUS)


class TestMemory(unittest.TestCase):
    def test_remember_and_recall(self):
        ok, _ = memory.remember("test favorite snack", "chips")
        self.assertTrue(ok)
        self.assertEqual(memory.recall("test favorite snack"), "chips")
        ok, _ = memory.forget("test favorite snack")
        self.assertTrue(ok)

    def test_rejects_secrets(self):
        ok, msg = memory.remember("api key", "secret123")
        self.assertFalse(ok)
        self.assertIn("won't store", msg.lower())


class TestSecurity(unittest.TestCase):
    def test_classify_dangerous(self):
        self.assertEqual(classify_command("rm -rf /"), RiskLevel.DANGEROUS)

    def test_classify_safe(self):
        self.assertEqual(classify_command("dir"), RiskLevel.SAFE)


class TestPlanner(unittest.TestCase):
    def test_resolve_project_from_settings(self):
        resolved = planner.resolve_project("open cosmos project")
        if resolved:
            name, path = resolved
            self.assertIn("cosmos", name)


if __name__ == "__main__":
    unittest.main()
