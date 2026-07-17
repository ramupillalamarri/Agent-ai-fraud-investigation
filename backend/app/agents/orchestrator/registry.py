import logging
import threading
from typing import Dict, Any, List, Optional
from app.agents.base.base_agent import BaseAgent

logger = logging.getLogger("app.agents.orchestrator.registry")

class RegistryError(Exception):
    """Base exception for all registry-related errors."""
    pass

class DuplicateAgentError(RegistryError):
    """Raised when trying to register an agent under an ID that already exists."""
    pass

class AgentNotFoundError(RegistryError):
    """Raised when an agent lookup by ID or name fails."""
    pass

class InvalidAgentError(RegistryError):
    """Raised when a registered object does not conform to the BaseAgent contract."""
    pass

class AgentRegistry:
    """Thread-safe registry for managing autonomous AI investigation agents."""

    def __init__(self) -> None:
        """Initializes the agent storage dictionary and locks."""
        self._agents: Dict[str, BaseAgent] = {}
        self._lock = threading.Lock()
        logger.info("Initialized AgentRegistry")

    def register(self, agent: BaseAgent) -> None:
        """Registers a new agent instance, ensuring validation checks and thread-safety.
        
        Args:
            agent: An instance of an agent inheriting from BaseAgent.
            
        Raises:
            InvalidAgentError: If validation of parameters or inheritance checks fail.
            DuplicateAgentError: If an agent with the same ID is already registered.
        """
        if not isinstance(agent, BaseAgent):
            raise InvalidAgentError("Registered object does not inherit from BaseAgent.")
            
        if not getattr(agent, "agent_id", None):
            raise InvalidAgentError("Agent lacks a valid 'agent_id'.")
            
        if not getattr(agent, "agent_name", None):
            raise InvalidAgentError("Agent lacks a valid 'agent_name'.")
            
        if getattr(agent, "execution_priority", None) is None:
            raise InvalidAgentError("Agent lacks an 'execution_priority' definition.")

        with self._lock:
            if agent.agent_id in self._agents:
                logger.warning("Duplicate registration attempt for agent ID: %s", agent.agent_id)
                raise DuplicateAgentError(f"Agent with ID '{agent.agent_id}' is already registered.")
            
            self._agents[agent.agent_id] = agent
            logger.info("Registered agent: %s (ID: %s)", agent.agent_name, agent.agent_id)

    def unregister(self, agent_id: str) -> None:
        """Removes an agent from the registry.
        
        Args:
            agent_id: Target agent unique ID.
            
        Raises:
            AgentNotFoundError: If the ID does not exist in registry.
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning("Unregister failed. Agent ID not found: %s", agent_id)
                raise AgentNotFoundError(f"Agent with ID '{agent_id}' not found.")
            
            removed = self._agents.pop(agent_id)
            logger.info("Unregistered agent: %s (ID: %s)", removed.agent_name, agent_id)

    def clear(self) -> None:
        """Clears all registered agents."""
        with self._lock:
            self._agents.clear()
            logger.info("Agent registry cleared.")

    def get_agent(self, agent_id: str) -> BaseAgent:
        """Looks up a registered agent by ID.
        
        Args:
            agent_id: Unique ID of the agent.
            
        Returns:
            BaseAgent: The registered agent instance.
            
        Raises:
            AgentNotFoundError: If the ID does not exist in registry.
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning("Agent ID not found during lookup: %s", agent_id)
                raise AgentNotFoundError(f"Agent with ID '{agent_id}' not found.")
            return self._agents[agent_id]

    def get_agent_by_name(self, name: str) -> BaseAgent:
        """Looks up a registered agent by human-readable name.
        
        Args:
            name: The agent_name string.
            
        Returns:
            BaseAgent: The registered agent instance.
            
        Raises:
            AgentNotFoundError: If no agent matches the name.
        """
        with self._lock:
            for agent in self._agents.values():
                if agent.agent_name == name:
                    return agent
            logger.warning("Agent name not found during lookup: %s", name)
            raise AgentNotFoundError(f"Agent with name '{name}' not found.")

    def get_all_agents(self) -> List[BaseAgent]:
        """Retrieves a list of all registered agents."""
        with self._lock:
            return list(self._agents.values())

    def get_enabled_agents(self) -> List[BaseAgent]:
        """Retrieves all enabled agents sorted by execution_priority ascending."""
        with self._lock:
            enabled = [agent for agent in self._agents.values() if agent.enabled]
            return sorted(enabled, key=lambda a: a.execution_priority)

    def get_disabled_agents(self) -> List[BaseAgent]:
        """Retrieves all disabled agents."""
        with self._lock:
            return [agent for agent in self._agents.values() if not agent.enabled]

    def get_agents_by_feature(self, feature: str) -> List[BaseAgent]:
        """Filters registered agents supporting a specific capability flag.
        
        Args:
            feature: The target string capability (e.g. 'device', 'merchant').
            
        Returns:
            List[BaseAgent]: List of matching agents.
        """
        with self._lock:
            return [agent for agent in self._agents.values() if feature in agent.supported_features]

    def enable(self, agent_id: str) -> None:
        """Enables the target agent.
        
        Args:
            agent_id: Unique ID of the agent.
            
        Raises:
            AgentNotFoundError: If the ID does not exist in registry.
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning("Enable failed. Agent ID not found: %s", agent_id)
                raise AgentNotFoundError(f"Agent with ID '{agent_id}' not found.")
            self._agents[agent_id].enabled = True
            logger.info("Enabled agent: %s (ID: %s)", self._agents[agent_id].agent_name, agent_id)

    def disable(self, agent_id: str) -> None:
        """Disables the target agent.
        
        Args:
            agent_id: Unique ID of the agent.
            
        Raises:
            AgentNotFoundError: If the ID does not exist in registry.
        """
        with self._lock:
            if agent_id not in self._agents:
                logger.warning("Disable failed. Agent ID not found: %s", agent_id)
                raise AgentNotFoundError(f"Agent with ID '{agent_id}' not found.")
            self._agents[agent_id].enabled = False
            logger.info("Disabled agent: %s (ID: %s)", self._agents[agent_id].agent_name, agent_id)

    def list_agent_metadata(self) -> List[Dict[str, Any]]:
        """Compiles metadata specifications for all registered agents.
        
        Returns:
            List[Dict[str, Any]]: List of metadata specification dictionaries.
        """
        with self._lock:
            metadata_list = []
            for agent in self._agents.values():
                metadata_list.append({
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "description": agent.description,
                    "version": agent.version,
                    "execution_priority": agent.execution_priority,
                    "enabled": agent.enabled,
                    "supported_features": agent.supported_features
                })
            return metadata_list

if __name__ == "__main__":
    import sys
    import os
    
    # Setup path so standard imports work when executed directly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    
    from app.agents.models.investigation_context import InvestigationContext
    from app.agents.models.agent_result import AgentResult
    
    # 1. Define dummy classes to verify BaseAgent compliance
    class DummyCustomerAgent(BaseAgent):
        def _execute(self, context: InvestigationContext) -> AgentResult:
            return self.create_success_result([], [], [])
        def validate(self, context: InvestigationContext) -> None:
            pass
        def health_check(self) -> bool:
            return True

    class DummyDeviceAgent(BaseAgent):
        def _execute(self, context: InvestigationContext) -> AgentResult:
            return self.create_success_result([], [], [])
        def validate(self, context: InvestigationContext) -> None:
            pass
        def health_check(self) -> bool:
            return True

    # 2. Instantiate and register agents
    registry = AgentRegistry()
    
    customer_agent = DummyCustomerAgent(
        agent_id="customer_agent_id",
        agent_name="CustomerAgent",
        description="Analyzes customer properties",
        version="1.0",
        execution_priority=1
    )
    
    device_agent = DummyDeviceAgent(
        agent_id="device_agent_id",
        agent_name="DeviceAgent",
        description="Analyzes device properties",
        version="1.0",
        execution_priority=5
    )
    
    registry.register(customer_agent)
    print(f"Registered agent: {customer_agent.agent_name}")
    
    registry.register(device_agent)
    print(f"Registered agent: {device_agent.agent_name}")
    
    # 3. Disable DeviceAgent
    registry.disable("device_agent_id")
    print(f"Disabled {device_agent.agent_name}")
    
    # 4. Request enabled agents
    print("Enabled agents:")
    for agent in registry.get_enabled_agents():
        print(agent.agent_name)
        
    # 5. Print metadata
    print("Metadata:")
    for meta in registry.list_agent_metadata():
        print(f"{meta['agent_name']} v{meta['version']}")
