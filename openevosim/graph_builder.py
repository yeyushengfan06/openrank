import os
import json
# Fallback to networkx if easygraph is broken
try:
    import easygraph as eg
except (ImportError, ModuleNotFoundError):
    import networkx as eg

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class EcosystemGraphBuilder:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.graph = eg.Graph()
        self.developers = set()
        self.repos = set()

    def load_data(self):
        """
        Recursively find contributors_detail.json files and build the graph.
        """
        logger.info(f"Scanning {self.data_dir} for contributors data...")
        
        for root, dirs, files in os.walk(self.data_dir):
            if "contributors_detail.json" in files:
                self._process_contributors_file(Path(root), "contributors_detail.json")
            # Also support bus_factor_detail which gives core devs
            if "bus_factor_detail.json" in files:
                self._process_contributors_file(Path(root), "bus_factor_detail.json")

        logger.info(f"Graph built with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")

    def _process_contributors_file(self, dir_path: Path, filename: str):
        """
        Extract repo info from path and add edges.
        Path structure usually: .../{platform}/{owner}/{repo}/...
        """
        try:
            # Attempt to extract owner/repo from path
            # We assume the path contains .../owner/repo/...
            # This is heuristic based on OpenDigger folder structure
            parts = dir_path.parts
            
            # Simple heuristic: look for 'github' or 'gitee' and take next two
            repo_name = "unknown/unknown"
            if 'github' in parts:
                idx = parts.index('github')
                if idx + 2 < len(parts):
                    repo_name = f"{parts[idx+1]}/{parts[idx+2]}"
            elif 'gitee' in parts:
                idx = parts.index('gitee')
                if idx + 2 < len(parts):
                    repo_name = f"{parts[idx+1]}/{parts[idx+2]}"
            else:
                # Fallback: use the last two directory names before 'developers' or just parent
                if 'developers' in parts:
                    dev_idx = parts.index('developers')
                    repo_name = f"{parts[dev_idx-2]}/{parts[dev_idx-1]}"
                else:
                    repo_name = f"{parts[-2]}/{parts[-1]}"

            file_path = dir_path / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Data format: "2015": ["dev1", "dev2"] or "2015": [["dev1", score], ...]
            # We aggregate all time
            
            contributors = set()
            
            for period, user_list in data.items():
                for item in user_list:
                    if isinstance(item, list):
                        user = item[0] # [name, score]
                    else:
                        user = item # name
                    contributors.add(user)

            # Add Nodes and Edges
            self.graph.add_node(repo_name, type="repo")
            self.repos.add(repo_name)
            
            for user in contributors:
                self.graph.add_node(user, type="developer")
                self.developers.add(user)
                # Weighted edge could be added if we count frequency, 
                # for now just existence
                self.graph.add_edge(user, repo_name)
                
        except Exception as e:
            logger.error(f"Error processing {dir_path}/{filename}: {e}")

    def get_project_developer_network(self) -> eg.Graph:
        return self.graph

    def get_developer_network(self) -> eg.Graph:
        """
        Project the bipartite graph to a developer-developer network.
        Two developers are connected if they contribute to the same repo.
        """
        # EasyGraph doesn't have a direct bipartite projection yet? 
        # We can do it manually or check if it exists.
        # Implementing manual projection for safety.
        
        dev_graph = eg.Graph()
        for dev in self.developers:
            dev_graph.add_node(dev, type="developer")
            
        # For each repo, connect all its devs
        for repo in self.repos:
            if not self.graph.has_node(repo):
                continue
            neighbors = list(self.graph.neighbors(repo))
            # Create clique
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u, v = neighbors[i], neighbors[j]
                    if dev_graph.has_edge(u, v):
                        dev_graph[u][v]['weight'] += 1
                    else:
                        dev_graph.add_edge(u, v, weight=1)
                        
        return dev_graph
