import logging
import time
import psutil
import threading
from typing import Dict

logger = logging.getLogger(__name__)


class RAMMonitor:
    """Simplified RAM monitoring."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.ram_samples = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start RAM monitoring."""
        self.monitoring = True
        self.ram_samples = []
        self.monitor_thread = threading.Thread(target=self._monitor_ram)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop RAM monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_ram(self):
        """Monitor RAM usage."""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                ram_mb = memory_info.rss / (1024 * 1024)
                self.ram_samples.append(ram_mb)
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"RAM monitoring error: {e}")
                break
    
    def get_ram_stats(self) -> Dict[str, float]:
        """Get RAM statistics."""
        if not self.ram_samples:
            return {"average": 0, "max": 0, "current": 0}
        
        current_memory = self.process.memory_info().rss / (1024 * 1024)
        return {
            "average": sum(self.ram_samples) / len(self.ram_samples),
            "max": max(self.ram_samples),
            "current": current_memory
        }