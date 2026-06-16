# User Profile DAO.
#
# Used to persist the following information about the user in the
# agent's long-term memory:
# 1. Name
# 2. Profession
# 3. Favorite programming language

import sqlite3
from typing import Any, TypedDict, cast

class UserProfile(TypedDict):
    user_id: str
    full_name: str
    profession: str
    favorite_language: str

class UserProfileDAO:

    def __init__(self, file_name: str) -> None:
        self.__file_name = file_name

        with sqlite3.connect(self.__file_name) as db_connection:
            cursor: sqlite3.Cursor = db_connection.cursor()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS user_profiles(
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT,
                    profession TEXT,
                    favorite_language TEXT
                )"""
            )
            db_connection.commit()

    def load_user_profile(self, user_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.__file_name) as db_connection:
            cursor: sqlite3.Cursor = db_connection.cursor()

            _ = cursor.execute(
                """SELECT user_id, full_name, profession, favorite_language
                    FROM user_profiles
                    WHERE user_id = ?""",
                [user_id]
            )
            row = cursor.fetchone()

            if row:
                return {
                    "user_id": row[0],
                    "full_name": row[1],
                    "profession": row[2],
                    "favorite_language": row[3]
                }
            else:
                return None

    def save_user_profile(self, user_profile: UserProfile) -> None:
        with sqlite3.connect(self.__file_name) as db_connection:
            cursor: sqlite3.Cursor = db_connection.cursor()

            _ = cursor.execute(
                """INSERT OR REPLACE INTO user_profiles(user_id, full_name, profession, favorite_language)
                    VALUES(?, ?, ?, ?)""",
                (
                    user_profile["user_id"],
                    user_profile["full_name"],
                    user_profile["profession"],
                    user_profile["favorite_language"]
                )
            )
            db_connection.commit()

# Test cases for class UserProfileDAO
def main() -> None:
    # Instantiate the DAO first
    user_profile_dao: UserProfileDAO = UserProfileDAO("user_profiles.sqlite")

    # Let's persist user_profile_1 to DB
    user_profile_1: UserProfile = UserProfile(
        user_id="1",
        full_name="Amit Batra",
        profession="Software Architect",
        favorite_language="Python"
    )
    user_profile_dao.save_user_profile(user_profile_1)

    # Let's persist user_profile_2 to DB
    user_profile_2: UserProfile = UserProfile(
        user_id="2",
        full_name="Rahul Batra",
        profession="Software Architect",
        favorite_language="PHP"
    )
    user_profile_dao.save_user_profile(user_profile_2)

    # Let's retrieve user_profile_1 from DB
    user_profile_3: UserProfile = cast(UserProfile, user_profile_dao.load_user_profile("1"))
    print(f"Retrieved from DB: {user_profile_3}")

    # Overwrite the user_profile_1 in the DB
    user_profile_4: UserProfile = UserProfile(
        user_id="1",
        full_name="Sumit Batra",
        profession="Software Engineer",
        favorite_language="Java"
    )
    user_profile_dao.save_user_profile(user_profile_4)

    # Now again retrieve user_profile_1 from DB
    user_profile_5: UserProfile = cast(UserProfile, user_profile_dao.load_user_profile("1"))
    print(f"Retrieved from DB: {user_profile_5}")

if __name__ == "__main__":
    main()