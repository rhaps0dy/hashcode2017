#!/usr/bin/env python3

import sys

def intify(line):
    l = line.strip().split()
    return list(int(i) for i in l)

def main():
    with open(sys.argv[1], 'r') as f:
        ls = f.readlines()
    _, n_ends, _, _, cache_capacity = intify(ls[0])
    videos = intify(ls[1])
    ls = ls[2:]
    endpoints = []
    for e in range(n_ends):
        latency, n_caches = intify(ls[0])
        d = {'latency': latency, 'caches': []}
        for c in range(n_caches):
            d['caches'].append(tuple(intify(ls[1+c])))
        endpoints.append(d)
        ls = ls[1+n_caches:]
    requests = []
    for l in ls:
        video, endpoint, n = intify(l)
        requests.append({'video': video, 'endpoint': endpoint, 'n': n})
    del ls
    print(videos, endpoints, requests, cache_capacity)

if __name__ == '__main__':
    main()
