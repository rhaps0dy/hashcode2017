#!/usr/bin/env python3

import sys
import numpy as np

def intify(line):
    l = line.strip().split()
    return list(int(i) for i in l)

class Problem:
    def __init__(self, videos, endpoints, requests, cache_capacity, n_cache_servers):
        self.video_sizes = videos
        self.endpoints = endpoints
        self.requests = requests
        self.cache_capacity = cache_capacity

        self.caches = list({'videos': set(), 'capacity_left': cache_capacity, 'endpoints': []} for _ in range(n_cache_servers))
        for e in self.endpoints:
            for c_id, c_lat in e['caches'].items():
                self.caches[c_id]['endpoints'].append({'endpoint': e, 'latency': c_lat})

        self.requests_by_video = list([] for _ in range(len(self.video_sizes)))
        for r in self.requests:
            self.requests_by_video[r['video_i']].append(r)

        self.density_matrix = np.zeros((len(self.caches), len(self.video_sizes)))
        self.requests_by_cache_video = {}
        for vid, reqs in enumerate(self.requests_by_video):
            for r in reqs:
                for cache in self.endpoints[r['endpoint_i']]['caches']:
                    t = (cache, vid)
                    if t not in self.requests_by_cache_video:
                        self.requests_by_cache_video[t] = []
                    self.requests_by_cache_video[t].append(r)

    def solve(self):
        for cache in range(self.density_matrix.shape[0]):
            for video in range(self.density_matrix.shape[1]):
                if (cache, video) in self.requests_by_cache_video:
                    self.density_matrix[cache,video] = self.video_density(cache, video)
        while np.any(self.density_matrix):
            aux = [0, 0, 0]
            max_cache = [0, 0, 0]
            max_video = [0, 0, 0]
            max_cache[0], max_video[0] = np.unravel_index(np.argmax(self.density_matrix), self.density_matrix.shape)
            aux[0] = self.density_matrix[max_cache[0], max_video[0]]
            self.density_matrix[max_cache[0], max_video[0]] = 0
            max_cache[1], max_video[1] = np.unravel_index(np.argmax(self.density_matrix), self.density_matrix.shape)
            aux[1] = self.density_matrix[max_cache[1], max_video[1]]
            self.density_matrix[max_cache[1], max_video[1]] = 0
            max_cache[2], max_video[2] = np.unravel_index(np.argmax(self.density_matrix), self.density_matrix.shape)
            aux[2] = self.density_matrix[max_cache[2], max_video[2]]
            self.density_matrix[max_cache[1], max_video[1]] = aux[0]
            self.density_matrix[max_cache[2], max_video[2]] = aux[1]
            aux[0] = self.video_sizes[max_video[0]]*aux[0]
            aux[1] = self.video_sizes[max_video[1]]*aux[1]
            aux[2] = self.video_sizes[max_video[2]]*aux[2]
            sum = aux[0] + aux[1] + aux[2]
            aux[0] /= sum
            aux[1] /= sum
            aux[2] /= sum
            index = np.random.choice(np.arange(0, 3), p=[aux[0], aux[1], aux[2] ])
            max_cache = max_cache[index]
            max_video = max_video[index]
            self.caches[max_cache]['videos'].add(max_video)
            self.caches[max_cache]['capacity_left'] -= self.video_sizes[max_video]

            self.density_matrix[max_cache, max_video] = 0
            to_update, = np.where(self.density_matrix[:, max_video] != 0.0)
            for cache in to_update:
                self.density_matrix[cache, max_video] = self.video_density(cache, max_video)
            to_update, = np.where(self.density_matrix[max_cache, :] != 0.0)
            for video in to_update:
                if self.video_sizes[video] > self.caches[max_cache]['capacity_left']:
                    self.density_matrix[max_cache,video] = 0

    def video_density(self, cache, video):
        video_size = self.video_sizes[video]
        if video_size > self.caches[cache]['capacity_left']:
            return 0.0

        sum_densities = 0
        for r in self.requests_by_cache_video[cache, video]:
            endp = self.endpoints[r['endpoint_i']]
            min_latency = endp['latency']
            for c_id, c_lat in endp['caches'].items():
                if video in self.caches[c_id]['videos']:
                    min_latency = min(min_latency, c_lat)
            current_lat = endp['caches'][cache]
            if current_lat >= min_latency:
                continue
            sum_densities += (min_latency - current_lat) * r['n']

        return sum_densities / video_size

    def print_output(self):
        cs = {}
        for i, c in enumerate(self.caches):
            if len(c['videos']) != 0:
                cs[i] = c['videos']
        print(len(cs))
        for i, c in cs.items():
            print(" ".join(str(a) for a in ([i] + list(c))))

    def calc_score(self):
        print(self.caches)
        for i, c in enumerate(self.caches):
            print("Cache {:d}: sum {:d}".format(i, (sum(self.video_sizes[v] for v in c['videos']))))
        pass

def main():
    #with open('me_at_the_zoo.in', 'r') as f:
    #with open('me_at_the_zoo.in', 'r') as f:
    #with open('kittens.in', 'r') as f:
    with open('me_at_the_zoo.in', 'r') as f:
        ls = f.readlines()
    n_videos, n_ends, n_requests, n_cache_servers, cache_capacity = intify(ls[0])
    videos = intify(ls[1])
    ls = ls[2:]
    endpoints = []
    for e in range(n_ends):
        latency, n_caches = intify(ls[0])
        d = {'latency': latency, 'caches': {}}
        for c in range(n_caches):
            c_id, c_lat = intify(ls[1+c])
            d['caches'][c_id] = c_lat
        endpoints.append(d)
        ls = ls[1+n_caches:]
    requests = []
    for l in ls:
        video, endpoint, n = intify(l)
        requests.append({'video_i': video, 'endpoint_i': endpoint, 'n': n})
    p = Problem(videos, endpoints, requests, cache_capacity, n_cache_servers)
    p.solve()
    p.print_output()
    print("score:", p.calc_score())

if __name__ == '__main__':
    main()
