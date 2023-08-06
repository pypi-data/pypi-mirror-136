# TODO : MOVE THIS IN dfysetters/

import gspread
from dfysetters.roles import Roles

gc = gspread.oauth(
    credentials_filename="/Users/louisrae/Documents/team_scripts/credentials/credentials.json",
    authorized_user_filename="/Users/louisrae/Documents/team_scripts/credentials/authorized_user.json",
)

LEVEL_10_SHEET = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1Y7cQYW1MJ1HstJVJEADVqKgbI-bOMyv74159jOJQtc4/edit#gid=1480274768"
).sheet1

SPECIALIST_NAME = "Tylee Evans Groll"

MESSAGE_DATA_SHEET = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1IfZlLzzwkC05I6fv-4ZRNFOc7ul7k0qIfeG-bk9j6AA/edit#gid=81738738"
).sheet1

SCHEDULE_ONCE_HEADERS = {
    "Accept": "application/json",
    "API-Key": "d7459f78d474f09276b4d708d2f2a161",
}

SCHEDULE_ONCE_URL = (
    "https://api.oncehub.com/v2/bookings?expand=booking_page&limit=100"
)

Roles().register_all_members()
ROLE_DICTIONARY = Roles().all_roles
