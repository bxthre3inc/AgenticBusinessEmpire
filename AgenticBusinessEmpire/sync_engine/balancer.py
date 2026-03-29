"""
balancer.py — AgenticBusinessEmpire Pressure-Aware Mesh Balancer
Calculates health scores for hardware-optimized task routing across the mesh.
(FOXXD S67 / Kali Chromebook / Zo.computer Optimized)
"""

import logging
from AgenticBusinessEmpire.kernel import resource_monitor
from AgenticBusinessEmpire.core import config

logger = logging.getLogger("agenticbusinessempire.balancer")

class MeshBalancer:
    @staticmethod
    def calculate_pressure_score() -> float:
        """
        Returns a score from 0 (Perfect) to 100 (Saturated).
        Takes into account CPU, RAM, and Battery (for mobile nodes).
        """
        report = resource_monitor.get_pressure_report()
        
        cpu_weight = 0.4
        ram_weight = 0.4
        
        # Base score from CPU and RAM
        # On FOXXD S67 / Chromebook, high RAM usage is a critical kill-switch
        score = (report["cpu_p"] * cpu_weight) + (report["ram_p"] * ram_weight)
        
        # Battery awareness for FOXXD S67 / Chromebook
        is_server = config.IS_SERVER
        if not is_server:
            battery_p = report.get("battery_p", 100)
            is_charging = report.get("is_charging", True)
            
            # Penalize low battery heavily if not charging
            if not is_charging:
                if battery_p < 20:
                    score += 50  # Overload
                elif battery_p < 50:
                    score += 20
            else:
                # Slight bonus for being plugged in
                score -= 5
        
        # Server bias: Prefer Zo.computer for high-reliability tasks
        if is_server:
            score -= 15

        return max(0.0, min(100.0, float(score)))

    @staticmethod
    def should_offload(threshold: float = 70.0) -> bool:
        """
        Decision engine for inference_node.
        Returns True if the current node is too pressurized for local inference.
        """
        if config.IS_SERVER:
            return False # Servers rarely offload unless at 95%+
            
        score = MeshBalancer.calculate_pressure_score()
        
        # Automatic offload if free RAM is critically low (Chromebook Check)
        report = resource_monitor.get_pressure_report()
        if report["ram_p"] > 85: # Only 15% RAM left (Critical for 4GB nodes)
            logger.warning("[Balancer] RAM Critical (%.1f%% used). Forcing offload.", report["ram_p"])
            return True

        return score > threshold

balancer = MeshBalancer()
