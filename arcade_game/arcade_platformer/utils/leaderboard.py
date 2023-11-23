import pickle
import bisect

class Leaderboard():

    def __init__(self):
        self.leaderboard = []
        self.leaderfile = './leaderboard.dat'
        self.read_scores()

    def read_scores(self):
        try:
            with open(self.leaderfile, 'rb') as f:
                self.leaderboard = pickle.load(f)
            self.leaderboard.sort(key = lambda json: json['score'], reverse=True)
        except FileNotFoundError:
            # first time running, no leaderboard file
            pass
        
    def dump_scores(self):
        print('Leaderboard:')
        self.leaderboard.sort(key = lambda json: json['score'], reverse=True)
        i = 1
        for item in self.leaderboard:
            print('%02d %s -> %s' % (i, item['score'], item['name']))
            i += 1

    def add_score(self, name, score):
        self.leaderboard.append({'name': name, 'score': score})
        self.leaderboard.sort(key = lambda json: json['score'], reverse=True)
        if len(self.leaderboard) > 10:
            self.leaderboard.pop()

        #bisect.insort(self.leaderboard, (score, name), key=lambda x: x[0])
        #self.leaderboard.reverse()

    def save(self):
        with open(self.leaderfile, 'wb+') as f:
            pickle.dump(self.leaderboard, f)
