"""
Evaluation script — test permission filtering, search quality, and end-to-end flow.
Run: python scripts/evaluate.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.auth import create_token, get_user_context
from backend.services.retriever import hybrid_search
from backend.services.reranker import rerank
from backend.services.generator import generate_answer
from backend.services.permissions import build_permission_filter


def test_permission_filtering():
    """Test that restricted documents are only visible to authorized users."""
    print("=" * 60)
    print("TEST 1: Permission Filtering")
    print("=" * 60)

    test_cases = [
        {
            "user_id": "amrutha",
            "query": "What are the salary bands?",
            "should_see": "Compensation Policy",
            "reason": "Alice has 'hr' role → can see restricted HR docs",
        },
        {
            "user_id": "harshini",
            "query": "What are the salary bands?",
            "should_not_see": "Compensation Policy",
            "reason": "Bob is an engineer → cannot see restricted HR docs",
        },
        {
            "user_id": "tanvi",
            "query": "What is the sales commission structure?",
            "should_see": "Sales Playbook",
            "reason": "Carol has 'sales' role → can see restricted Sales docs",
        },
        {
            "user_id": "harshini",
            "query": "What is the sales commission structure?",
            "should_not_see": "Sales Playbook",
            "reason": "Bob is an engineer → cannot see restricted Sales docs",
        },
        {
            "user_id": "bhaskar",
            "query": "What are the salary bands?",
            "should_see": "Compensation Policy",
            "reason": "Bhaskar has 'admin' role → can see all docs",
        },
    ]

    passed = 0
    for tc in test_cases:
        user_ctx = get_user_context(tc["user_id"])
        results = hybrid_search(tc["query"], user_ctx, top_k=10)
        doc_titles = [r["doc_title"] for r in results]

        if "should_see" in tc:
            found = tc["should_see"] in doc_titles
            status = "PASS" if found else "FAIL"
            print(f"  {status}: {tc['user_id']} searching '{tc['query']}'")
            print(f"         Expected to see: '{tc['should_see']}' -- {tc['reason']}")
            if found:
                passed += 1
        else:
            blocked = tc["should_not_see"] not in doc_titles
            status = "PASS" if blocked else "FAIL"
            print(f"  {status}: {tc['user_id']} searching '{tc['query']}'")
            print(f"         Expected NOT to see: '{tc['should_not_see']}' -- {tc['reason']}")
            if blocked:
                passed += 1
        print()

    print(f"  Result: {passed}/{len(test_cases)} permission tests passed.\n")
    return passed == len(test_cases)


def test_search_relevance():
    """Test that search results are relevant to the query."""
    print("=" * 60)
    print("TEST 2: Search Relevance")
    print("=" * 60)

    test_cases = [
        {
            "query": "What is the PTO policy?",
            "expected_doc": "Employee Handbook",
            "user_id": "amrutha",
        },
        {
            "query": "What caused incident 5023?",
            "expected_doc": "Incident Report INC-5023",
            "user_id": "harshini",
        },
        {
            "query": "What are our pricing tiers?",
            "expected_doc": "Pricing Tiers",
            "user_id": "tanvi",
        },
        {
            "query": "What is the tech stack?",
            "expected_doc": "Architecture Overview",
            "user_id": "harshini",
        },
        {
            "query": "How do I submit a code review?",
            "expected_doc": "Coding Standards",
            "user_id": "harshini",
        },
    ]

    passed = 0
    for tc in test_cases:
        user_ctx = get_user_context(tc["user_id"])
        results = hybrid_search(tc["query"], user_ctx, top_k=5)
        ranked = rerank(tc["query"], results, top_n=3)

        top_title = ranked[0]["doc_title"] if ranked else "NONE"
        all_titles = [r["doc_title"] for r in ranked[:3]]

        is_top = top_title == tc["expected_doc"]
        is_in_top3 = tc["expected_doc"] in all_titles

        if is_top:
            status = "PASS (top-1)"
        elif is_in_top3:
            status = "PASS (top-3)"
        else:
            status = "FAIL"

        if is_top or is_in_top3:
            passed += 1

        print(f"  {status}: '{tc['query']}'")
        print(f"         Expected: '{tc['expected_doc']}' | Got top-3: {all_titles}")
        print()

    print(f"  Result: {passed}/{len(test_cases)} relevance tests passed.\n")
    return passed == len(test_cases)


def test_end_to_end_latency():
    """Test end-to-end latency (search + rerank, without LLM)."""
    print("=" * 60)
    print("TEST 3: End-to-End Latency (Search + Rerank)")
    print("=" * 60)

    user_ctx = get_user_context("amrutha")
    queries = [
        "What is the remote work policy?",
        "How to request PTO?",
        "What are our company values?",
    ]

    latencies = []
    for q in queries:
        start = time.time()
        results = hybrid_search(q, user_ctx, top_k=20)
        ranked = rerank(q, results, top_n=8)
        elapsed_ms = int((time.time() - start) * 1000)
        latencies.append(elapsed_ms)
        print(f"  '{q}' -> {len(ranked)} results in {elapsed_ms} ms")

    avg = sum(latencies) / len(latencies)
    print(f"\n  Average latency: {int(avg)} ms")
    ok = avg < 5000  # Under 5 seconds is our target for PoC
    status = "PASS" if ok else "SLOW"
    print(f"  {status}: Target < 5000 ms\n")
    return ok


def main():
    print("\nEKIP PoC Evaluation\n")

    r1 = test_permission_filtering()
    r2 = test_search_relevance()
    r3 = test_end_to_end_latency()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Permission Filtering: {'PASS' if r1 else 'FAIL'}")
    print(f"  Search Relevance:     {'PASS' if r2 else 'FAIL'}")
    print(f"  Latency:              {'PASS' if r3 else 'SLOW'}")

    all_pass = r1 and r2 and r3
    print(f"\n{'All tests passed!' if all_pass else 'Some tests need attention.'}\n")


if __name__ == "__main__":
    main()
