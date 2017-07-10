#!/usr/bin/env python

from __future__ import division
import urllib3

def main():
    http = urllib3.PoolManager()
    r = http.request("GET", "http://dist.neo4j.org/neo4j-community-3.2.2-unix.tar.gz", preload_content=False)
    c_len = int(r.getheader("Content-Length"))
    pc = c_len // 100
    progress = 0
    for chunk in r.stream(pc):
        progress += len(chunk)
        print("\r{:.01f}%".format(progress * 100.0 / c_len), end="")
    r.release_conn()


if __name__ == "__main__":
    main()

