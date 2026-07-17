import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from app.agents.models.investigation_context import InvestigationContext
from app.agents.models.agent_result import AgentResult

class BaseAgent(ABC):
    """Abstract Base Class defining the operational contract and execution lifecycle 
    for all autonomous AI investigation agents within the retail fraud framework.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        description: str,
        version: str,
        enabled: bool = True,
        execution_priority: int = 10,
        supported_features: Optional[List[str]] = None
    ) -> None:
        """Initializes the base agent parameters.
        
        Args:
            agent_id: Unique string identifier for the agent instance.
            agent_name: Human readable name of the agent.
            description: Summary explanation of what indicators the agent inspects.
            version: Semver identifier.
            enabled: Toggle indicating if the agent should run.
            execution_priority: Relative execution order precedence (lower runs first).
            supported_features: List of string capability flags.
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        self.version = version
        self.enabled = enabled
        self.execution_priority = execution_priority
        self.supported_features = supported_features or []
        
        # Initialize specialized logger per agent class
        self.logger = logging.getLogger(f"app.agents.{self.agent_name}")
        
        # Telemetry metrics
        self._start_time: Optional[float] = None
        self._stop_time: Optional[float] = None

    @abstractmethod
    def _execute(self, context: InvestigationContext) -> AgentResult:
        """Protected core execution logic to be overridden by concrete agent subclasses.
        
        Args:
            context: Shared workspace state.
            
        Returns:
            AgentResult: The formulated investigation result.
        """
        pass

    @abstractmethod
    def validate(self, context: InvestigationContext) -> None:
        """Runs subclass-specific validation checks on the incoming context before execution.
        
        Must raise a ValueError if validation conditions fail.
        
        Args:
            context: Shared workspace state.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifies if external systems/APIs required by this agent are active and healthy.
        
        Returns:
            bool: True if healthy, False otherwise.
        """
        pass

    def execute(self, context: InvestigationContext) -> AgentResult:
        """Standardized public execution entrypoint wrapper enforcing validation schemas,
        timing telemetry, skipped behaviors, error handling, and context state logs.
        
        Args:
            context: Shared workspace state.
            
        Returns:
            AgentResult: Structured result of the execution.
        """
        self.logger.info("Agent started: %s (%s)", self.agent_name, self.agent_id)
        self.start_timer()
        
        try:
            # 1. Enforce Core Context Validation
            if not isinstance(context, InvestigationContext):
                raise ValueError("Invalid execution context: Context must be an instance of InvestigationContext.")
            
            if not getattr(context, "transaction_data", None):
                raise ValueError("Invalid execution context: Missing transaction data.")
                
            if not getattr(context, "prediction_result", None):
                raise ValueError("Invalid execution context: Missing prediction result.")
            
            # 2. Call custom subclass validations
            self.validate(context)
            
            # 3. Check enabled state
            if not self.enabled:
                self.log_warning("Agent %s is disabled. Skipping execution.", self.agent_name)
                self.stop_timer()
                return self.create_skipped_result("Agent disabled in configuration.")
                
            # 4. Trigger protected execution lifecycle
            result = self._execute(context)
            
            # 5. Type validation check on subclass result
            if not isinstance(result, AgentResult):
                raise TypeError(f"Subclass execution did not return a valid AgentResult instance. Got: {type(result)}")
                
            self.stop_timer()
            
            # 6. Set timing telemetry and update context states
            result.execution_time_ms = int((self._stop_time - self._start_time) * 1000)
            context.mark_agent_executed(self.agent_name)
            
            self.logger.info("Agent completed successfully: %s in %d ms", self.agent_name, result.execution_time_ms)
            return result
            
        except ValueError as ve:
            self.stop_timer()
            self.log_warning("Context validation failure: %s", str(ve))
            exec_time = int((self._stop_time - self._start_time) * 1000)
            return self.create_failure_result(
                findings=["Validation checks failed before agent execution."],
                recommendations=["Inspect input transaction schema and models context parameters."],
                error_msg=str(ve),
                execution_time_ms=exec_time,
                status="FAILED_VALIDATION"
            )
        except Exception as e:
            self.stop_timer()
            self.logger.exception("Runtime exception crashed execution of agent %s: %s", self.agent_name, str(e))
            exec_time = int((self._stop_time - self._start_time) * 1000)
            return self.create_failure_result(
                findings=["Unexpected runtime error interrupted execution flow."],
                recommendations=["Consult system traceback logs for engineering review."],
                error_msg=str(e),
                execution_time_ms=exec_time,
                status="FAILED"
            )

    # Reusable Utility Helpers
    def start_timer(self) -> None:
        """Starts the stopwatch timer metrics."""
        self._start_time = time.perf_counter()

    def stop_timer(self) -> None:
        """Stops the stopwatch timer metrics."""
        self._stop_time = time.perf_counter()
        if self._start_time is None:
            self._start_time = self._stop_time

    def log_info(self, msg: str, *args: Any) -> None:
        """Delegates messages to the info channel logger."""
        self.logger.info(msg, *args)

    def log_warning(self, msg: str, *args: Any) -> None:
        """Delegates messages to the warning channel logger."""
        self.logger.warning(msg, *args)

    def log_error(self, msg: str, *args: Any) -> None:
        """Delegates messages to the error channel logger."""
        self.logger.error(msg, *args)

    def create_success_result(
        self,
        findings: List[str],
        recommendations: List[str],
        evidence: List[Dict[str, Any]],
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Constructs a successful standardized AgentResult representation."""
        return AgentResult(
            agent_name=self.agent_name,
            status="SUCCESS",
            confidence_score=confidence_score,
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
            execution_time_ms=0,  # Dynamically set by base execution execute wrapper
            metadata=metadata or {}
        )

    def create_failure_result(
        self,
        findings: List[str],
        recommendations: List[str],
        error_msg: str,
        execution_time_ms: int = 0,
        status: str = "FAILED",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Constructs a failed standardized AgentResult representation."""
        meta = metadata or {}
        meta["error_message"] = error_msg
        return AgentResult(
            agent_name=self.agent_name,
            status=status,
            confidence_score=0.0,
            findings=findings,
            recommendations=recommendations,
            evidence=[],
            execution_time_ms=execution_time_ms,
            metadata=meta
        )

    def create_skipped_result(self, reason: str) -> AgentResult:
        """Constructs a skipped standardized AgentResult representation."""
        return AgentResult(
            agent_name=self.agent_name,
            status="SKIPPED",
            confidence_score=1.0,
            findings=["Agent skipped execution."],
            recommendations=["Verify configuration state enabled properties."],
            evidence=[],
            execution_time_ms=0,
            metadata={"skip_reason": reason}
        )
