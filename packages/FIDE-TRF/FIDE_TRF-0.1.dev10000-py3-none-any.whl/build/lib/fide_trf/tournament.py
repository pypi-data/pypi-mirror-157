from operator import attrgetter

from fide_trf import Player


class Tournament:

    def __init__(self, filename=None):
        self.players = []

        if filename is not None:
            self.scan_filename(filename)

    def scan_filename(self, filename):
        self.lines = []
        with open(filename) as trf:
            for line in trf.readlines():
                line_ = line.rstrip()
                if line_[:3] == '001':
                    self.players.append(Player(raw_string=line_[4:]))
                else:
                    self.lines.append({'code': line_[:3], 'data': line_[4:]})

    def compute_rankings(self):
        return sorted(self.players, key=attrgetter('score'), reverse=True)

    def update_rankings(self):
        sorted_players = self.compute_rankings()
        for player in self.players:
            new_rank = sorted_players.index(player) + 1
            player.update_rank(new_rank)

    def __str__(self):
        return (('\n'.join(f'{d["code"]} {d["data"]}' for d in self.lines))
                + '\n' +
                ('\n'.join(f'001 {p}' for p in self.players)))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'name={self.lines[0]["data"]!r}, city={self.lines[1]["data"]!r},'
            f' fed={self.lines[2]["data"]!r}, date={self.lines[3]["data"]!r}'
            ')'
        )
