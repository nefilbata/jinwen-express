import logging

logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    """Normalize title for comparison: lowercase, collapse whitespace, strip."""
    import re

    t = title.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def _char_bigrams(text: str) -> set[str]:
    """Generate character bigrams for similarity comparison."""
    text = text.replace(" ", "")
    if len(text) < 2:
        return {text}
    return {text[i : i + 2] for i in range(len(text) - 1)}


def jaccard_similarity(a: str, b: str) -> float:
    """Jaccard similarity coefficient of character bigrams."""
    ba = _char_bigrams(a)
    bb = _char_bigrams(b)
    if not ba and not bb:
        return 1.0
    if not ba or not bb:
        return 0.0
    intersection = len(ba & bb)
    union = len(ba | bb)
    return intersection / union if union > 0 else 0.0


class DedupService:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def deduplicate(self, papers: list) -> list:
        """Deduplicate papers by title similarity. Keeps first occurrence."""
        if not papers:
            return []

        unique: list = []
        unique_norm: list[str] = []

        for p in papers:
            norm = normalize_title(p.title)
            if not norm:
                continue

            is_dup = False
            for i, existing_norm in enumerate(unique_norm):
                # Fast exact match first
                if norm == existing_norm:
                    logger.debug(f"Dedup exact match: {p.title[:60]}")
                    is_dup = True
                    break
                # Then bigram similarity
                if jaccard_similarity(norm, existing_norm) >= self.threshold:
                    logger.debug(
                        f"Dedup fuzzy match: {p.title[:60]} ~= {unique[i].title[:60]}"
                    )
                    is_dup = True
                    break

            if not is_dup:
                unique.append(p)
                unique_norm.append(norm)

        removed = len(papers) - len(unique)
        if removed:
            logger.info(f"Dedup removed {removed} duplicates")
        return unique
