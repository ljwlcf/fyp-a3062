"""Shared helpers for the Phase 1 structural measurements.

Loads SWE-bench instances, checks a repository out at its base commit, builds the
SWE-Debate dependency graph for it, and maps a gold patch onto graph nodes.

The graph itself is SWE-Debate's, imported unmodified from the fork in swe-debate/
so that what we measure is the graph the system actually walks.
"""

import ast
import os
import os.path as osp
import pickle
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = osp.dirname(osp.dirname(osp.dirname(osp.abspath(__file__))))
SWE_DEBATE_LOCALIZATION = osp.join(REPO_ROOT, "swe-debate", "localization")
if SWE_DEBATE_LOCALIZATION not in sys.path:
    sys.path.insert(0, SWE_DEBATE_LOCALIZATION)

from dependency_graph.build_graph import (  # noqa: E402
    VERSION as GRAPH_VERSION,
    NODE_TYPE_CLASS,
    NODE_TYPE_DIRECTORY,
    NODE_TYPE_FILE,
    NODE_TYPE_FUNCTION,
    build_graph,
)
from dependency_graph.traverse_graph import is_test_file  # noqa: E402

ENTITY_NODE_TYPES = (NODE_TYPE_CLASS, NODE_TYPE_FUNCTION)


# --------------------------------------------------------------------------
# dataset
# --------------------------------------------------------------------------

def load_instances(parquet_path: str, instance_id_path: Optional[str] = None) -> List[dict]:
    import pandas as pd

    df = pd.read_parquet(parquet_path)
    if instance_id_path:
        with open(instance_id_path) as f:
            wanted = [line.strip() for line in f if line.strip()]
        df = df.set_index("instance_id").loc[wanted].reset_index()
    return df.to_dict("records")


def repo_dir(repos_root: str, repo: str) -> str:
    return osp.join(repos_root, repo.replace("/", "__"))


def checkout(repo_path: str, commit: str) -> None:
    """Hard-reset the working tree to `commit`. The clone is ours, so this is safe."""
    subprocess.run(["git", "-C", repo_path, "checkout", "-f", "-q", commit], check=True)
    subprocess.run(["git", "-C", repo_path, "clean", "-xdfq"], check=True)


# --------------------------------------------------------------------------
# graph
# --------------------------------------------------------------------------

def strip_graph(G):
    """Drop `code` attributes. The full graph holds every file's source, which is far
    too large to cache 75 times; structure plus line spans is all the measurements need."""
    import networkx as nx

    H = nx.MultiDiGraph()
    for nid, data in G.nodes(data=True):
        attrs = {"type": data.get("type")}
        if "start_line" in data:
            attrs["start_line"] = data["start_line"]
        if "end_line" in data:
            attrs["end_line"] = data["end_line"]
        if data.get("type") == NODE_TYPE_FILE:
            attrs["n_lines"] = len(data.get("code", "").split("\n"))
        H.add_node(nid, **attrs)
    for u, v, data in G.edges(data=True):
        H.add_edge(u, v, type=data["type"])
    return H


def build_or_load_graph(instance: dict, repos_root: str, cache_dir: str,
                        global_import: bool = True, fuzzy_search: bool = True):
    """Return the stripped dependency graph for one instance, building it if needed."""
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = osp.join(cache_dir, f"{instance['instance_id']}.pkl")
    if osp.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f), True

    path = repo_dir(repos_root, instance["repo"])
    checkout(path, instance["base_commit"])
    G = build_graph(path, fuzzy_search=fuzzy_search, global_import=global_import)
    H = strip_graph(G)
    del G
    with open(cache_path, "wb") as f:
        pickle.dump(H, f, protocol=pickle.HIGHEST_PROTOCOL)
    return H, False


def orphan_file_nodes(G) -> List[str]:
    """Files that are nodes but whose contents SWE-Debate could not parse.

    build_graph() adds the file node before calling analyze_file(); on
    SyntaxError/UnicodeDecodeError it `continue`s, so the file node survives with no
    children and no containment edge from its directory. Those files are in the graph
    but unreachable through it.
    """
    orphans = []
    for nid, data in G.nodes(data=True):
        if data.get("type") != NODE_TYPE_FILE:
            continue
        if G.in_degree(nid) == 0:
            orphans.append(nid)
    return sorted(orphans)


# --------------------------------------------------------------------------
# gold patch -> files and pre-image line numbers
# --------------------------------------------------------------------------

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse_patch(patch: str) -> Dict[str, Dict]:
    """Map each file touched by a unified diff to the pre-image lines it changes.

    Returns {path: {"lines": sorted[int], "added_only": bool, "new_file": bool,
                    "deleted_file": bool}}.
    Line numbers are in the PRE-image (the base commit), which is what the graph is
    built from. A hunk that only adds lines has no pre-image line of its own, so the
    line just before the insertion point is recorded instead; that is enough to find
    the enclosing function or class.
    """
    files: Dict[str, Dict] = {}
    current = None
    src = ""
    old_ln = 0
    in_hunk = False
    hunk_had_removal = False

    for raw in patch.split("\n"):
        if raw.startswith("diff --git "):
            current = None
            in_hunk = False
            continue
        # header lines only count outside a hunk: a removed source line can also
        # start with "--- "
        if not in_hunk and raw.startswith("--- "):
            src = raw[4:].strip()
            continue
        if not in_hunk and raw.startswith("+++ "):
            dst = raw[4:].strip()
            path = dst[2:] if dst.startswith("b/") else dst
            if dst == "/dev/null":
                path = src[2:] if src.startswith("a/") else src
            current = path
            entry = files.setdefault(current, {
                "lines": set(), "added_only": True,
                "new_file": src == "/dev/null", "deleted_file": dst == "/dev/null",
            })
            continue
        if current is None:
            continue

        m = _HUNK_RE.match(raw)
        if m:
            old_ln = int(m.group(1))
            in_hunk = True
            hunk_had_removal = False
            continue
        if raw.startswith("-") and not raw.startswith("---"):
            files[current]["lines"].add(old_ln)
            files[current]["added_only"] = False
            hunk_had_removal = True
            old_ln += 1
        elif raw.startswith("+") and not raw.startswith("+++"):
            if not hunk_had_removal:
                # pure insertion: anchor on the preceding pre-image line
                files[current]["lines"].add(max(old_ln - 1, 1))
        elif raw.startswith(" ") or raw == "":
            old_ln += 1
        # '\ No newline at end of file' and anything else: ignore

    for entry in files.values():
        entry["lines"] = sorted(entry["lines"])
    return files


def gold_nodes(G, patch_files: Dict[str, Dict]) -> Dict[str, dict]:
    """Map gold files onto graph nodes.

    For each gold file, report whether the file node exists and which class/function
    nodes span the changed lines (innermost containing node per line).
    """
    by_file: Dict[str, List[Tuple[str, int, int]]] = defaultdict(list)
    for nid, data in G.nodes(data=True):
        if data.get("type") not in ENTITY_NODE_TYPES:
            continue
        if "start_line" not in data or "end_line" not in data:
            continue
        by_file[nid.split(":")[0]].append((nid, data["start_line"], data["end_line"]))

    out = {}
    for path, info in patch_files.items():
        entities, uncovered = set(), []
        for line in info["lines"]:
            containing = [(e - s, nid) for nid, s, e in by_file.get(path, [])
                          if s <= line <= e]
            if containing:
                entities.add(min(containing)[1])
            else:
                uncovered.append(line)
        out[path] = {
            "is_python": path.endswith(".py"),
            "file_node_in_graph": path in G,
            "excluded_by_test_filter": is_test_file(path),
            "new_file": info["new_file"],
            "deleted_file": info["deleted_file"],
            "changed_lines": len(info["lines"]),
            "lines_outside_any_entity": len(uncovered),
            "entity_nodes": sorted(entities),
        }
    return out


# --------------------------------------------------------------------------
# entry set: names the issue text mentions
# --------------------------------------------------------------------------

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_PATH_RE = re.compile(r"[\w./-]+\.py")

_STOPWORDS = set(dir(__builtins__) if isinstance(__builtins__, dict) else dir(__builtins__))
_STOPWORDS |= set(getattr(__import__("keyword"), "kwlist"))
_STOPWORDS |= {
    "self", "cls", "args", "kwargs", "None", "True", "False", "test", "tests",
    "python", "django", "sympy", "sphinx", "error", "code", "line", "file", "data",
    "value", "result", "name", "type", "class", "def", "return", "import", "from",
}


def name_index(G) -> Dict[str, List[str]]:
    """Short name -> node ids, mirroring RepoEntitySearcher.global_name_dict
    (test files excluded, files indexed by basename with and without .py)."""
    index: Dict[str, List[str]] = defaultdict(list)
    for nid in G.nodes():
        if is_test_file(nid):
            continue
        if nid.endswith(".py"):
            fname = nid.split("/")[-1]
            index[fname].append(nid)
            index[fname[:-3]].append(nid)
        elif ":" in nid:
            index[nid.split(":")[-1].split(".")[-1]].append(nid)
    return index


def issue_entry_nodes(G, problem_statement: str, index: Dict[str, List[str]],
                      min_name_len: int = 3, max_nodes_per_name: Optional[int] = None,
                      use_stopwords: bool = True) -> Tuple[Set[str], Dict[str, int]]:
    """Nodes whose name is mentioned verbatim in the issue text.

    A deterministic stand-in for SWE-Debate's stage-1 LLM entity extraction: whatever
    the LLM names, it can only name entities the issue text refers to. Generous, so
    reachability measured from here is an upper bound on the real pipeline's.
    """
    entry: Set[str] = set()
    matched_names: Dict[str, int] = {}

    tokens = set(_IDENT_RE.findall(problem_statement))
    for path in _PATH_RE.findall(problem_statement):
        if path in G and not is_test_file(path):
            entry.add(path)
            matched_names[path] = 1
        tokens.add(path.split("/")[-1])

    stop = _STOPWORDS if use_stopwords else frozenset()
    for tok in tokens:
        if len(tok) < min_name_len or tok in stop:
            continue
        hits = index.get(tok)
        if not hits:
            continue
        if max_nodes_per_name is not None and len(hits) > max_nodes_per_name:
            continue
        entry.update(hits)
        matched_names[tok] = len(hits)

    return entry, matched_names
