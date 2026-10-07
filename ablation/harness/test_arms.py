"""Unit tests for the arm wrappers in run_localization.py (no GPU, no pipeline import).

A fake pipeline replays the call sequence run_pipeline uses for stages 6-7 (vote, then
_generate_modification_plan, which calls _conduct_second_round_analysis) and logs what was called.

Usage:  python ablation/harness/test_arms.py      (needs pyyaml)
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rl", os.path.join(HERE, "run_localization.py"))
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)


class Fake:
    def __init__(self, votes):
        self.votes, self.log = votes, []

    def _vote_on_chains(self, chains, issue, num_agents=5):
        self.log.append(("vote", num_agents))
        w, n = self.votes
        return {"success": True, "winning_chain": {"c": 1}, "winning_votes": w,
                "total_valid_votes": n}

    def _conduct_second_round_analysis(self, chain_info, issue, first, instance_id=None,
                                       cache_timestamp=None):
        self.log.append(("round2_released", len(first)))
        return first

    def _generate_modification_plan(self, chain, issue, num_agents=5, instance_id=None,
                                    cache_timestamp=None):
        self.log.append(("plan", num_agents))
        first = [{"analysis": {"modification_locations": [{"entity_id": "x"}]}}
                 for _ in range(num_agents)]
        return {"second": self._conduct_second_round_analysis("c", issue, first, instance_id,
                                                              cache_timestamp)}

    def run(self):   # stage 6 then stage 7, as run_pipeline calls them
        v = self._vote_on_chains([], "issue", num_agents=5)
        return self._generate_modification_plan(v["winning_chain"], "issue", 5, "iid", "ts")


def adaptive(tau=1.0, **extra):
    return {"name": "adaptive", "trigger": {"signal": "vote_agreement", "threshold": tau}, **extra}


def test_adaptive_single_agent():
    for votes, skip in [((5, 5), True), ((4, 5), False), ((3, 4), False), ((0, 0), False)]:
        p = Fake(votes)
        info = rl.apply_arm(p, adaptive())
        out = p.run()
        assert info["skipped"] == skip and info["skip_mode"] == "single_agent", (votes, info)
        if skip:
            assert p.log == [("vote", 5), ("plan", 1)], p.log
            a = out["second"][0]
            assert a["round"] == "second_round_skipped"
            assert a["analysis"]["refined_modification_locations"] == [{"entity_id": "x"}]
        else:
            assert p.log == [("vote", 5), ("plan", 5), ("round2_released", 5)], p.log


def test_adaptive_round1_only():
    p = Fake((5, 5))
    info = rl.apply_arm(p, adaptive(skip_mode="round1_only"))
    out = p.run()
    assert info["skipped"] and p.log == [("vote", 5), ("plan", 5)], p.log
    assert len(out["second"]) == 5 and all(a["round"] == "second_round_skipped" for a in out["second"])
    p = Fake((3, 5))
    info = rl.apply_arm(p, adaptive(skip_mode="round1_only"))
    p.run()
    assert not info["skipped"] and p.log == [("vote", 5), ("plan", 5), ("round2_released", 5)]


def test_adaptive_threshold_and_errors():
    p = Fake((4, 5))
    info = rl.apply_arm(p, adaptive(0.8))
    p.run()
    assert info["skipped"] and p.log == [("vote", 5), ("plan", 1)]
    for bad in (adaptive(skip_mode="nope"),
                {"name": "adaptive", "trigger": {"signal": "lp_conf", "threshold": 0.9}}):
        try:
            rl.apply_arm(Fake((5, 5)), bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad}")


def test_self_consistency():
    p = Fake((7, 9))
    info = rl.apply_arm(p, {"name": "self_consistency", "n_votes": 9})
    out = p.run()
    assert info == {"name": "self_consistency", "n_votes": 9}
    assert p.log == [("vote", 9), ("plan", 1)] and out["second"][0]["round"] == "second_round_skipped"


def test_original_untouched():
    p = Fake((3, 5))
    assert rl.apply_arm(p, {"name": "original"}) == {"name": "original"}
    p.run()
    assert p.log == [("vote", 5), ("plan", 5), ("round2_released", 5)]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
    print("ALL OK")
