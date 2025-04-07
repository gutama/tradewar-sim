"""External events generation for trade war simulation."""

import logging
import random
from typing import Dict, List, Optional, Set

import numpy as np

from tradewar.economics.models import Country, EventConfig
from tradewar.simulation.state import SimulationState

logger = logging.getLogger(__name__)


class EventGenerator:
    """
    Generator for external events that impact the trade war simulation.
    
    This class manages random and scheduled events like economic crises,
    natural disasters, political changes, and other exogenous shocks
    that can affect trade relations and economic indicators.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the event generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        self.random = random.Random(seed)
        self.predefined_events = self._create_predefined_events()
        self.triggered_events: Set[str] = set()
    
    def generate_events(
        self, state: SimulationState, year: int, quarter: int
    ) -> List[EventConfig]:
        """
        Generate external events for the current simulation period.
        
        Args:
            state: Current simulation state
            year: Current simulation year
            quarter: Current simulation quarter
            
        Returns:
            List of event configurations
        """
        events = []
        
        # Check for scheduled events
        scheduled = self._check_scheduled_events(year, quarter)
        events.extend(scheduled)
        
        # Generate random events
        randoms = self._generate_random_events(state, year, quarter)
        events.extend(randoms)
        
        # Log generated events
        if events:
            event_names = [e.name for e in events]
            logger.info(f"Generated events for Y{year}Q{quarter}: {event_names}")
        
        return events
    
    def _check_scheduled_events(self, year: int, quarter: int) -> List[EventConfig]:
        """Check for scheduled events based on the timeline."""
        events = []
        
        # Convert year and quarter to a single timeline position
        timeline_pos = year * 4 + quarter
        
        # Check each predefined event
        for event in self.predefined_events:
            # Skip already triggered one-time events
            if event.name in self.triggered_events:
                continue
            
            # Check if this event should trigger on this exact time
            if hasattr(event, "trigger_time") and event.trigger_time == timeline_pos:
                events.append(event)
                
                # Mark as triggered to avoid repeats
                self.triggered_events.add(event.name)
        
        return events
    
    def _generate_random_events(
        self, state: SimulationState, year: int, quarter: int
    ) -> List[EventConfig]:
        """Generate random events based on probabilities."""
        events = []
        
        # Sample from predefined events with their probabilities
        for event in self.predefined_events:
            # Skip events that are specifically scheduled
            if hasattr(event, "trigger_time"):
                continue
            
            # Skip already triggered one-time events
            if event.name in self.triggered_events and hasattr(event, "one_time") and event.one_time:
                continue
            
            # Roll the dice to see if this event occurs
            if self.random.random() < event.probability:
                events.append(event)
                
                # If it's a one-time event, mark as triggered
                if hasattr(event, "one_time") and event.one_time:
                    self.triggered_events.add(event.name)
        
        return events
    
    def _create_predefined_events(self) -> List[EventConfig]:
        """Create the set of predefined events for the simulation."""
        events = []
        
        # Global financial crisis
        events.append(
            EventConfig(
                name="Global Financial Crisis",
                probability=0.01,  # 1% chance per quarter
                affected_countries={"US", "China", "Indonesia"},
                affected_sectors={"banking", "services", "manufacturing"},
                gdp_impact={
                    "US": -0.02,       # -2% GDP growth
                    "China": -0.015,   # -1.5% GDP growth
                    "Indonesia": -0.025, # -2.5% GDP growth
                },
                duration_quarters=4,
                description="Major global financial crisis impacting all economies"
            )
        )
        
        # US recession
        events.append(
            EventConfig(
                name="US Economic Recession",
                probability=0.03,  # 3% chance per quarter
                affected_countries={"US", "China", "Indonesia"},
                affected_sectors={"services", "manufacturing", "technology"},
                gdp_impact={
                    "US": -0.015,     # -1.5% GDP growth
                    "China": -0.01,   # -1% GDP growth 
                    "Indonesia": -0.005, # -0.5% GDP growth
                },
                duration_quarters=3,
                description="Economic recession in the United States"
            )
        )
        
        # US presidential election
        election_event = EventConfig(
            name="US Presidential Election",
            probability=0.0,  # Scheduled event
            affected_countries={"US", "China", "Indonesia"},
            affected_sectors={"all"},
            gdp_impact={
                "US": 0.0,       # Neutral immediate effect
                "China": 0.0,    # Neutral immediate effect
                "Indonesia": 0.0,  # Neutral immediate effect
            },
            duration_quarters=1,
            description="US Presidential election causing policy uncertainty"
        )
        # Add a specific trigger time (year 2, quarter 3)
        setattr(election_event, "trigger_time", 2 * 4 + 3)
        setattr(election_event, "one_time", True)
        events.append(election_event)
        
        # China credit crunch
        events.append(
            EventConfig(
                name="China Credit Crunch",
                probability=0.02,  # 2% chance per quarter
                affected_countries={"China", "US", "Indonesia"},
                affected_sectors={"real_estate", "manufacturing", "banking"},
                gdp_impact={
                    "China": -0.02,   # -2% GDP growth
                    "US": -0.005,     # -0.5% GDP growth
                    "Indonesia": -0.01, # -1% GDP growth
                },
                duration_quarters=2,
                description="Tightening credit conditions in China's economy"
            )
        )
        
        # Supply chain disruption
        events.append(
            EventConfig(
                name="Global Supply Chain Disruption",
                probability=0.025,  # 2.5% chance per quarter
                affected_countries={"US", "China", "Indonesia"},
                affected_sectors={"manufacturing", "technology", "raw_materials"},
                gdp_impact={
                    "US": -0.01,       # -1% GDP growth
                    "China": -0.015,   # -1.5% GDP growth
                    "Indonesia": -0.01,  # -1% GDP growth
                },
                duration_quarters=2,
                description="Major disruption to global supply chains"
            )
        )
        
        # Indonesian natural disaster
        events.append(
            EventConfig(
                name="Natural Disaster in Indonesia",
                probability=0.03,  # 3% chance per quarter
                affected_countries={"Indonesia"},
                affected_sectors={"agriculture", "manufacturing", "tourism"},
                gdp_impact={
                    "Indonesia": -0.02,  # -2% GDP growth
                },
                duration_quarters=2,
                description="Major natural disaster affecting Indonesia's economy"
            )
        )
        
        # Oil price shock
        events.append(
            EventConfig(
                name="Global Oil Price Shock",
                probability=0.02,  # 2% chance per quarter
                affected_countries={"US", "China", "Indonesia"},
                affected_sectors={"energy", "transportation", "manufacturing"},
                gdp_impact={
                    "US": -0.007,      # -0.7% GDP growth
                    "China": -0.01,    # -1% GDP growth
                    "Indonesia": 0.01,  # +1% GDP growth (oil exporter benefit)
                },
                duration_quarters=3,
                description="Sudden change in global oil prices"
            )
        )
        
        # Technology breakthrough
        events.append(
            EventConfig(
                name="Major Technology Breakthrough",
                probability=0.01,  # 1% chance per quarter
                affected_countries={"US", "China"},
                affected_sectors={"technology", "manufacturing"},
                gdp_impact={
                    "US": 0.01,      # +1% GDP growth
                    "China": 0.007,  # +0.7% GDP growth
                },
                duration_quarters=6,
                description="Breakthrough in technology providing economic advantages"
            )
        )
        
        # Pandemic
        pandemic_event = EventConfig(
            name="Global Pandemic",
            probability=0.005,  # 0.5% chance per quarter
            affected_countries={"US", "China", "Indonesia"},
            affected_sectors={"all"},
            gdp_impact={
                "US": -0.03,      # -3% GDP growth
                "China": -0.025,  # -2.5% GDP growth
                "Indonesia": -0.035, # -3.5% GDP growth
            },
            duration_quarters=5,
            description="Global health crisis severely impacting all economies"
        )
        setattr(pandemic_event, "one_time", True)
        events.append(pandemic_event)
        
        return events
