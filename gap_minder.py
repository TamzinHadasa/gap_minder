# %%
import datetime as dt
import requests
from typing import Any

# %%
NonAutoDict = list[dict[str, str | int]]
HEADERS = {
    'User-Agent': 'edit timing analyzer [pre-alpha]',
    'From': 'wikimedian@tamz.in'
}

# %%
class CombinedContribs(list):
    def get_gaps(self) -> list[tuple[dt.timedelta, int, int]]:
        pairs = [(i, j) for i, j in zip(self, self[1:]) if i['username'] != j['username']]
        print(f"{pairs=}")
        gaps = [(j['timestamp'] - i['timestamp'],
                 i['rev_id'],
                 j['rev_id'])
                for i, j in pairs]
        print(f"{gaps=}")
        gaps.sort(key=lambda x: x[0])
        return gaps

# %%
class UserContribs:
    def __init__(self, username: str, start: str = "", end: str = "", limit: int = 5000):
        query_url = f"https://xtools.wmcloud.org/api/user/nonautomated_edits/en.wikipedia/{username}/all/{start}/{end}?limit={limit}"
        self._data = requests.get(query_url, headers=HEADERS).json()
        self.username = self._data['username']
        self.nonauto: list[dict[str, Any]] = self._data['nonautomated_edits']
        for edit in self.nonauto:
            edit['username'] = self.username
            edit['timestamp'] = dt.datetime.strptime(str(edit['timestamp']), "%Y%m%d%H%M%S")

    def __add__(self, other: 'UserContribs') -> CombinedContribs:
        combined = self.nonauto + other.nonauto
        combined.sort(key=lambda x: x['timestamp'])
        return CombinedContribs(combined)
