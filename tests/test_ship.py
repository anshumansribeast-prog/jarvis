"""Ship report, GitHub push helpers, Abhishek mail draft."""

from __future__ import annotations

import json
import os
import shutil
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request as urlreq

import pytest

import command_office
import command_office.runtime as runtime
import command_office.ship as ship
import command_office.store as store
import team
from command_office.orchestrator import commander_chat


@pytest.fixture
def office_data(tmp_path, monkeypatch):
    data = tmp_path / "data"
    work = tmp_path / "workspace"
    monkeypatch.setattr(command_office, "DATA", data)
    monkeypatch.setattr(command_office, "WORKSPACE", work)
    monkeypatch.setattr(store, "DATA", data)
    monkeypatch.setattr(store, "WORKSPACE", work)
    monkeypatch.setattr(runtime, "WORKSPACE", work)
    monkeypatch.setattr(team, "ROOT", tmp_path)
    store.ensure_dirs()
    return tmp_path


def test_build_report_and_mailto(office_data, monkeypatch):
    ship.set_abhishek_email("abhishek@example.com")
    commander_chat("Build a website called ship-demo")
    report = ship.build_report()
    assert "Abhishek" in report["body"]
    assert report["path"] == "office/briefing-abhishek.md"
    link = ship.mailto_link(report)
    assert link.startswith("mailto:abhishek@example.com")
    assert "ANSHUX" in link


def test_default_abhishek_email_is_eleven11():
    assert "eleven11.pro" in ship.DEFAULT_ABHISHEK
    assert ship.DEFAULT_ABHISHEK == "abhiis@eleven11.pro" or os.environ.get("ANSHUX_ABHISHEK_EMAIL")


def test_ship_mail_falls_back_to_mailto(office_data, monkeypatch):
    monkeypatch.delenv("ANSHUX_SMTP_HOST", raising=False)
    ship.set_abhishek_email("abhishek@example.com")
    result = ship.ship_all(push=False, mail=True)
    assert result["mail"]["ok"] is False
    assert result["mailto"].startswith("mailto:")


def test_ship_http(office_data, monkeypatch):
    src = Path(__file__).resolve().parents[1] / "office" / "index.html"
    office = office_data / "office"
    office.mkdir()
    shutil.copy(src, office / "index.html")
    commander_chat("Build a website.")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), team.OfficeHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]
    try:
        home = urlreq.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode()
        assert "VR office" in home
        assert "Ship · GitHub · Mail" in home
        report = json.loads(urlreq.urlopen(f"http://127.0.0.1:{port}/api/command/ship", timeout=8).read().decode())
        assert report["ok"] is True
        assert "body" in report["report"]
        vr = json.loads(urlreq.urlopen(f"http://127.0.0.1:{port}/api/command/vr", timeout=8).read().decode())
        assert vr["ok"] is True
        assert vr["desks"]
        assert vr["agents"] is not None
        req = urlreq.Request(
            f"http://127.0.0.1:{port}/api/command/ship",
            data=json.dumps({
                "abhishek_email": "abhishek@example.com",
                "push": False,
                "mail": True,
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        shipped = json.loads(urlreq.urlopen(req, timeout=20).read().decode())
        assert shipped["ok"] is True
        assert shipped["mailto"].startswith("mailto:abhishek@example.com")
    finally:
        httpd.shutdown()
