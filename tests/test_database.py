import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
from model.database import VaultDB

TEST_DB = "test_vault.db"


def setup():
    import model.database as db_module
    db_module.DB_FILE = TEST_DB


def teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_add_and_get():
    setup()
    db = VaultDB()
    db.add_credential("github.com", "tom", "MySecret123", "personal account")
    db.add_credential("google.com", "tom@gmail.com", "Pass456!")
    creds = db.get_all_credentials()
    assert len(creds) == 2
    assert creds[0].site == "github.com"
    assert creds[0].password == "MySecret123"
    assert creds[1].site == "google.com"
    assert creds[1].password == "Pass456!"
    db.close()
    print("test_add_and_get ✔")


def test_search():
    setup()
    db = VaultDB()
    db.add_credential("github.com", "tom", "pass1")
    db.add_credential("google.com", "tom", "pass2")
    db.add_credential("amazon.com", "john", "pass3")
    results = db.search_credentials("git")
    assert len(results) == 1
    assert results[0].site == "github.com"
    db.close()
    print("test_search ✔")


def test_password_is_encrypted():
    setup()
    db = VaultDB()
    db.add_credential("test.com", "user", "PlainPassword")
    raw = db.connection.execute(
        "SELECT password_encrypted FROM credentials WHERE site='test.com'"
    ).fetchone()[0]
    assert raw != "PlainPassword", "Password should be encrypted in DB!"
    db.close()
    print("test_password_is_encrypted ✔")


if __name__ == "__main__":
    teardown()
    test_add_and_get()
    teardown()
    test_search()
    teardown()
    test_password_is_encrypted()
    teardown()
    print("\nAll tests passed ✔")
