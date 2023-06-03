Import-Module .\functions.psm1

function assertActualEqualsExpected {
    Param ($actual, $expected)

    Write-Host ("Comparing: Actual: '{0}', Expected: '{1}'" -f $actual, $expected)

    if ("$actual" -ne "$expected") {
        Write-Error ("Assertion error: Actual: '{0}', Expected: '{1}'" -f $actual, $expected)
    }
}

# clear any state
$stats = $null

# Test output from Doom map
$stats = ParseLevelStats("E1M1 - 0:13.11 (0:13)  K: 3/4  I: 15/37  S: 2/3 ")

$expected = "0:13.11"
assertActualEqualsExpected $stats.Time $expected

$expected = "3/4"
assertActualEqualsExpected $stats.Kills $expected

$expected = "15/37"
assertActualEqualsExpected $stats.Items $expected

$expected = "2/3"
assertActualEqualsExpected $stats.Secrets $expected

$stats = $null

# Test output from Doom 2 map
$stats = ParseLevelStats("MAP01 - 0:07.94 (0:07)  K: 2/9  I: 7/9  S: 2/5 ")

$expected = "0:07.94"
assertActualEqualsExpected $stats.Time $expected

$expected = "2/9"
assertActualEqualsExpected $stats.Kills $expected

$expected = "7/9"
assertActualEqualsExpected $stats.Items $expected

$expected = "2/5"
assertActualEqualsExpected $stats.Secrets $expected

$stats = $null

Write-Host("Tests completed")
