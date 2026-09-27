"""Persistencia de entidades y decisiones del matching."""

from collections.abc import Iterable

from app.db import connect
from app.matching.domain.models import Decision, Venue


SCHEMA = """
CREATE TABLE IF NOT EXISTS just_eat_venues (
    just_eat_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    postal_code TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
CREATE TABLE IF NOT EXISTS google_venues (
    google_place_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    postal_code TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
CREATE TABLE IF NOT EXISTS restaurant_matches (
    just_eat_id TEXT PRIMARY KEY REFERENCES just_eat_venues(just_eat_id),
    google_place_id TEXT REFERENCES google_venues(google_place_id),
    status TEXT NOT NULL CHECK (status IN ('matched', 'ambiguous', 'unmatched')),
    score DOUBLE PRECISION,
    name_score DOUBLE PRECISION,
    address_score DOUBLE PRECISION,
    distance_meters DOUBLE PRECISION,
    runner_up_score DOUBLE PRECISION,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def save_decisions(venues: Iterable[Venue], decisions: Iterable[Decision]) -> None:
    venues_by_id = {venue.identifier: venue for venue in venues}
    decisions = list(decisions)
    google_venues = [decision.candidate.venue for decision in decisions if decision.candidate]
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA)
            # El estado materializado representa el ultimo pack. Los resultados de
            # packs anteriores permanecen disponibles como artefactos inmutables de
            # sus ejecuciones y no deben contaminar la siguiente clasificacion.
            cursor.execute("DELETE FROM restaurant_matches")
            cursor.executemany(
                """INSERT INTO just_eat_venues (just_eat_id, name, address, postal_code, latitude, longitude)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (just_eat_id) DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address,
                   postal_code = EXCLUDED.postal_code, latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude""",
                [_venue_row(venues_by_id[decision.just_eat_id]) for decision in decisions],
            )
            cursor.executemany(
                """INSERT INTO google_venues (google_place_id, name, address, postal_code, latitude, longitude)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (google_place_id) DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address,
                   postal_code = EXCLUDED.postal_code, latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude""",
                [_google_row(venue) for venue in google_venues],
            )
            cursor.executemany(
                """INSERT INTO restaurant_matches
                   (just_eat_id, google_place_id, status, score, name_score, address_score, distance_meters, runner_up_score)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (just_eat_id) DO UPDATE SET google_place_id = EXCLUDED.google_place_id,
                   status = EXCLUDED.status, score = EXCLUDED.score, name_score = EXCLUDED.name_score,
                   address_score = EXCLUDED.address_score, distance_meters = EXCLUDED.distance_meters,
                   runner_up_score = EXCLUDED.runner_up_score, updated_at = NOW()""",
                [_decision_row(decision) for decision in decisions],
            )


def _venue_row(venue: Venue) -> tuple:
    return venue.identifier, venue.name, venue.address, venue.postal_code, venue.latitude, venue.longitude


def _google_row(venue: Venue) -> tuple:
    return venue.identifier, venue.name, venue.address, venue.postal_code, venue.latitude, venue.longitude


def _decision_row(decision: Decision) -> tuple:
    candidate = decision.candidate
    return (
        decision.just_eat_id,
        candidate.venue.identifier if candidate else None,
        decision.status,
        candidate.score if candidate else None,
        candidate.name_score if candidate else None,
        candidate.address_score if candidate else None,
        candidate.distance_meters if candidate else None,
        decision.runner_up.score if decision.runner_up else None,
    )
