# -*- coding: utf-8 -*-
"""
Refactoring Integration Service

Integrates ProgressiveRefactoringService with routes using MetricsFacade.
Provides seamless migration from legacy GLPIService to Clean Architecture.
"""

import logging
from typing import Any, Dict

from ...application.services.progressive_refactoring_service import (
    create_progressive_refactoring_service,
    RefactoringPhase
)
from ...infrastructure.external.glpi.metrics_adapter import GLPIConfig
from config.settings import active_config
from ..contracts.metrics_contracts import UnifiedGLPIServiceContract
from .metrics_facade import MetricsFacade


class RefactoringIntegrationService:
    """
    Service that integrates progressive refactoring with the facade pattern.
    
    This service acts as the main entry point for routes, deciding whether
    to use legacy services or the new architecture based on refactoring phase.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        config = active_config()
        
        # Create GLPI configuration
        self.glpi_config = GLPIConfig(
            base_url=config.GLPI_URL,
            app_token=config.GLPI_APP_TOKEN,
            user_token=config.GLPI_USER_TOKEN,
            timeout=getattr(config, 'API_TIMEOUT', 30)
        )
        
        # Create new architecture facade
        self.new_service = MetricsFacade()
        
        # Create progressive refactoring service in VALIDATION phase
        # This means we'll run both old and new implementations and compare
        self.refactoring_service = create_progressive_refactoring_service(
            phase=RefactoringPhase.VALIDATION,
            glpi_config=self.glpi_config,
            legacy_service=None,  # Will be injected when needed
            validation_sampling=1.0,  # Validate all requests initially (100%)
        )
        
        self.logger.info("RefactoringIntegrationService initialized in VALIDATION phase")
    
    def get_service(self) -> UnifiedGLPIServiceContract:
        """
        Returns the appropriate service implementation.
        
        During VALIDATION phase, returns the new service directly since
        we want to start testing the new architecture.
        """
        return self.new_service
    
    def get_refactoring_metrics(self) -> Dict[str, Any]:
        """Get metrics about the refactoring process."""
        return {
            "phase": self.refactoring_service.config.phase.value,
            "performance_metrics": self.refactoring_service.performance_metrics,
            "validation_enabled": self.refactoring_service.config.validation_enabled,
            "migration_percentage": getattr(self.refactoring_service.config, 'migration_percentage', 0),
        }
    
    def switch_to_strangler_fig_phase(self, migration_percentage: int = 50):
        """Switch to Strangler Fig phase with gradual migration."""
        self.logger.info(f"Switching to STRANGLER_FIG phase with {migration_percentage}% migration")
        
        self.refactoring_service = create_progressive_refactoring_service(
            phase=RefactoringPhase.STRANGLER_FIG,
            glpi_config=self.glpi_config,
            legacy_service=None,  # Legacy service to be provided later
            migration_percentage=migration_percentage,
        )
    
    def complete_migration(self):
        """Complete migration to new architecture."""
        self.logger.info("Completing migration - switching to NEW_ONLY phase")
        
        self.refactoring_service = create_progressive_refactoring_service(
            phase=RefactoringPhase.NEW_ONLY,
            glpi_config=self.glpi_config,
        )


# Lazy initialization to avoid import-time side effects
_refactoring_integration_service = None

def get_refactoring_integration_service() -> RefactoringIntegrationService:
    """Get singleton instance of RefactoringIntegrationService."""
    global _refactoring_integration_service
    if _refactoring_integration_service is None:
        _refactoring_integration_service = RefactoringIntegrationService()
    return _refactoring_integration_service