import json
import random
import os
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path("opendigger_data")

def generate_mock_data():
    """
    Generate extensive mock data for demo purposes.
    Simulates:
    - 50+ repositories
    - 3 years of monthly data
    - Metrics: OpenRank, Activity, Stars, Issues, PRs
    """
    print("Generating mock data...")
    
    # Define some categories/owners
    owners = [
        "cloud-native", "ai-labs", "web-frameworks", "database-systems", 
        "blockchain-core", "iot-edge", "mobile-tooling", "devops-platform"
    ]
    
    base_date = datetime(2023, 1, 1)
    months = []
    for i in range(36):
        d = base_date + timedelta(days=30*i)
        months.append(d.strftime("%Y-%m"))
        
    for owner in owners:
        # Create 10-25 repos per owner for density
        num_repos = random.randint(10, 25)
        for i in range(num_repos):
            repo_name = f"{owner}-project-{i}"
            repo_dir = DATA_DIR / "mock" / owner / repo_name
            repo_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Activity (Monthly)
            # Create distinct patterns for Lifecycle Matrix
            pattern = random.choice(['growth', 'stable', 'decline', 'volatile'])
            activity = {}
            val = random.randint(50, 500)
            
            for m_idx, m in enumerate(months):
                if pattern == 'growth':
                    val *= 1.05 # Steady growth
                elif pattern == 'decline':
                    val *= 0.95 # Steady decline
                elif pattern == 'volatile':
                    val += random.randint(-100, 100) # Chaos
                else:
                    val += random.randint(-10, 10) # Stable
                
                val = max(5, val)
                activity[m] = int(val)
                
            _save_json(repo_dir / "activity.json", activity)
            
            # 2. OpenRank (Monthly)
            openrank = {}
            # AI/DB usually have higher impact
            base_rank = random.randint(50, 150) if owner in ['ai-labs', 'database-systems'] else random.randint(10, 80)
            val = base_rank
            for m in months:
                val = val * random.uniform(0.98, 1.02)
                openrank[m] = max(1, val)
            _save_json(repo_dir / "openrank.json", openrank)
            
            # 3. Issue Resolution (Distribution)
            # Web frameworks usually faster
            is_fast = owner in ['web-frameworks', 'mobile-tooling']
            issues = {
                "avg_resolution_time": random.randint(1, 5) if is_fast else random.randint(10, 60),
                "close_rate": random.uniform(0.8, 0.99) if is_fast else random.uniform(0.4, 0.8),
                "distribution": {
                    "<1day": random.randint(50, 100) if is_fast else random.randint(5, 20),
                    "1-7days": random.randint(20, 50),
                    ">30days": random.randint(0, 10) if is_fast else random.randint(20, 100)
                }
            }
            _save_json(repo_dir / "issue_stats.json", issues)
            
            # 4. Contributors
            contributors = []
            # Bus Factor simulation: some repos have 1-2 dominators
            has_bus_factor = random.random() < 0.3
            num_devs = random.randint(5, 50)
            
            for k in range(num_devs):
                commits = 0
                if has_bus_factor and k < 2:
                    commits = random.randint(500, 1000) # Dominators
                else:
                    commits = random.randint(1, 50) # Long tail
                    
                contributors.append({
                    "name": f"dev-{owner}-{k}",
                    "commits": commits,
                    "issues_active": random.randint(0, 20),
                    "response_speed": random.randint(1, 72)
                })
            _save_json(repo_dir / "contributors.json", contributors)

    # --- Inject Specific Scenarios for Analysis ---
    
    # 1. Declining Project (ai-labs)
    declining_dir = DATA_DIR / "mock" / "ai-labs" / "project-declining-demo"
    declining_dir.mkdir(parents=True, exist_ok=True)
    act = {}
    for i, m in enumerate(months):
        if i < 18: # First half (High)
            act[m] = random.randint(200, 300)
        else: # Second half (Crash)
            act[m] = max(5, int(200 * (0.8 ** (i-18)))) # Exponential decay
    _save_json(declining_dir / "activity.json", act)
    _save_json(declining_dir / "openrank.json", {m: random.uniform(10, 20) for m in months})
    
    # 2. High Impact, Low Activity (Legacy Giant)
    legacy_dir = DATA_DIR / "mock" / "cloud-native" / "project-legacy-core"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    _save_json(legacy_dir / "activity.json", {m: random.randint(10, 30) for m in months})
    _save_json(legacy_dir / "openrank.json", {m: random.uniform(80, 100) for m in months}) # High Rank

    # 3. High Efficiency Benchmark
    efficient_dir = DATA_DIR / "mock" / "web-frameworks" / "project-speed-demon"
    efficient_dir.mkdir(parents=True, exist_ok=True)
    _save_json(efficient_dir / "activity.json", {m: random.randint(50, 100) for m in months})
    _save_json(efficient_dir / "issue_stats.json", {
        "avg_resolution_time": 0.5,
        "close_rate": 0.98,
        "distribution": {"<1day": 200, "1-7days": 10, ">30days": 0}
    })

    # 4. Spike Anomaly (Linux Kernel simulation)
    linux_dir = DATA_DIR / "mock" / "torvalds" / "linux"
    linux_dir.mkdir(parents=True, exist_ok=True)
    # Normal activity then a huge spike
    linux_act = {}
    for i, m in enumerate(months):
        if i == len(months) - 1:
            linux_act[m] = 580.0 # Huge spike
        else:
            linux_act[m] = random.uniform(100, 130) # Stable around 117
    _save_json(linux_dir / "activity.json", linux_act)
    _save_json(linux_dir / "openrank.json", {m: random.uniform(200, 210) for m in months})

    print("Mock data generation complete.")

def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    generate_mock_data()
