import json
import os
from pathlib import Path
import tempfile

from app.matching.domain.models import Decision


def write_sample(path: Path, decisions: list[Decision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".match-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump([_as_dict(decision) for decision in decisions], stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def _as_dict(decision: Decision) -> dict:
    def candidate(value):
        return None if value is None else {
            "googlePlaceId": value.venue.identifier, "name": value.venue.name,
            "score": value.score, "nameScore": value.name_score,
            "addressScore": value.address_score, "cuisineScore": value.cuisine_score, "distanceMeters": value.distance_meters,
        }

    return {"justEatId": decision.just_eat_id, "status": decision.status, "reason": decision.reason,
            "candidate": candidate(decision.candidate), "runnerUp": candidate(decision.runner_up)}
