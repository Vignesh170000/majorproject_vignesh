import unittest
from voice_assistant import VoiceAssistant


class TestVoiceAssistant(unittest.TestCase):
    """Automated unit test suite for AI Voice Assistant core engine."""

    @classmethod
    def setUpClass(cls):
        cls.assistant = VoiceAssistant(name="TestAria")

    def test_01_initialization(self):
        """Test assistant name and default property setup."""
        self.assertEqual(self.assistant.name, "TestAria")
        self.assertIsNotNone(self.assistant)

    def test_02_time_command(self):
        """Test current time command handling."""
        time_str = self.assistant.get_time()
        self.assertIn("The current time is", time_str)
        
        response, action_type, details = self.assistant.process_command("What is the current time?")
        self.assertEqual(action_type, "time")
        self.assertIn("The current time is", response)

    def test_03_greeting_command(self):
        """Test greeting response."""
        response, action_type, _ = self.assistant.process_command("Hello who are you")
        self.assertEqual(action_type, "greeting")
        self.assertIn("TestAria", response)

    def test_04_system_stats(self):
        """Test system statistics generation."""
        stats = self.assistant.get_system_stats()
        self.assertTrue("CPU Usage" in stats or "psutil" in stats)

        response, action_type, _ = self.assistant.process_command("show system status")
        self.assertEqual(action_type, "system_stats")

    def test_05_math_calculation(self):
        """Test math calculation engine."""
        calc_result = self.assistant.calculate_math("what is 45 plus 55")
        self.assertIn("100", calc_result)

        response, action_type, _ = self.assistant.process_command("calculate 12 times 8")
        self.assertEqual(action_type, "math")
        self.assertIn("96", response)

    def test_06_joke_command(self):
        """Test joke handler."""
        response, action_type, _ = self.assistant.process_command("Tell me a joke")
        self.assertEqual(action_type, "joke")
        self.assertTrue(len(response) > 5)

    def test_07_open_app_routing(self):
        """Test system application command matching."""
        response, action_type, _ = self.assistant.process_command("Open Notepad")
        self.assertEqual(action_type, "open_app")
        self.assertIn("Notepad", response)

        response, action_type, _ = self.assistant.process_command("Open YouTube")
        self.assertEqual(action_type, "open_app")
        self.assertIn("YouTube", response)

    def test_08_wikipedia_search(self):
        """Test Wikipedia search routing."""
        response, action_type, _ = self.assistant.process_command("Search Wikipedia for Python")
        self.assertEqual(action_type, "wikipedia")
        self.assertTrue("Wikipedia" in response or "Python" in response)

    def test_09_exit_command(self):
        """Test exit command routing."""
        response, action_type, _ = self.assistant.process_command("goodbye")
        self.assertEqual(action_type, "exit")
        self.assertIn("Goodbye", response)

    def test_10_describe_query(self):
        """Test search and describe query handling."""
        response, action_type, _ = self.assistant.process_command("describe me about artificial intelligence")
        self.assertEqual(action_type, "web_search")
        self.assertTrue(len(response) > 10)


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("[TEST] Running AI Voice Assistant Test Suite...\n")
    unittest.main()
