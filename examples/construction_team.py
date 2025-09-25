"""
Multi-Agent Construction Team Example

Shows how three specialized construction agents collaborate:
1. Project Manager - Timeline and coordination focus
2. Architectural Specialist - Plans interpretation and buildability
3. Value Engineering Specialist - Cost optimization and ROI

This demonstrates AG2's GroupChat pattern with PersonaAgents.

Prerequisites:
    # Install dependencies
    

    # Setup Ollama with Gemma3:4b (local, no API key needed)
    ollama pull gemma2:2b
    ollama serve

    # Alternative: For OpenAI instead of Ollama:
    # pip install "ag2[openai]" && export OPENAI_API_KEY=your_key

    (Uses local ../ag2_persona development version)

Run:
    cd examples/
    python construction_team.py
"""

import sys
from pathlib import Path

# Add the parent directory to path to import local ag2_persona
sys.path.insert(0, str(Path(__file__).parent.parent))

from ag2_persona import PersonaAgent, HumanInputMode
from ag2_persona.persona_builder import PersonaBuilder
from autogen import GroupChat, GroupChatManager, UserProxyAgent

def create_construction_team():
    """Create a team of construction specialists using PersonaBuilder"""

    # Define LLM config once for all agents (Ollama with Gemma2:2b)
    llm_config = {
        "config_list": [
            {
                "model": "gemma2:2b",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # placeholder for Ollama
            }
        ],
        "temperature": 0.3
    }

    # Create construction specialists using PersonaBuilder with AG2 best practices
    project_manager = (PersonaBuilder("project_manager")
                       .from_yaml("library/construction_project_manager.yaml")
                       .with_llm_config(llm_config)
                       .with_human_input_mode(HumanInputMode.NEVER)
                       .with_description("Manages project timelines, coordinates trades, resolves scheduling conflicts")
                       .build())

    architect_specialist = (PersonaBuilder("architect_specialist")
                           .from_yaml("library/architectural_specialist.yaml")
                           .with_llm_config(llm_config)
                           .with_human_input_mode(HumanInputMode.NEVER)
                           .with_description("Reviews architectural plans, identifies conflicts, ensures buildability")
                           .build())

    value_engineer = (PersonaBuilder("value_engineer")
                     .from_yaml("library/value_engineering_specialist.yaml")
                     .with_llm_config(llm_config)
                     .with_human_input_mode(HumanInputMode.NEVER)
                     .with_description("Optimizes costs, identifies value engineering opportunities, maximizes ROI")
                     .build())

    # Create a user proxy to represent the client/owner
    client = UserProxyAgent(
        name="client",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0
    )

    # Create GroupChat for team collaboration with AG2 best practices
    groupchat = GroupChat(
        agents=[client, project_manager, architect_specialist, value_engineer],
        speaker_selection_method="auto",  # Uses agent descriptions for selection
        messages=[],
        max_round=10,
        send_introductions=True  # Optional: agents introduce themselves
    )

    # Create the GroupChatManager to coordinate - using same LLM config
    manager = GroupChatManager(
        name="construction_manager",
        groupchat=groupchat,
        llm_config=llm_config
    )

    return client, manager

def analyze_project_scenario():
    """Example scenario: Analyzing a complex construction decision"""

    client, manager = create_construction_team()

    # Complex scenario requiring all three perspectives
    scenario = """
    We're evaluating a 200,000 sq ft mixed-use development with these challenges:

    1. The architect specified a complex curved glass facade ($8M) that the structural
       engineer says will take 4 extra months to fabricate and install.

    2. The mechanical systems in the original design conflict with the ceiling heights
       in the retail spaces (need 14ft clear, currently showing 12ft).

    3. We have a hard deadline in 18 months due to anchor tenant lease commitments,
       with $50K/day penalties for delays.

    4. Current budget is $65M but bids are coming in at $72M.

    What are your recommendations for moving forward while balancing design intent,
    timeline, and budget constraints?
    """

    # Initiate the group discussion
    client.initiate_chat(
        manager,
        message=scenario
    )

def main():
    """Demonstrate the construction team in action"""

    print("=" * 60)
    print("CONSTRUCTION TEAM COLLABORATION EXAMPLE")
    print("=" * 60)
    print("\nThis example shows how three specialized construction agents")
    print("work together to solve complex project challenges:\n")
    print("• Project Manager: Focus on timeline and coordination")
    print("• Architectural Specialist: Ensure buildability and code compliance")
    print("• Value Engineering: Optimize costs and ROI\n")
    print("-" * 60)

    try:
        # Run the actual AG2 conversation
        analyze_project_scenario()
    except Exception as e:
        print(f"\nError running AG2 conversation: {e}")
        print("\nThis likely means:")
        print("1. AG2 not properly installed with LLM support")
        print("2. No LLM configured or API key missing")
        print("3. Missing ruamel.yaml: pip install ruamel.yaml")
        print("\nInstallation options:")
        print('  OpenAI: pip install "ag2[openai]" && export OPENAI_API_KEY=key')
        print("  Ollama: pip install ag2 (local models, no API key needed)")

if __name__ == "__main__":
    main()