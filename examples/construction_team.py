"""
Multi-Agent Construction Team Example

Shows how three specialized construction agents collaborate:
1. Project Manager - Timeline and coordination focus
2. Architectural Specialist - Plans interpretation and buildability
3. Value Engineering Specialist - Cost optimization and ROI

This demonstrates AG2's GroupChat pattern with PersonaAgents.
"""

from ag2_persona import PersonaAgent
from autogen import GroupChat, GroupChatManager, UserProxyAgent

def create_construction_team():
    """Create a team of construction specialists"""

    # Load the three construction specialists
    project_manager = PersonaAgent.from_yaml("library/construction_project_manager.yaml")
    architect_specialist = PersonaAgent.from_yaml("library/architectural_specialist.yaml")
    value_engineer = PersonaAgent.from_yaml("library/value_engineering_specialist.yaml")

    # Create a user proxy to represent the client/owner
    client = UserProxyAgent(
        name="client",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0
    )

    # Create GroupChat for team collaboration
    groupchat = GroupChat(
        agents=[client, project_manager, architect_specialist, value_engineer],
        messages=[],
        max_round=10
    )

    # Create the GroupChatManager to coordinate
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"model": "gpt-4", "temperature": 0.3}
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

    # In real usage with AG2 installed:
    # analyze_project_scenario()

    # For demonstration without AG2:
    print("\nExample Analysis Output:")
    print("\nPROJECT MANAGER: 'The 4-month facade delay is critical path...")
    print("We need to explore fast-track alternatives or phase the facade...'")
    print("\nARCHITECTURAL SPECIALIST: 'The MEP conflict requires immediate")
    print("resolution. We can raise the structure 2ft or redesign ductwork...'")
    print("\nVALUE ENGINEER: 'I recommend a flat panel system with accent curves")
    print("saving $3M and 3 months. ROI analysis shows...'")
    print("\n[Team continues collaborating to reach optimal solution]")

if __name__ == "__main__":
    main()