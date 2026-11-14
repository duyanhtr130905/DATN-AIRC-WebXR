"""Tests for discovery and owned-process cleanup, not XR hardware."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("runner", Path(__file__).with_name("run_browser_smoke.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class RunnerTests(unittest.TestCase):
    def test_explicit_browser_wins(self):
        self.assertEqual(runner.find_browser({"CHROME_BIN": "/custom/chrome"}, lambda _: None, lambda p: p == "/custom/chrome"), "/custom/chrome")

    def test_invalid_explicit_browser_does_not_fall_back(self):
        self.assertIsNone(runner.find_browser({"CHROME_BIN": "/missing"}, lambda _: None, lambda _: False))

    def test_path_discovery(self):
        self.assertEqual(runner.find_browser({}, lambda p: "/bin/chromium" if p == "chromium" else None, lambda _: True), "/bin/chromium")

    def test_windows_common_location(self):
        expected = str(Path("C:/Apps") / "Google/Chrome/Application/chrome.exe")
        self.assertEqual(runner.find_browser({"PROGRAMFILES": "C:/Apps"}, lambda _: None, lambda p: p == expected), expected)

    def test_no_browser(self):
        self.assertIsNone(runner.find_browser({}, lambda _: None, lambda _: False))

    def test_already_exited_process_is_not_killed(self):
        process = Mock(); process.poll.return_value = 0
        self.assertTrue(runner.stop_browser(process))
        process.kill.assert_not_called()

    def test_windows_timeout_targets_only_owned_pid(self):
        process = Mock(pid=12345)
        process.wait.side_effect = [subprocess.TimeoutExpired("owned-browser", 5), 0]
        process.poll.return_value = 0
        with patch.object(runner.os, "name", "nt"), patch.object(runner.subprocess, "run") as run:
            self.assertTrue(runner.stop_browser(process))
            self.assertEqual(run.call_args.args[0], ["taskkill", "/PID", "12345", "/T", "/F"])

    def test_timeout_terminates_only_owned_process(self):
        process = Mock(pid=12345)
        process.wait.side_effect = [subprocess.TimeoutExpired("owned-browser", 5), 0]
        process.poll.return_value = 0
        with patch.object(runner.os, "name", "posix"), patch.object(runner.os, "killpg", create=True) as killpg:
            self.assertTrue(runner.stop_browser(process))
            killpg.assert_called_once_with(12345, runner.signal.SIGTERM)

if __name__ == "__main__":
    unittest.main()
