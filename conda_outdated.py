"""
MIT License
Copyright (c) 2019 Abraham Hinteregger
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
import subprocess
from collections import defaultdict
from itertools import chain


def get_versions(lines):
    ddict = defaultdict(set)
    for line in lines.splitlines()[2:]:
        pkg, version = re.match(r"^(\S+)\s+(\S+)", line, re.MULTILINE).groups()
        ddict[pkg].add(version)
    return ddict


def semantic_cmp(version_string):
    def mysplit(string):
        version_substrs = lambda x: re.findall(r"([A-z]+|\d+)", x)  # noqa: E731
        return list(chain(map(version_substrs, string.split("."))))

    def str_ord(string):
        num = 0
        for char in string:
            num *= 255
            num += ord(char)
        return num

    def try_int(version_str):
        try:
            return int(version_str)
        except ValueError:
            return str_ord(version_str)

    mss = list(chain(*mysplit(version_string)))
    return tuple(map(try_int, mss))


def main():
    sp_i = subprocess.run(["conda", "list"], stdout=subprocess.PIPE)
    sp_v = subprocess.run(["conda", "search", "--outdated"], stdout=subprocess.PIPE)
    installed = get_versions(sp_i.stdout.decode("utf-8"))
    available = get_versions(sp_v.stdout.decode("utf-8"))
    for pkg, inst_vs in installed.items():
        avail_vs = sorted(list(available[pkg]), key=semantic_cmp)
        if not avail_vs:
            continue
        current = min(inst_vs, key=semantic_cmp)
        newest = avail_vs[-1]
        if avail_vs and current != newest:
            if semantic_cmp(current) < semantic_cmp(newest):
                print(f"{pkg}:\n\tInstalled:\t{current}\n\tNewest:\t\t{newest}")
                new = [x for x in avail_vs if semantic_cmp(current) < semantic_cmp(x)]
                print("\tNewer:\t\t" + f", ".join(new))


if __name__ == "__main__":
    main()