"""Permission-aware BM25 baseline with extractive evidence and explicit abstention."""

from collections import Counter
from datetime import date
import math
import re
import unicodedata


STOPWORDS = set("a o as os de da do das dos e em no na nos nas um uma qual quais que como para por com posso devo ao se quando onde what is the how to of for and".split())
ALIASES = {"comprar": "compra", "compras": "compra", "cotacoes": "cotacao",
           "cotar": "cotacao", "fornecedores": "fornecedor", "contratos": "contrato",
           "vencimentos": "vencimento", "vence": "vencimento", "vencer": "vencimento",
           "documentos": "documento", "reembolsos": "reembolso", "despesas": "despesa",
           "backups": "backup", "incidentes": "incidente", "acessos": "acesso"}
ROLES = {"operations", "finance", "legal"}


def tokens(text):
    plain = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                    if unicodedata.category(c) != "Mn")
    return [ALIASES.get(word, word) for word in re.findall(r"[a-z0-9]+", plain)
            if word not in STOPWORDS]


def visible_documents(documents, role, as_of):
    if role not in ROLES:
        raise ValueError("Unknown demo role; access denied")
    today = date.fromisoformat(as_of)
    eligible = [doc for doc in documents
                if role in doc["roles"]
                and date.fromisoformat(doc["valid_from"]) <= today
                and (not doc.get("valid_until") or today < date.fromisoformat(doc["valid_until"]))]
    # Validity intervals are [from, until). Overlapping revisions fail closed.
    keys = [doc["id"] for doc in eligible]
    if len(keys) != len(set(keys)):
        raise ValueError("Overlapping active document versions")
    return eligible


def retrieve(documents, question, *, role, as_of="2026-06-30", k=3):
    if not 1 <= k <= 10:
        raise ValueError("k must be between 1 and 10")
    visible = visible_documents(documents, role, as_of)
    query = set(tokens(question))
    if not query or not visible:
        return []
    corpus = [Counter(tokens(doc["title"] + " " + doc["body"])) for doc in visible]
    avg_len = sum(sum(doc.values()) for doc in corpus) / len(corpus)
    df = Counter(term for doc in corpus for term in doc)
    ranked = []
    for doc, counts in zip(visible, corpus):
        overlap = query & counts.keys()
        coverage = len(overlap) / len(query)
        # Conservative lexical baseline, not a calibrated confidence probability.
        if coverage < 0.55 or len(overlap) < min(2, len(query)):
            continue
        score = 0.0
        for term in overlap:
            inverse_frequency = math.log(1 + (len(corpus) - df[term] + 0.5) / (df[term] + 0.5))
            frequency = counts[term]
            score += inverse_frequency * frequency * 2.5 / (frequency + 1.5 * (0.25 + 0.75 * sum(counts.values()) / avg_len))
        ranked.append({
            "document_id": doc["id"], "version": doc["version"], "title": doc["title"],
            "citation": f"{doc['id']}@v{doc['version']}#p1", "excerpt": doc["body"],
            "score": round(score, 6), "term_coverage": round(coverage, 3),
        })
    return sorted(ranked, key=lambda hit: (-hit["score"], hit["document_id"]))[:k]


def answer(documents, question, *, role="operations", as_of="2026-06-30"):
    hits = retrieve(documents, question, role=role, as_of=as_of)
    return {
        "synthetic": True, "mode": "extractive_bm25_baseline", "role": role, "as_of": as_of,
        "status": "evidence_found" if hits else "abstained", "citations": hits,
        "answer": hits[0]["excerpt"] if hits else "Não encontrei evidência suficiente no acervo permitido. Encaminhe a pergunta ao responsável pelo processo.",
        "limitation": "Extractive retrieval only: no LLM, embeddings, legal advice or automated action.",
    }


def evaluate(documents, cases):
    results = []
    for case in cases:
        response = answer(documents, case["question"], role=case["role"], as_of=case.get("as_of", "2026-06-30"))
        expected = case["expected_document"]
        found = [hit["document_id"] for hit in response["citations"]]
        passed = expected in found if expected else not found
        rank = found.index(expected) + 1 if expected in found else None
        results.append({"id": case["id"], "expected": expected, "found": found,
                        "passed": passed, "rank": rank, "status": response["status"]})
    positives = [row for row in results if row["expected"]]
    negatives = [row for row in results if not row["expected"]]
    return {
        "synthetic": True, "cases": len(results), "passed": sum(row["passed"] for row in results),
        "retrieval_hit_at_3": sum(row["passed"] for row in positives) / len(positives) if positives else None,
        "mean_reciprocal_rank": sum(1 / row["rank"] if row["rank"] else 0 for row in positives) / len(positives) if positives else None,
        "abstention_accuracy": sum(row["passed"] for row in negatives) / len(negatives) if negatives else None,
        "results": results,
        "scope": "Small authored synthetic regression suite, not a representative production benchmark.",
    }
