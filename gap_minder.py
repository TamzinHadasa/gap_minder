import datetime as dt
from collections import UserList
from typing import Any, Iterable, Literal, TypedDict

import requests

import config


class Data(TypedDict):
    project: str
    username: str
    namespace: int | Literal['all']
    limit: int
    nonautomated_edits: 'ContribList'


class Contrib(TypedDict):
    full_page_title: str
    page_title: str
    namespace: int
    rev_id: int
    timestamp: dt.datetime
    minor: int
    length: int
    length_change: int
    comment: str
    username: str


ContribList = list[Contrib]
HEADERS = {
    'User-Agent': 'gap_minder.py edit timing analyzer [alpha]',
    'From': config.FROM
}
API_PATH = "https://xtools.wmcloud.org/api/user/nonautomated_edits/en.wikipedia"


class Contribs(UserList):

    @classmethod
    def new_nonauto(cls, username: str, start: str = "", end: str = "", limit: int = 5000):
        query_url = f"{API_PATH}/{username}/all/{start}/{end}?limit={limit}"
        print("Querying XTools API...")
        data: Data = requests.get(query_url, headers=HEADERS, timeout=90).json()
        nonauto: ContribList = [
            (edit | {'username': username,  # type: ignore
                     'timestamp': dt.datetime.strptime(str(edit['timestamp']), "%Y%m%d%H%M%S")})
            for edit in data['nonautomated_edits']
        ]
        obj = Contribs(nonauto)
        return obj

    def __add__(self, other: Iterable[Any]) -> 'Contribs':
        try:
            obj = Contribs(self.data + other.data)  # type: ignore
        except AttributeError as e:
            raise NotImplementedError from e
        try:
            obj.sort(key=lambda x: x['timestamp'])
        except KeyError as e:
            raise NotImplementedError from e
        return obj

    def get_gaps(self) -> list[tuple[dt.timedelta, int, int]]:
        pairs = [(i, j) for i, j in zip(self, self[1:]) if i['username'] != j['username']]
        gaps = [(j['timestamp'] - i['timestamp'],
                 i['rev_id'],
                 j['rev_id'])
                for i, j in pairs]
        gaps.sort(key=lambda x: x[0])
        return gaps


def main():
    user1 = Contribs.new_nonauto(input("User 1? "))
    user2 = Contribs.new_nonauto(input("User 2? "))
    combined = user1 + user2
    print(combined.get_gaps())


if __name__ == "__main__":
    main()
