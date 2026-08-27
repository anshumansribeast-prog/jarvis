import tempfile
import unittest
from pathlib import Path

from anshux_os.kernel import AnshuXKernel
from anshux_os.memory import MemoryStore
from anshux_os.permissions import Risk


class AnshuXOSTest(unittest.TestCase):
    def make_kernel(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return AnshuXKernel(MemoryStore(Path(tmp.name) / "memory.json"))

    def test_builtin_agents(self):
        kernel = self.make_kernel()
        names = {item["name"] for item in kernel.agents.list()}
        self.assertEqual(names, {"AnshuX", "Ada", "Beast"})

    def test_action_requires_approval_token(self):
        kernel = self.make_kernel()
        item = kernel.request_action("restart", Risk.DANGEROUS, "restart computer")
        self.assertIn(item["action_id"], kernel.permissions.pending())

    def test_memory_round_trip(self):
        kernel = self.make_kernel()
        kernel.memory.remember("project", "AnshuX OS")
        self.assertEqual(kernel.memory.recall("project"), "AnshuX OS")


if __name__ == "__main__":
    unittest.main()
