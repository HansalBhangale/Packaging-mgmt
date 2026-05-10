"""
database.py  –  MongoDB Atlas data-access layer
All public methods are non-blocking: they spin up a daemon thread and
call back on the worker thread.  UI code must forward results back to
the main thread via  Clock.schedule_once().
"""

import re
import threading
import certifi
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from bson import ObjectId

# ─────────────────────────────────────────────────────────────────────────────
# ↓↓  REPLACE THIS WITH YOUR MONGODB ATLAS CONNECTION STRING  ↓↓
MONGO_URI = (
    "mongodb+srv://bhangalehansal:1234@packaging-mgmt.ppbb7gy.mongodb.net/?appName=Packaging-mgmt"
)
DB_NAME = "packaging_db"
# ─────────────────────────────────────────────────────────────────────────────


class Database:
    """
    Singleton wrapper around MongoClient.
    Usage:
        db = Database.get()
        db.connect_async(on_success=..., on_error=...)
    """

    _instance = None
    _lock = threading.Lock()

    # ── Singleton ──────────────────────────────────────────────────────────

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._client = None
                inst._db = None
                inst._connected = False
                cls._instance = inst
        return cls._instance

    @classmethod
    def get(cls):
        return cls()

    # ── Connection ─────────────────────────────────────────────────────────

    def connect_async(self, on_success=None, on_error=None):
        """Connect to Atlas in a background thread."""
        def _worker():
            try:
                client = MongoClient(
                    MONGO_URI,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=15000,
                    connectTimeoutMS=15000,
                    socketTimeoutMS=20000,
                    heartbeatFrequencyMS=10000,   # reduce heartbeat noise
                    retryWrites=True,
                )
                client.admin.command("ping")
                self._client = client
                self._db = client[DB_NAME]
                self._connected = True

                # Indexes for fast search
                self._db.items.create_index(
                    [("item_name", ASCENDING)], background=True
                )
                self._db.cartons.create_index(
                    [("carton_id", ASCENDING)], unique=True, background=True
                )
                if on_success:
                    on_success()
            except ServerSelectionTimeoutError:
                if on_error:
                    on_error("Cannot reach MongoDB Atlas. Check your internet "
                             "connection and Atlas IP whitelist (0.0.0.0/0).")
            except Exception as exc:
                if on_error:
                    on_error(str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def is_connected(self):
        return self._connected

    # ── Items: READ ────────────────────────────────────────────────────────

    def search_items(self, query: str, callback):
        """
        Case-insensitive fuzzy search on item_name.
        callback(results: list[dict], error: str | None)
        Each result: {_id, item_name, carton_id, location}
        """
        def _worker():
            try:
                escaped = re.escape(query.strip())
                pattern = re.compile(escaped, re.IGNORECASE)
                pipeline = [
                    {"$match": {"item_name": {"$regex": pattern}}},
                    {
                        "$lookup": {
                            "from": "cartons",
                            "localField": "carton_id",
                            "foreignField": "carton_id",
                            "as": "carton_info",
                        }
                    },
                    {
                        "$unwind": {
                            "path": "$carton_info",
                            "preserveNullAndEmptyArrays": True,
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "item_name": 1,
                            "carton_id": 1,
                            "location": {
                                "$ifNull": ["$carton_info.location", "—"]
                            },
                        }
                    },
                    {"$sort": {"item_name": 1}},
                ]
                results = list(self._db.items.aggregate(pipeline))
                callback(results, None)
            except Exception as exc:
                callback([], str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def get_all_items(self, callback):
        """Return ALL items joined with carton location, sorted a-z."""
        def _worker():
            try:
                pipeline = [
                    {
                        "$lookup": {
                            "from": "cartons",
                            "localField": "carton_id",
                            "foreignField": "carton_id",
                            "as": "carton_info",
                        }
                    },
                    {
                        "$unwind": {
                            "path": "$carton_info",
                            "preserveNullAndEmptyArrays": True,
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "item_name": 1,
                            "carton_id": 1,
                            "location": {
                                "$ifNull": ["$carton_info.location", "—"]
                            },
                        }
                    },
                    {"$sort": {"item_name": 1}},
                ]
                results = list(self._db.items.aggregate(pipeline))
                callback(results, None)
            except Exception as exc:
                callback([], str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Items: WRITE ───────────────────────────────────────────────────────

    def add_item(self, item_name: str, carton_id: str, callback):
        """callback(inserted_id: str | None, error: str | None)"""
        def _worker():
            try:
                doc = {
                    "item_name": item_name.strip(),
                    "carton_id": carton_id.strip(),
                }
                result = self._db.items.insert_one(doc)
                callback(str(result.inserted_id), None)
            except Exception as exc:
                callback(None, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def update_item(self, item_id: str, item_name: str, carton_id: str, callback):
        """callback(success: bool, error: str | None)"""
        def _worker():
            try:
                self._db.items.update_one(
                    {"_id": ObjectId(item_id)},
                    {"$set": {
                        "item_name": item_name.strip(),
                        "carton_id": carton_id.strip(),
                    }},
                )
                callback(True, None)
            except Exception as exc:
                callback(False, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def delete_item(self, item_id: str, callback):
        """callback(success: bool, error: str | None)"""
        def _worker():
            try:
                self._db.items.delete_one({"_id": ObjectId(item_id)})
                callback(True, None)
            except Exception as exc:
                callback(False, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Cartons: READ ──────────────────────────────────────────────────────

    def get_all_cartons(self, callback):
        """callback(cartons: list[dict], error: str | None)"""
        def _worker():
            try:
                results = list(
                    self._db.cartons.find(
                        {}, {"_id": 1, "carton_id": 1, "location": 1}
                    ).sort("carton_id", ASCENDING)
                )
                callback(results, None)
            except Exception as exc:
                callback([], str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Cartons: WRITE ─────────────────────────────────────────────────────

    def add_carton(self, carton_id: str, location: str, callback):
        """callback(inserted_id: str | None, error: str | None)"""
        def _worker():
            try:
                doc = {
                    "carton_id": carton_id.strip(),
                    "location": location.strip(),
                }
                result = self._db.cartons.insert_one(doc)
                callback(str(result.inserted_id), None)
            except DuplicateKeyError:
                callback(None, f"Carton ID '{carton_id}' already exists.")
            except Exception as exc:
                callback(None, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def update_carton(self, carton_id: str, location: str, callback):
        """callback(success: bool, error: str | None)"""
        def _worker():
            try:
                self._db.cartons.update_one(
                    {"carton_id": carton_id},
                    {"$set": {"location": location.strip()}},
                )
                callback(True, None)
            except Exception as exc:
                callback(False, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def delete_carton(self, carton_id: str, callback):
        """
        Deletes the carton AND all items that reference it.
        callback(success: bool, error: str | None)
        """
        def _worker():
            try:
                self._db.cartons.delete_one({"carton_id": carton_id})
                self._db.items.delete_many({"carton_id": carton_id})
                callback(True, None)
            except Exception as exc:
                callback(False, str(exc))

        threading.Thread(target=_worker, daemon=True).start()