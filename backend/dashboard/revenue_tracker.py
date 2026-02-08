"""
💰 REVENUE TRACKING DASHBOARD 💰

Monetization metrics and financial analytics for The Pauli Effect
Part of the Aggressive Full Superagent Architecture
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RevenueSource(Enum):
    """Sources of revenue"""
    CLIENT_PROJECT = "client_project"
    SUBSCRIPTION = "subscription"
    TEMPLATE_SALE = "template_sale"
    CONSULTING = "consulting"
    YAPPYVERSE_MERCH = "yappyverse_merch"
    YOUTUBE_ADS = "youtube_ads"
    AFFILIATE = "affiliate"
    MAINTENANCE = "maintenance"


class ProjectStatus(Enum):
    """Project payment status"""
    PROPOSAL = "proposal"
    CONTRACT_SIGNED = "contract_signed"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    PAID = "paid"
    OVERDUE = "overdue"


@dataclass
class RevenueEntry:
    """Single revenue transaction"""
    entry_id: str
    timestamp: str
    source: RevenueSource
    amount_usd: float
    description: str
    client_name: Optional[str] = None
    project_id: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PAID
    expenses: float = 0.0
    notes: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Client:
    """Client information"""
    client_id: str
    name: str
    email: str
    company: Optional[str] = None
    total_revenue: float = 0.0
    project_count: int = 0
    status: str = "active"  # active, inactive, vip
    first_project: Optional[str] = None
    last_project: Optional[str] = None
    notes: str = ""


class RevenueTracker:
    """
    Comprehensive revenue tracking and financial analytics
    Tracks all monetization streams for The Pauli Effect
    """
    
    def __init__(self, storage_path: str = "dashboard/revenue_data.json"):
        self.storage_path = storage_path
        self.entries: Dict[str, RevenueEntry] = {}
        self.clients: Dict[str, Client] = {}
        self.monthly_targets = {
            "revenue_target": 50000.0,  # $50k/month target
            "project_target": 10,
            "client_target": 5
        }
        
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load revenue data from storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load entries
                    for entry_data in data.get("entries", []):
                        entry = RevenueEntry(
                            entry_id=entry_data["entry_id"],
                            timestamp=entry_data["timestamp"],
                            source=RevenueSource(entry_data["source"]),
                            amount_usd=entry_data["amount_usd"],
                            description=entry_data["description"],
                            client_name=entry_data.get("client_name"),
                            project_id=entry_data.get("project_id"),
                            status=ProjectStatus(entry_data.get("status", "paid")),
                            expenses=entry_data.get("expenses", 0.0),
                            notes=entry_data.get("notes", ""),
                            tags=entry_data.get("tags", [])
                        )
                        self.entries[entry.entry_id] = entry
                    
                    # Load clients
                    for client_data in data.get("clients", []):
                        client = Client(**client_data)
                        self.clients[client.client_id] = client
                    
                    self.monthly_targets = data.get("monthly_targets", self.monthly_targets)
                    
        except Exception as e:
            logger.warning(f"Failed to load revenue data: {e}")
    
    def _save_data(self):
        """Save revenue data to storage"""
        try:
            data = {
                "entries": [asdict(e) for e in self.entries.values()],
                "clients": [asdict(c) for c in self.clients.values()],
                "monthly_targets": self.monthly_targets,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save revenue data: {e}")
    
    def add_revenue(self, 
                   source: RevenueSource,
                   amount_usd: float,
                   description: str,
                   client_name: Optional[str] = None,
                   project_id: Optional[str] = None,
                   status: ProjectStatus = ProjectStatus.PAID,
                   expenses: float = 0.0,
                   tags: List[str] = None) -> RevenueEntry:
        """Add a new revenue entry"""
        
        entry = RevenueEntry(
            entry_id=f"rev_{int(datetime.now().timestamp())}",
            timestamp=datetime.now().isoformat(),
            source=source,
            amount_usd=amount_usd,
            description=description,
            client_name=client_name,
            project_id=project_id,
            status=status,
            expenses=expenses,
            tags=tags or []
        )
        
        self.entries[entry.entry_id] = entry
        
        # Update client stats if client specified
        if client_name:
            self._update_client_revenue(client_name, amount_usd)
        
        self._save_data()
        logger.info(f"Revenue added: ${amount_usd} from {source.value}")
        
        return entry
    
    def _update_client_revenue(self, client_name: str, amount: float):
        """Update client revenue statistics"""
        # Find or create client
        client = None
        for c in self.clients.values():
            if c.name == client_name:
                client = c
                break
        
        if not client:
            client_id = f"client_{int(datetime.now().timestamp())}"
            client = Client(
                client_id=client_id,
                name=client_name,
                email="",
                total_revenue=0.0,
                project_count=0,
                first_project=datetime.now().isoformat()
            )
            self.clients[client_id] = client
        
        client.total_revenue += amount
        client.project_count += 1
        client.last_project = datetime.now().isoformat()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        
        # Calculate metrics
        now = datetime.now()
        this_month = now.month
        this_year = now.year
        
        # Monthly revenue
        monthly_entries = [
            e for e in self.entries.values()
            if datetime.fromisoformat(e.timestamp).month == this_month
            and datetime.fromisoformat(e.timestamp).year == this_year
        ]
        monthly_revenue = sum(e.amount_usd for e in monthly_entries)
        monthly_expenses = sum(e.expenses for e in monthly_entries)
        monthly_profit = monthly_revenue - monthly_expenses
        
        # Yearly revenue
        yearly_entries = [
            e for e in self.entries.values()
            if datetime.fromisoformat(e.timestamp).year == this_year
        ]
        yearly_revenue = sum(e.amount_usd for e in yearly_entries)
        
        # Revenue by source
        revenue_by_source = {}
        for source in RevenueSource:
            source_revenue = sum(
                e.amount_usd for e in self.entries.values()
                if e.source == source
            )
            revenue_by_source[source.value] = source_revenue
        
        # Project status breakdown
        status_counts = {}
        for status in ProjectStatus:
            count = sum(
                1 for e in self.entries.values()
                if e.status == status
            )
            status_counts[status.value] = count
        
        # Top clients
        top_clients = sorted(
            self.clients.values(),
            key=lambda c: c.total_revenue,
            reverse=True
        )[:10]
        
        # Targets progress
        target_progress = {
            "revenue": {
                "current": monthly_revenue,
                "target": self.monthly_targets["revenue_target"],
                "percentage": (monthly_revenue / self.monthly_targets["revenue_target"]) * 100
            },
            "projects": {
                "current": len([e for e in monthly_entries if e.source == RevenueSource.CLIENT_PROJECT]),
                "target": self.monthly_targets["project_target"],
                "percentage": (len([e for e in monthly_entries if e.source == RevenueSource.CLIENT_PROJECT]) / self.monthly_targets["project_target"]) * 100
            }
        }
        
        return {
            "monthly": {
                "revenue": monthly_revenue,
                "expenses": monthly_expenses,
                "profit": monthly_profit,
                "margin_percent": (monthly_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
            },
            "yearly": {
                "revenue": yearly_revenue
            },
            "revenue_by_source": revenue_by_source,
            "project_status": status_counts,
            "top_clients": [
                {
                    "name": c.name,
                    "total_revenue": c.total_revenue,
                    "project_count": c.project_count,
                    "status": c.status
                }
                for c in top_clients
            ],
            "targets": target_progress,
            "total_entries": len(self.entries),
            "total_clients": len(self.clients)
        }
    
    def get_revenue_by_period(self, 
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get revenue for a specific time period"""
        
        entries = list(self.entries.values())
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) <= end]
        
        total_revenue = sum(e.amount_usd for e in entries)
        total_expenses = sum(e.expenses for e in entries)
        
        return {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "profit": total_revenue - total_expenses,
            "entry_count": len(entries),
            "entries": [asdict(e) for e in entries]
        }
    
    def get_client_report(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get report for a specific client or all clients"""
        
        if client_id:
            client = self.clients.get(client_id)
            if not client:
                return {"error": "Client not found"}
            
            client_entries = [
                e for e in self.entries.values()
                if e.client_name == client.name
            ]
            
            return {
                "client": asdict(client),
                "entries": [asdict(e) for e in client_entries],
                "total_revenue": sum(e.amount_usd for e in client_entries),
                "total_projects": len(client_entries)
            }
        
        # All clients report
        return {
            "clients": [asdict(c) for c in self.clients.values()],
            "total_clients": len(self.clients),
            "total_revenue": sum(c.total_revenue for c in self.clients.values()),
            "average_revenue_per_client": (
                sum(c.total_revenue for c in self.clients.values()) / len(self.clients)
                if self.clients else 0
            )
        }
    
    def set_targets(self, 
                   revenue_target: Optional[float] = None,
                   project_target: Optional[int] = None,
                   client_target: Optional[int] = None):
        """Set monthly targets"""
        if revenue_target:
            self.monthly_targets["revenue_target"] = revenue_target
        if project_target:
            self.monthly_targets["project_target"] = project_target
        if client_target:
            self.monthly_targets["client_target"] = client_target
        
        self._save_data()
    
    def get_yappyverse_metrics(self) -> Dict[str, Any]:
        """Get Yappyverse-specific monetization metrics"""
        
        yappyverse_entries = [
            e for e in self.entries.values()
            if e.source in [RevenueSource.YAPPYVERSE_MERCH, RevenueSource.YOUTUBE_ADS]
        ]
        
        return {
            "total_revenue": sum(e.amount_usd for e in yappyverse_entries),
            "merch_revenue": sum(
                e.amount_usd for e in yappyverse_entries
                if e.source == RevenueSource.YAPPYVERSE_MERCH
            ),
            "youtube_revenue": sum(
                e.amount_usd for e in yappyverse_entries
                if e.source == RevenueSource.YOUTUBE_ADS
            ),
            "entry_count": len(yappyverse_entries)
        }


# Singleton instance
_tracker: Optional[RevenueTracker] = None


def get_revenue_tracker() -> RevenueTracker:
    """Get singleton revenue tracker"""
    global _tracker
    if _tracker is None:
        _tracker = RevenueTracker()
    return _tracker