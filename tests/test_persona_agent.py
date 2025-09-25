"""
Test suite for AG2 PersonaAgent.

This module contains comprehensive tests for the PersonaAgent implementation,
ensuring reliability and compatibility with AG2 patterns.
"""

import unittest

from ag2_persona.persona_agent import AG2_AVAILABLE, PersonaAgent


class TestPersonaAgent(unittest.TestCase):
    """Test PersonaAgent functionality."""

    def test_basic_creation(self):
        """Test creating a basic PersonaAgent."""
        agent = PersonaAgent(name="test_agent", role="Tester", goal="Test the system")

        self.assertEqual(agent.name, "test_agent")
        self.assertEqual(agent.role, "Tester")
        self.assertEqual(agent.goal, "Test the system")
        self.assertEqual(agent.backstory, "")
        self.assertEqual(agent.constraints, [])

    def test_full_creation(self):
        """Test creating a PersonaAgent with all parameters."""
        agent = PersonaAgent(
            name="reviewer",
            role="Code Reviewer",
            goal="Review code quality",
            backstory="10 years of experience",
            constraints=["Focus on Python", "Check security"],
            llm_config={"model": "gpt-4", "temperature": 0.3},
        )

        self.assertEqual(agent.role, "Code Reviewer")
        self.assertEqual(agent.backstory, "10 years of experience")
        self.assertEqual(len(agent.constraints), 2)
        self.assertIn("Focus on Python", agent.constraints)
        self.assertEqual(agent.llm_config["model"], "gpt-4")

    def test_system_message_composition(self):
        """Test that system message is properly composed."""
        agent = PersonaAgent(
            name="test",
            role="Analyst",
            goal="Analyze data",
            backstory="Expert in statistics",
            constraints=["Use Python", "Be concise"],
        )

        message = agent.system_message

        # Check all components are present
        self.assertIn("Role: Analyst", message)
        self.assertIn("Analyze data", message)
        self.assertIn("Expert in statistics", message)
        self.assertIn("Use Python", message)
        self.assertIn("Be concise", message)

        # Check structure
        self.assertIn("# Role:", message)
        self.assertIn("## Goal", message)
        self.assertIn("## Background", message)
        self.assertIn("## Constraints", message)

    def test_system_message_minimal(self):
        """Test system message with minimal components."""
        agent = PersonaAgent(name="minimal", role="Helper", goal="Help users")

        message = agent.system_message

        self.assertIn("Role: Helper", message)
        self.assertIn("Help users", message)
        self.assertNotIn("Background", message)
        self.assertNotIn("Constraints", message)

    def test_update_goal(self):
        """Test dynamic goal updating."""
        agent = PersonaAgent(name="assistant", role="Assistant", goal="General help")

        original_message = agent.system_message

        # Update goal
        agent.update_goal("Focus on technical documentation")

        # Check goal updated
        self.assertEqual(agent.goal, "Focus on technical documentation")

        # Check system message regenerated
        self.assertNotEqual(agent.system_message, original_message)
        self.assertIn("Focus on technical documentation", agent.system_message)

    def test_add_remove_constraints(self):
        """Test adding and removing constraints."""
        agent = PersonaAgent(name="test", role="Tester", goal="Test system")

        # Start with no constraints
        self.assertEqual(len(agent.constraints), 0)
        self.assertNotIn("Constraints", agent.system_message)

        # Add constraints
        agent.add_constraint("Be polite")
        agent.add_constraint("Use formal language")

        self.assertEqual(len(agent.constraints), 2)
        self.assertIn("Be polite", agent.system_message)
        self.assertIn("Use formal language", agent.system_message)

        # Test duplicate addition (should not add)
        agent.add_constraint("Be polite")
        self.assertEqual(len(agent.constraints), 2)

        # Remove constraint
        agent.remove_constraint("Be polite")

        self.assertEqual(len(agent.constraints), 1)
        self.assertNotIn("Be polite", agent.system_message)
        self.assertIn("Use formal language", agent.system_message)

        # Test removing non-existent constraint (should not error)
        agent.remove_constraint("Non-existent")
        self.assertEqual(len(agent.constraints), 1)

    def test_backward_compatibility(self):
        """Test that additional system_message is preserved."""
        agent = PersonaAgent(
            name="test",
            role="Tester",
            goal="Test system",
            system_message="Custom instructions here",
        )

        self.assertIn("Role: Tester", agent.system_message)
        self.assertIn("Additional Instructions:", agent.system_message)
        self.assertIn("Custom instructions here", agent.system_message)

    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        original = PersonaAgent(
            name="analyst",
            role="Data Analyst",
            goal="Analyze datasets",
            backstory="PhD in Statistics",
            constraints=["Use pandas", "Create visualizations"],
            llm_config={"model": "gpt-4", "temperature": 0.5},
        )

        # Export to dict
        config = original.to_dict()

        self.assertEqual(config["name"], "analyst")
        self.assertEqual(config["role"], "Data Analyst")
        self.assertEqual(len(config["constraints"]), 2)
        self.assertEqual(config["llm_config"]["model"], "gpt-4")

        # Create from dict
        restored = PersonaAgent.from_dict(config)

        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.role, original.role)
        self.assertEqual(restored.goal, original.goal)
        self.assertEqual(restored.backstory, original.backstory)
        self.assertEqual(restored.constraints, original.constraints)
        self.assertEqual(restored.llm_config, original.llm_config)

    def test_repr(self):
        """Test string representation."""
        agent = PersonaAgent(name="test", role="Tester", goal="Test the system thoroughly")

        repr_str = repr(agent)
        self.assertIn("PersonaAgent", repr_str)
        self.assertIn("test", repr_str)
        self.assertIn("Tester", repr_str)

        # Test long goal truncation
        agent_long_goal = PersonaAgent(
            name="test2",
            role="Tester",
            goal="A" * 100,  # Very long goal
        )

        repr_long = repr(agent_long_goal)
        self.assertIn("...", repr_long)  # Should be truncated


class TestPersonaBuilder(unittest.TestCase):
    """Test PersonaBuilder functionality."""

    def test_persona_builder_basic(self):
        """Test basic PersonaBuilder usage."""
        from ag2_persona import PersonaBuilder

        agent = PersonaBuilder("helper").role("Helper").goal("Assist users").build()

        self.assertIsInstance(agent, PersonaAgent)
        self.assertEqual(agent.role, "Helper")
        self.assertEqual(agent.name, "helper")

    def test_persona_builder_from_dict(self):
        """Test creating agent from config dictionary using PersonaBuilder."""
        from ag2_persona import PersonaBuilder

        config = {
            "role": "Tester",
            "goal": "Test system",
            "backstory": "Expert tester",
            "constraints": ["Be thorough"],
        }

        agent = PersonaBuilder("test").from_dict(config).build()

        self.assertEqual(agent.name, "test")
        self.assertEqual(agent.role, "Tester")
        self.assertEqual(agent.backstory, "Expert tester")
        self.assertEqual(agent.constraints, ["Be thorough"])


class TestAG2Integration(unittest.TestCase):
    """Test integration with AG2 features."""

    @unittest.skipIf(not AG2_AVAILABLE, "AG2 not available")
    def test_inheritance(self):
        """Test that PersonaAgent properly inherits from ConversableAgent."""
        agent = PersonaAgent(name="test", role="Tester", goal="Test")

        # Should have ConversableAgent methods and properties
        self.assertTrue(hasattr(agent, "name"))
        self.assertTrue(hasattr(agent, "system_message"))
        self.assertTrue(hasattr(agent, "llm_config"))

    def test_mock_integration(self):
        """Test with mock ConversableAgent when AG2 not available."""
        agent = PersonaAgent(name="test", role="Tester", goal="Test")

        # Basic properties should work regardless
        self.assertEqual(agent.name, "test")
        self.assertIsInstance(agent.system_message, str)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_strings(self):
        """Test handling of empty strings."""
        agent = PersonaAgent(
            name="test",
            role="",  # Empty role
            goal="",  # Empty goal
        )

        self.assertEqual(agent.role, "")
        self.assertEqual(agent.goal, "")
        # Should still create valid system message
        self.assertIn("Role:", agent.system_message)

    def test_none_constraints(self):
        """Test handling of None constraints."""
        agent = PersonaAgent(name="test", role="Tester", goal="Test", constraints=None)

        self.assertEqual(agent.constraints, [])

    def test_unicode_content(self):
        """Test handling of unicode characters."""
        agent = PersonaAgent(
            name="tëst",
            role="Tëstër 🧪",
            goal="Tëst systëm with ëmojis 🚀",
            backstory="Ëxpert in ïnternationalization",
        )

        self.assertIn("Tëstër 🧪", agent.system_message)
        self.assertIn("🚀", agent.system_message)

    def test_very_long_content(self):
        """Test handling of very long content."""
        long_goal = "A" * 10000  # Very long goal
        long_backstory = "B" * 5000  # Very long backstory

        agent = PersonaAgent(name="test", role="Tester", goal=long_goal, backstory=long_backstory)

        self.assertEqual(len(agent.goal), 10000)
        self.assertEqual(len(agent.backstory), 5000)
        self.assertIn("A" * 100, agent.system_message)  # Should contain the content


def run_tests() -> None:
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
