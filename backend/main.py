from collections import defaultdict
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PipelinePayload(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


def is_directed_acyclic_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> bool:
    node_ids = {node.get("id") for node in nodes if node.get("id")}
    adjacency = defaultdict(list)
    indegree = {node_id: 0 for node_id in node_ids}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in indegree or target not in indegree:
            continue
        adjacency[source].append(target)
        indegree[target] += 1

    queue = [node_id for node_id, degree in indegree.items() if degree == 0]
    visited = 0
    pointer = 0

    while pointer < len(queue):
        node_id = queue[pointer]
        pointer += 1
        visited += 1
        for neighbor in adjacency[node_id]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited == len(node_ids)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(payload: PipelinePayload):
    return {
        'num_nodes': len(payload.nodes),
        'num_edges': len(payload.edges),
        'is_dag': is_directed_acyclic_graph(payload.nodes, payload.edges),
    }
