"""
Integration tests for the complete mutant generation pipeline
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestIntegration:
    """Integration tests for the complete system"""    
    
    def test_parallel_worker_integration(self, temp_dir):
        """Test that parallel worker setup works correctly"""
        from parallel.worker_pool import WorkerPool
        
        worker_pool = WorkerPool(max_workers=2)
        
        # This is a basic test to ensure the worker pool can be instantiated
        # Actual parallel execution testing would require more complex setup
        assert worker_pool.max_workers == 2
        
    def test_configuration_loading(self):
        """Test that configuration is loaded correctly"""
        from config.settings import BASE_CHECKOUT_DIR, MAX_WORKERS, DEFECTS4J_EXECUTABLE
        
        # Basic validation that configuration values exist
        assert BASE_CHECKOUT_DIR is not None
        assert isinstance(MAX_WORKERS, int)
        assert MAX_WORKERS > 0
        assert DEFECTS4J_EXECUTABLE is not None