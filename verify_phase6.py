import sys
import asyncio
from pathlib import Path

root = Path(__file__).parent
sys.path.append(str(root))

async def run_checks():
    print("🚀 AgentOS Phase 6 System Health Check\n")
    
    # Check 1: Workforce Manager
    try:
        from AgentOS.kernel.skills import workforce_manager
        methods = ["delegate_task", "report_task_completion", "get_workforce_capacity"]
        for m in methods:
            if hasattr(workforce_manager, m):
                print(f"  ✓ Workforce Manager: {m} implemented.")
            else:
                print(f"  ✗ Workforce Manager: {m} MISSING!")
    except Exception as e:
        print(f"  ✗ Workforce Manager Check Failed: {e}")

    # Check 2: GitHub Skill
    try:
        from AgentOS.kernel.skills import github_skill
        if hasattr(github_skill, "github_skill"):
            print("  ✓ GitHub Skill: Module implemented.")
        else:
            print("  ✗ GitHub Skill: Module MISSING!")
    except Exception as e:
        print(f"  ✗ GitHub Skill Check Failed: {e}")

    # Check 3: Ecosystem Registration
    try:
        from AgentOS.kernel.registry import registry
        if "github_sync" in registry.list_commands():
            print("  ✓ Ecosystem: github_sync registered.")
        else:
            print("  ✗ Ecosystem: github_sync NOT found in registry!")
    except Exception as e:
        print(f"  ✗ Ecosystem Check Failed: {e}")

    # Check 4: Mobile Bridge
    try:
        from AgentOS.kernel.skills import mobile_bridge
        if hasattr(mobile_bridge, "mobile_bridge"):
            print("  ✓ Mobile Bridge: Module implemented.")
        else:
            print("  ✗ Mobile Bridge: Module MISSING!")
    except Exception as e:
        print(f"  ✗ Mobile Bridge Check Failed: {e}")

    # Check 5: Financial Service
    try:
        from AgentOS.kernel.skills import financial_service
        if hasattr(financial_service, "financial_service"):
            print("  ✓ Financial Service: Module implemented.")
        else:
            print("  ✗ Financial Service: Module MISSING!")
    except Exception as e:
        print(f"  ✗ Financial Service Check Failed: {e}")

    # Check 6: Global Registry Commands
    try:
        from AgentOS.kernel.registry import registry
        cmds = ["github_sync", "mobile_sync", "financial_op"]
        registered = registry.list_commands()
        for c in cmds:
            if c in registered:
                print(f"  ✓ Registry: {c} registered.")
            else:
                print(f"  ✗ Registry: {c} NOT found!")
    except Exception as e:
        print(f"  ✗ Registry Check Failed: {e}")

    print("\n✓ Health Check Complete.")


if __name__ == "__main__":
    asyncio.run(run_checks())
