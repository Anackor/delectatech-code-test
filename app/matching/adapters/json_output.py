import json
import os
from pathlib import Path
import tempfile

from app.matching.domain.models import Decision, Venue


def write_sample(path: Path, sources: list[Venue], decisions: list[Decision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".match-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            source_by_id = {source.identifier: source for source in sources}
            json.dump([_as_dict(source_by_id[decision.just_eat_id], decision) for decision in decisions], stream,
                      ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def _as_dict(source: Venue, decision: Decision) -> dict:
    return {
        "source": {"provider": source.source, "id": source.identifier, "name": source.name},
        "decision": {
            "status": decision.status,
            "reason": decision.reason,
            "selectedGooglePlaceId": decision.candidate.venue.identifier if decision.status == "matched" and decision.candidate else None,
        },
        "proposals": [_proposal(proposal) for proposal in decision.proposals],
    }


def _proposal(proposal) -> dict:
    return {
        "venue": {"provider": proposal.venue.source, "id": proposal.venue.identifier, "name": proposal.venue.name},
        "evidence": {"score": proposal.score, "nameScore": proposal.name_score,
                     "addressScore": proposal.address_score, "distanceScore": proposal.distance_score,
                     "distanceMeters": proposal.distance_meters},
    }
