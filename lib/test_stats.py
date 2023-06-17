#!/usr/bin/env python
from stats import *

input1 = "E1M1 - 0:09.80 (0:09)  K: 2/2  I: 2/7  S: 1/1"
input2 = "MAP03 - 0:22.17 (0:22)  K: 2/2  I: 6/7  S: 1/1"
input3 = "E1M1 - 0:02.06 (0:02)  K: 0/2  I: 0/7  S: 0/1"

actual1 = ParseLevelStats(input1)
actual2 = ParseLevelStats(input2)
actual3 = ParseLevelStats(input3)

assert actual1["Time"] == "0:09.80", f"Time was {actual1['Time']}"
assert actual1["Kills"] == "2/2", f"Kills was {actual1['Kills']}"
assert actual1["Items"] == "2/7", f"Items was {actual1['Items']}"
assert actual1["Secrets"] == "1/1", f"Secrets was {actual1['Secrets']}"
