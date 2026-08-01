from __future__ import annotations

import json
from pathlib import Path

import pytest

from blackholememory.provenance_attestation import PROVENANCE_ATTESTATION_SCHEMA, build_provenance_attestation_report

REPO_ROOT = Path(__file__).resolve().parents[2]


def _setup_fixture_repo(tmp_path: Path, external: dict[str, str | None], monkeypatch: pytest.MonkeyPatch) -> Path:
    import hashlib

    (tmp_path / ".git").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".gitignore").write_text(".src/\n", encoding="utf-8")
    (tmp_path / ".dockerignore").write_text(".src/\n", encoding="utf-8")
    monkeypatch.setattr("blackholememory.provenance_boundary._git_paths", lambda *args, **kwargs: [])

    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    real_registry_bytes = (REPO_ROOT / "config" / "source-registry.json").read_bytes()
    real_registry = json.loads(real_registry_bytes.decode("utf-8"))
    cbm_u = next(s for s in real_registry["sources"] if s["id"] == "CBM-U")

    minimal_registry = {
        "schema_version": "bhm.source-registry.v2",
        "plan_id": "test",
        "sources": [cbm_u],
    }
    registry_bytes = json.dumps(minimal_registry, indent=2).encode("utf-8") + b"\n"
    (config_dir / "source-registry.json").write_bytes(registry_bytes)

    s_dir = tmp_path / ".src" / "codebase-memory-mcp"
    s_dir.mkdir(parents=True, exist_ok=True)
    checkout = s_dir / "source"
    checkout.mkdir(parents=True, exist_ok=True)
    (checkout / ".git").mkdir(parents=True, exist_ok=True)

    license_content = b"MIT License\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.\n"
    (checkout / "LICENSE").write_bytes(license_content)
    license_sha = hashlib.sha256(license_content).hexdigest()

    monkeypatch.setattr("blackholememory.source_registry._run_git", lambda args, cwd=None, timeout=300: cbm_u["revision"] if "rev-parse" in args else "")
    monkeypatch.setattr("blackholememory.source_registry.git_tree_sha256", lambda checkout, rev: license_sha)

    manifest_dict = {
        "schema_version": "bhm.source-manifest.v1",
        "source_id": cbm_u["id"],
        "slug": cbm_u["slug"],
        "name": cbm_u["name"],
        "source_url": cbm_u["source_url"],
        "source_type": cbm_u["source_type"],
        "upstream_commit_or_tag": cbm_u["revision"],
        "license": cbm_u["license"],
        "license_status": cbm_u["license_status"],
        "attribution": cbm_u["attribution"],
        "purpose": cbm_u["purpose"],
        "evidence_class": cbm_u["evidence_class"],
        "disposition": cbm_u["disposition"],
        "allowed_use": cbm_u["allowed_use"],
        "reviewer": cbm_u["reviewer"],
        "recheck_date": cbm_u["recheck_date"],
        "code_copy_allowed": True,
        "transfer_mode": "direct-transfer-scoped",
        "source_is_untrusted_evidence": True,
        "permission_status": cbm_u.get("permission_status", "written-permission"),
        "permission_evidence_ref": cbm_u.get("permission_evidence_ref"),
        "rightsholder": cbm_u.get("rightsholder"),
        "covered_scope": cbm_u.get("covered_scope"),
        "covered_files": cbm_u.get("covered_files", []),
        "covered_capabilities": cbm_u.get("covered_capabilities", []),
        "third_party_exclusions": cbm_u.get("third_party_exclusions", []),
        "permission_checked_at": cbm_u.get("permission_checked_at"),
        "license_files": ["LICENSE"],
        "acquisition_status": "acquired",
        "runtime_dependency": False,
        "authoritative_bhm_state": False,
        "content_sha256": license_sha,
    }
    manifest_bytes = json.dumps(manifest_dict, indent=2).encode("utf-8") + b"\n"
    manifest_path = s_dir / "SOURCE-MANIFEST.json"
    manifest_path.write_bytes(manifest_bytes)

    identity = {
        "source_id": "CBM-U",
        "revision": cbm_u["revision"],
        "content_sha256": license_sha,
        "license": cbm_u["license"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
    }

    envelope_path = tmp_path / "attestation.json"
    envelope_path.write_text(
        json.dumps(
            {
                "schema_version": PROVENANCE_ATTESTATION_SCHEMA,
                "source_id": "CBM-U",
                "identity": identity,
                "external_evidence": external,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return envelope_path


def test_missing_external_hashes_are_unverified(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    envelope = _setup_fixture_repo(tmp_path, external={"owner_message_hash": None, "signature_hash": None, "human_adoption_approval_hash": None}, monkeypatch=monkeypatch)
    report = build_provenance_attestation_report(tmp_path, envelope)
    assert report["state"] == "unverified"
    assert report["decision"] == "review_required"
    assert set(report["external_evidence"]["missing"]) == {"owner_message_hash", "signature_hash", "human_adoption_approval_hash"}


def test_external_hashes_can_reach_verified_without_import_or_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    digest = "a" * 64
    envelope = _setup_fixture_repo(tmp_path, external={"owner_message_hash": digest, "signature_hash": digest, "human_adoption_approval_hash": digest}, monkeypatch=monkeypatch)
    report = build_provenance_attestation_report(tmp_path, envelope)
    assert report["state"] == "verified"
    assert report["execution"] == {"writes_sqlite": False, "writes_qdrant": False, "imports_quarantine": False, "runtime_dependency": False}


def test_invalid_external_hash_is_unverified_not_fabricated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    envelope = _setup_fixture_repo(tmp_path, external={"owner_message_hash": "not-a-hash", "signature_hash": None, "human_adoption_approval_hash": None}, monkeypatch=monkeypatch)
    report = build_provenance_attestation_report(tmp_path, envelope)
    assert report["state"] == "unverified"
    assert report["external_evidence"]["present"] == []
