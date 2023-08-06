import pickle

PLAYERS_PER_TEAM = 10


class Tick:
    def __init__(self, start):
        self.starts = {}
        self.times = {}
        self.check_collision_time = Averager()
        self.send_message_time = Averager()
        self.send_message_count = 0
        self.shot_count = 0
        self.suspect = False

    def note(self, now, enter, label):
        if enter:
            self.starts[label] = now
        else:
            start = self.starts.pop(label)
            delta = now - start
            if delta > .01 and label != 'nothing':
                self.suspect = True
            if label == 'Shot.check_collision':
                self.check_collision_time.note(delta)
                for key in list(self.starts):
                    key += '+check_collision'
                    self.times[key] = self.times.get(key, 0) + delta
            elif label == 'send message':
                for l, s in list(self.starts.items()):
                    self.starts[l] += delta
                self.send_message_time.note(delta)
            elif label == 'single shot':
                self.shot_count += 1
            else:
                self.times[label] = delta


class Averager:
    def __init__(self):
        self.total = 0
        self.count = 0

    def note(self, value):
        self.total += value
        self.count += 1

    def get(self):
        return self.total / self.count


with open(f'profile-data-{PLAYERS_PER_TEAM}v{PLAYERS_PER_TEAM}.bin', 'rb') as f:
    data = pickle.load(f)

ticks = []
current_tick = None
for now, enter, label in data:
    if (enter, label) == (True, 'start-tick'):
        current_tick = Tick(now)
        ticks.append(current_tick)
    current_tick.note(now, enter, label)


interesting = 'buckets+75', 'buckets+100', 'buckets+125', 'nothing'
times_by_shots = {}
for tick in ticks:
    if tick.suspect:
        print(f'Suspicious tick: {tick.times}')
        continue

    if tick.shot_count not in times_by_shots:
        times_by_shots[tick.shot_count] = tuple(Averager() for i in interesting)
    for i, thing in enumerate(interesting):
        times_by_shots[tick.shot_count][i].note(tick.times[thing])


with open('profile-data.csv', 'w') as f:
    f.write('Active shots,' + ','.join(str(bit) for bit in interesting) + '\n')
    for shot_count, bits in times_by_shots.items():
        f.write(f'{shot_count},' + ','.join(str(a.get()) for a in bits) + '\n')

