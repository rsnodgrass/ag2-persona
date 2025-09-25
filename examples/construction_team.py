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

from autogen import GroupChat, GroupChatManager, UserProxyAgent

from ag2_persona.persona_builder import PersonaBuilder


def create_construction_team() -> tuple[UserProxyAgent, GroupChatManager]:
    """
    Create a team of construction specialists using PersonaBuilder.

    This creates a hybrid conversation pattern where UserProxyAgent serves as human stakeholder proxy:
    1. Client (UserProxyAgent) represents the human stakeholder with real construction challenges
    2. Client presents complex scenario with business constraints, then steps back (max_consecutive_auto_reply=0)
    3. Three AI specialists collaborate autonomously to analyze the human's problem
    4. GroupChatManager orchestrates using agent descriptions for speaker selection

    The UserProxyAgent here acts as a "human client proxy" - it doesn't require human input,
    but conceptually represents the human perspective and constraints in the collaborative discussion.

    Returns:
        tuple: (client_initiator, group_manager) for starting collaborative discussions
    """

    # Define LLM config once for all agents (Ollama with Tinyllama just for fast demo)
    llm_config = {
        "config_list": [
            {
                "model": "tinyllama",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # placeholder for Ollama
                "price": [0, 0],  # Free local model - suppresses cost warnings
            }
        ],
        "temperature": 0.3,
    }

    # Create set of construction specialists for evaluating projects
    # using PersonaBuilder along with AG2 best practices.
    project_manager = (
        PersonaBuilder("project_manager")
        .from_yaml("library/construction_project_manager.yaml")
        .llm_config(llm_config)
        .with_human_input_never()
        .build()
    )

    architect_specialist = (
        PersonaBuilder("architect_specialist")
        .from_yaml("library/architectural_specialist.yaml")
        .llm_config(llm_config)
        .with_human_input_never()
        .build()
    )

    value_engineer = (
        PersonaBuilder("value_engineer")
        .from_yaml("library/value_engineering_specialist.yaml")
        .llm_config(llm_config)
        .with_human_input_never()
        .description("Optimizes costs, identifies value engineering opportunities, maximizes ROI")
        .build()
    )

    # Create a UserProxyAgent as the human client/stakeholder proxy
    #
    # Why UserProxyAgent is Perfect Here:
    # - Conceptually represents the human client with real construction challenges
    # - Acts as a proxy for human stakeholder interests and constraints
    # - Brings real-world problems to the expert AI team for collaborative analysis
    # - Steps back after problem presentation to let specialists work autonomously
    #
    # This demonstrates a sophisticated AG2 pattern: human problems → AI collaboration
    client = UserProxyAgent(
        name="client",
        human_input_mode="NEVER",  # No human interaction during AI collaboration
        max_consecutive_auto_reply=0,  # Present problem as human proxy, then step back
        code_execution_config={
            "use_docker": False
        },  # Disable Docker requirement for code execution
    )

    # Create GroupChat for team collaboration with AG2 best practices
    groupchat = GroupChat(
        agents=[client, project_manager, architect_specialist, value_engineer],
        speaker_selection_method="auto",  # Uses agent descriptions for selection
        messages=[],
        max_round=10,
        send_introductions=True,  # Optional: agents introduce themselves
    )

    # Create the GroupChatManager to coordinate - using same LLM config
    manager = GroupChatManager(
        name="construction_manager", groupchat=groupchat, llm_config=llm_config
    )

    return client, manager


def analyze_project_scenario() -> None:
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

    # Start the hybrid conversation pattern using UserProxyAgent as human client proxy:
    # 1. Client (UserProxyAgent) provides the complex scenario representing human stakeholder concerns
    # 2. GroupChatManager takes over, using agent descriptions to select speakers
    # 3. Three AI specialists collaborate autonomously to analyze the human's construction problem
    client.initiate_chat(manager, message=scenario)


def main() -> None:
    """Demonstrate the construction team in action"""

    print("=" * 60)
    print("CONSTRUCTION TEAM COLLABORATION EXAMPLE")
    print("=" * 60)
    print("\nThis example demonstrates a hybrid conversation pattern:")
    print(
        "1. UserProxyAgent acts as proxy for a human client presenting a real construction challenges"
    )
    print("2. Client steps back, while AI specialists collaborate autonomously")
    print("3. GroupChatManager orchestrates the discussion using agent descriptions")
    print(
        "4. This represents common real-world pattern: human problems → expert AI collaboration\n"
    )

    print("Three specialized construction agents work together:")
    print("• Project Manager: Timeline and coordination expertise")
    print("• Architectural Specialist: Design buildability and code compliance")
    print("• Value Engineering: Cost optimization and ROI analysis\n")
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
        print("          ollama pull tinyllama ; ollama serve")


if __name__ == "__main__":
    main()
