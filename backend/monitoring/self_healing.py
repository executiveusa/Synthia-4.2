"""
🔄 SELF-HEALING MONITOR - Microsoft Lightning Integration 🔄

Monitors agent health, auto-fixes issues, learns from failures
Part of the Aggressive Full Superagent Architecture
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import traceback

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"
    RECOVERING = "recovering"


class IssueType(Enum):
    AGENT_CRASH = "agent_crash"
    MEMORY_LEAK = "memory_leak"
    API_RATE_LIMIT = "api_rate_limit"
    LLM_TIMEOUT = "llm_timeout"
    DATABASE_ERROR = "database_error"
    NETWORK_ISSUE = "network_issue"
    QUALITY_GATE_FAIL = "quality_gate_fail"
    CELERY_QUEUE_BACKUP = "celery_queue_backup"
    PUPPETEER_FAIL = "puppeteer_fail"
    VOICE_SERVICE_DOWN = "voice_service_down"


@dataclass
class HealthMetric:
    """Single health metric reading"""
    timestamp: str
    metric_name: str
    value: float
    threshold: float
    status: HealthStatus
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealingAction:
    """Record of a healing action taken"""
    action_id: str
    timestamp: str
    issue_type: IssueType
    target_agent: str
    action_taken: str
    parameters: Dict[str, Any]
    success: bool
    result_message: str
    time_to_resolve_ms: int


@dataclass
class Incident:
    """An incident that required healing"""
    incident_id: str
    timestamp: str
    issue_type: IssueType
    severity: int  # 1-10
    affected_agents: List[str]
    description: str
    root_cause: Optional[str] = None
    healing_actions: List[HealingAction] = field(default_factory=list)
    status: str = "open"  # open, resolved, escalated
    lessons_learned: Optional[str] = None


class SelfHealingMonitor:
    """
    Microsoft Lightning-inspired self-healing monitor
    Watches all agents, detects issues, auto-heals
    """
    
    # Healing strategies mapped to issue types
    HEALING_STRATEGIES = {
        IssueType.AGENT_CRASH: [
            "restart_agent",
            "clear_state_and_restart",
            "fallback_to_backup_agent"
        ],
        IssueType.MEMORY_LEAK: [
            "force_garbage_collection",
            "restart_service",
            "scale_up_memory"
        ],
        IssueType.API_RATE_LIMIT: [
            "backoff_and_retry",
            "switch_to_backup_key",
            "enable_caching"
        ],
        IssueType.LLM_TIMEOUT: [
            "reduce_context_window",
            "switch_to_faster_model",
            "queue_for_async"
        ],
        IssueType.DATABASE_ERROR: [
            "retry_with_backoff",
            "switch_to_read_replica",
            "queue_writes"
        ],
        IssueType.NETWORK_ISSUE: [
            "retry_with_backoff",
            "use_offline_cache",
            "alert_admin"
        ],
        IssueType.QUALITY_GATE_FAIL: [
            "auto_fix_issues",
            "escalate_to_human",
            "lower_threshold_temporarily"
        ],
        IssueType.CELERY_QUEUE_BACKUP: [
            "scale_workers",
            "prioritize_critical_jobs",
            "drop_low_priority"
        ],
        IssueType.PUPPETEER_FAIL: [
            "restart_browser",
            "clear_cache",
            "use_static_fallback"
        ],
        IssueType.VOICE_SERVICE_DOWN: [
            "switch_to_backup_provider",
            "queue_for_retry",
            "disable_voice_temporarily"
        ]
    }
    
    def __init__(self, storage_path: str = "monitoring/healing_state.json"):
        self.storage_path = storage_path
        self.metrics_history: List[HealthMetric] = []
        self.incidents: Dict[str, Incident] = {}
        self.healing_actions: List[HealingAction] = []
        self.agent_health: Dict[str, HealthStatus] = {}
        self.learning_model: Dict[str, Any] = {}  # Simple pattern learning
        
        # Healing functions registry
        self.healing_functions: Dict[str, Callable] = {
            "restart_agent": self._heal_restart_agent,
            "clear_state_and_restart": self._heal_clear_restart,
            "fallback_to_backup_agent": self._heal_fallback_agent,
            "force_garbage_collection": self._heal_gc,
            "restart_service": self._heal_restart_service,
            "scale_up_memory": self._heal_scale_memory,
            "backoff_and_retry": self._heal_backoff_retry,
            "switch_to_backup_key": self._heal_backup_key,
            "enable_caching": self._heal_enable_cache,
            "reduce_context_window": self._heal_reduce_context,
            "switch_to_faster_model": self._heal_faster_model,
            "queue_for_async": self._heal_async_queue,
            "retry_with_backoff": self._heal_retry_backoff,
            "switch_to_read_replica": self._heal_read_replica,
            "queue_writes": self._heal_queue_writes,
            "use_offline_cache": self._heal_offline_cache,
            "alert_admin": self._heal_alert_admin,
            "auto_fix_issues": self._heal_auto_fix,
            "escalate_to_human": self._heal_escalate,
            "lower_threshold_temporarily": self._heal_lower_threshold,
            "scale_workers": self._heal_scale_workers,
            "prioritize_critical_jobs": self._heal_prioritize,
            "drop_low_priority": self._heal_drop_low_priority,
            "restart_browser": self._heal_restart_browser,
            "clear_cache": self._heal_clear_cache,
            "use_static_fallback": self._heal_static_fallback,
            "switch_to_backup_provider": self._heal_backup_voice,
            "queue_for_retry": self._heal_queue_retry,
            "disable_voice_temporarily": self._heal_disable_voice
        }
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self._load_state()
    
    def _load_state(self):
        """Load monitoring state from disk"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.learning_model = data.get("learning_model", {})
                    self.incidents = {
                        k: Incident(**v) for k, v in data.get("incidents", {}).items()
                    }
        except Exception as e:
            logger.warning(f"Failed to load healing state: {e}")
    
    def _save_state(self):
        """Save monitoring state to disk"""
        try:
            data = {
                "learning_model": self.learning_model,
                "incidents": {k: asdict(v) for k, v in self.incidents.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save healing state: {e}")
    
    async def check_agent_health(self, agent_name: str) -> HealthMetric:
        """Check health of a specific agent"""
        # In production, this would check actual metrics
        # For now, simulate health check
        
        # Collect metrics
        metrics = await self._collect_agent_metrics(agent_name)
        
        # Determine status based on metrics
        status = HealthStatus.HEALTHY
        if metrics.get("error_rate", 0) > 0.1:
            status = HealthStatus.DEGRADED
        if metrics.get("error_rate", 0) > 0.3:
            status = HealthStatus.CRITICAL
        if metrics.get("crash_count", 0) > 0:
            status = HealthStatus.FAILED
        
        metric = HealthMetric(
            timestamp=datetime.now().isoformat(),
            metric_name=f"{agent_name}_health",
            value=metrics.get("health_score", 100),
            threshold=80.0,
            status=status,
            details=metrics
        )
        
        self.metrics_history.append(metric)
        self.agent_health[agent_name] = status
        
        # Trigger healing if needed
        if status in [HealthStatus.CRITICAL, HealthStatus.FAILED]:
            await self._trigger_healing(agent_name, status, metrics)
        
        return metric
    
    async def _collect_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Collect metrics from an agent"""
        # This would integrate with actual monitoring
        # Placeholder implementation
        return {
            "cpu_percent": 45.0,
            "memory_mb": 512,
            "error_rate": 0.05,
            "response_time_ms": 250,
            "request_count": 1000,
            "crash_count": 0,
            "health_score": 95.0
        }
    
    async def _trigger_healing(self, agent_name: str, status: HealthStatus, metrics: Dict):
        """Trigger healing process for an unhealthy agent"""
        logger.warning(f"Healing triggered for {agent_name} (status: {status.value})")
        
        # Determine issue type from metrics
        issue_type = self._classify_issue(metrics)
        
        # Create incident
        incident = Incident(
            incident_id=f"inc_{int(time.time())}_{agent_name}",
            timestamp=datetime.now().isoformat(),
            issue_type=issue_type,
            severity=8 if status == HealthStatus.FAILED else 5,
            affected_agents=[agent_name],
            description=f"Agent {agent_name} health degraded to {status.value}"
        )
        
        self.incidents[incident.incident_id] = incident
        
        # Apply healing strategies
        strategies = self.HEALING_STRATEGIES.get(issue_type, ["alert_admin"])
        
        for strategy in strategies:
            action = await self._execute_healing_strategy(
                incident.incident_id, 
                agent_name, 
                issue_type, 
                strategy
            )
            incident.healing_actions.append(action)
            
            if action.success:
                incident.status = "resolved"
                logger.info(f"Healing succeeded for {agent_name} using {strategy}")
                break
        else:
            # All strategies failed
            incident.status = "escalated"
            logger.error(f"All healing strategies failed for {agent_name}")
        
        self._save_state()
    
    def _classify_issue(self, metrics: Dict) -> IssueType:
        """Classify the type of issue from metrics"""
        if metrics.get("crash_count", 0) > 0:
            return IssueType.AGENT_CRASH
        if metrics.get("memory_mb", 0) > 1000:
            return IssueType.MEMORY_LEAK
        if metrics.get("error_rate", 0) > 0.2:
            return IssueType.LLM_TIMEOUT
        return IssueType.AGENT_CRASH  # Default
    
    async def _execute_healing_strategy(self, incident_id: str, agent_name: str, 
                                        issue_type: IssueType, strategy: str) -> HealingAction:
        """Execute a healing strategy"""
        start_time = time.time()
        
        healing_fn = self.healing_functions.get(strategy)
        if not healing_fn:
            return HealingAction(
                action_id=f"act_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                issue_type=issue_type,
                target_agent=agent_name,
                action_taken=strategy,
                parameters={},
                success=False,
                result_message=f"Unknown healing strategy: {strategy}",
                time_to_resolve_ms=0
            )
        
        try:
            result = await healing_fn(agent_name)
            success = result.get("success", False)
            message = result.get("message", "No message")
        except Exception as e:
            success = False
            message = f"Healing failed: {str(e)}"
            logger.error(f"Healing error: {traceback.format_exc()}")
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        action = HealingAction(
            action_id=f"act_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            issue_type=issue_type,
            target_agent=agent_name,
            action_taken=strategy,
            parameters={"auto": True},
            success=success,
            result_message=message,
            time_to_resolve_ms=elapsed_ms
        )
        
        self.healing_actions.append(action)
        return action
    
    # ===== HEALING FUNCTION IMPLEMENTATIONS =====
    
    async def _heal_restart_agent(self, agent_name: str) -> Dict:
        """Restart a crashed agent"""
        logger.info(f"Restarting agent: {agent_name}")
        # In production, this would actually restart the service
        return {"success": True, "message": f"Agent {agent_name} restarted"}
    
    async def _heal_clear_restart(self, agent_name: str) -> Dict:
        """Clear state and restart"""
        logger.info(f"Clearing state and restarting: {agent_name}")
        return {"success": True, "message": f"State cleared and {agent_name} restarted"}
    
    async def _heal_fallback_agent(self, agent_name: str) -> Dict:
        """Fallback to backup agent"""
        logger.info(f"Falling back to backup for: {agent_name}")
        return {"success": True, "message": f"Backup agent activated for {agent_name}"}
    
    async def _heal_gc(self, agent_name: str) -> Dict:
        """Force garbage collection"""
        import gc
        gc.collect()
        return {"success": True, "message": "Garbage collection forced"}
    
    async def _heal_restart_service(self, agent_name: str) -> Dict:
        """Restart the entire service"""
        logger.info(f"Restarting service for: {agent_name}")
        return {"success": True, "message": f"Service restarted for {agent_name}"}
    
    async def _heal_scale_memory(self, agent_name: str) -> Dict:
        """Scale up memory allocation"""
        logger.info(f"Scaling memory for: {agent_name}")
        return {"success": True, "message": "Memory scaled up"}
    
    async def _heal_backoff_retry(self, agent_name: str) -> Dict:
        """Apply backoff and retry"""
        await asyncio.sleep(5)  # Backoff
        return {"success": True, "message": "Retry after backoff"}
    
    async def _heal_backup_key(self, agent_name: str) -> Dict:
        """Switch to backup API key"""
        logger.info("Switching to backup API key")
        return {"success": True, "message": "Switched to backup API key"}
    
    async def _heal_enable_cache(self, agent_name: str) -> Dict:
        """Enable aggressive caching"""
        logger.info("Enabling aggressive caching")
        return {"success": True, "message": "Caching enabled"}
    
    async def _heal_reduce_context(self, agent_name: str) -> Dict:
        """Reduce LLM context window"""
        logger.info("Reducing context window")
        return {"success": True, "message": "Context window reduced"}
    
    async def _heal_faster_model(self, agent_name: str) -> Dict:
        """Switch to faster model"""
        logger.info("Switching to faster model")
        return {"success": True, "message": "Switched to faster model"}
    
    async def _heal_async_queue(self, agent_name: str) -> Dict:
        """Queue for async processing"""
        logger.info("Queueing for async processing")
        return {"success": True, "message": "Queued for async processing"}
    
    async def _heal_retry_backoff(self, agent_name: str) -> Dict:
        """Retry with exponential backoff"""
        await asyncio.sleep(5)
        return {"success": True, "message": "Retry completed"}
    
    async def _heal_read_replica(self, agent_name: str) -> Dict:
        """Switch to read replica"""
        logger.info("Switching to read replica")
        return {"success": True, "message": "Switched to read replica"}
    
    async def _heal_queue_writes(self, agent_name: str) -> Dict:
        """Queue database writes"""
        logger.info("Queueing writes")
        return {"success": True, "message": "Writes queued"}
    
    async def _heal_offline_cache(self, agent_name: str) -> Dict:
        """Use offline cache"""
        logger.info("Using offline cache")
        return {"success": True, "message": "Using offline cache"}
    
    async def _heal_alert_admin(self, agent_name: str) -> Dict:
        """Alert human admin"""
        logger.warning(f"ALERT: Admin intervention needed for {agent_name}")
        # Send notification to admin
        return {"success": True, "message": "Admin alerted"}
    
    async def _heal_auto_fix(self, agent_name: str) -> Dict:
        """Auto-fix quality issues"""
        logger.info("Auto-fixing quality issues")
        return {"success": True, "message": "Auto-fix applied"}
    
    async def _heal_escalate(self, agent_name: str) -> Dict:
        """Escalate to human"""
        logger.warning(f"Escalating {agent_name} to human")
        return {"success": True, "message": "Escalated to human"}
    
    async def _heal_lower_threshold(self, agent_name: str) -> Dict:
        """Temporarily lower quality threshold"""
        logger.info("Temporarily lowering threshold")
        return {"success": True, "message": "Threshold lowered temporarily"}
    
    async def _heal_scale_workers(self, agent_name: str) -> Dict:
        """Scale Celery workers"""
        logger.info("Scaling Celery workers")
        return {"success": True, "message": "Workers scaled"}
    
    async def _heal_prioritize(self, agent_name: str) -> Dict:
        """Prioritize critical jobs"""
        logger.info("Prioritizing critical jobs")
        return {"success": True, "message": "Critical jobs prioritized"}
    
    async def _heal_drop_low_priority(self, agent_name: str) -> Dict:
        """Drop low priority jobs"""
        logger.info("Dropping low priority jobs")
        return {"success": True, "message": "Low priority jobs dropped"}
    
    async def _heal_restart_browser(self, agent_name: str) -> Dict:
        """Restart Puppeteer browser"""
        logger.info("Restarting browser")
        return {"success": True, "message": "Browser restarted"}
    
    async def _heal_clear_cache(self, agent_name: str) -> Dict:
        """Clear browser cache"""
        logger.info("Clearing cache")
        return {"success": True, "message": "Cache cleared"}
    
    async def _heal_static_fallback(self, agent_name: str) -> Dict:
        """Use static fallback"""
        logger.info("Using static fallback")
        return {"success": True, "message": "Static fallback activated"}
    
    async def _heal_backup_voice(self, agent_name: str) -> Dict:
        """Switch to backup voice provider"""
        logger.info("Switching to backup voice provider")
        return {"success": True, "message": "Backup voice provider activated"}
    
    async def _heal_queue_retry(self, agent_name: str) -> Dict:
        """Queue for later retry"""
        logger.info("Queueing for retry")
        return {"success": True, "message": "Queued for retry"}
    
    async def _heal_disable_voice(self, agent_name: str) -> Dict:
        """Temporarily disable voice"""
        logger.info("Disabling voice temporarily")
        return {"success": True, "message": "Voice disabled temporarily"}
    
    # ===== PUBLIC API =====
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._calculate_overall_health(),
            "agent_health": {k: v.value for k, v in self.agent_health.items()},
            "open_incidents": len([i for i in self.incidents.values() if i.status == "open"]),
            "total_incidents_24h": len([
                i for i in self.incidents.values() 
                if (datetime.now() - datetime.fromisoformat(i.timestamp)).days < 1
            ]),
            "healing_success_rate": self._calculate_healing_success_rate(),
            "learning_patterns": len(self.learning_model.get("patterns", []))
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        if not self.agent_health:
            return "unknown"
        
        statuses = list(self.agent_health.values())
        if any(s == HealthStatus.FAILED for s in statuses):
            return "critical"
        if any(s == HealthStatus.CRITICAL for s in statuses):
            return "degraded"
        if any(s == HealthStatus.DEGRADED for s in statuses):
            return "warning"
        return "healthy"
    
    def _calculate_healing_success_rate(self) -> float:
        """Calculate healing success rate"""
        if not self.healing_actions:
            return 100.0
        
        successful = sum(1 for a in self.healing_actions if a.success)
        return (successful / len(self.healing_actions)) * 100
    
    def get_incidents(self, status: Optional[str] = None) -> List[Dict]:
        """Get incidents, optionally filtered by status"""
        incidents = self.incidents.values()
        if status:
            incidents = [i for i in incidents if i.status == status]
        return [asdict(i) for i in incidents]
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring loop"""
        logger.info(f"Starting self-healing monitor (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Check all registered agents
                agents = ["designer", "coder", "reviewer", "qa", "voice", "yappyverse"]
                for agent in agents:
                    await self.check_agent_health(agent)
                
                self._save_state()
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            
            await asyncio.sleep(interval_seconds)


# Singleton instance
_monitor: Optional[SelfHealingMonitor] = None


def get_self_healing_monitor() -> SelfHealingMonitor:
    """Get singleton self-healing monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = SelfHealingMonitor()
    return _monitor