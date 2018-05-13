from subprocess import run, PIPE, STDOUT
from collections import namedtuple

import pytest

TEST_DIRECTORY = 'tests/cli/data'

CliTestRecord = namedtuple("CliTestRecord", ["input", "output"])


def generate_cases(source_file):
    input = ""
    output = ""
    cases = []
    with open(source_file, 'r') as fd:
        for line in fd:
            if line.startswith("$ "):
                if input:
                    cases.append(CliTestRecord(input, output))
                    input = output = ""
                input = line[2:].strip()
            else:
                output += line

    if input:
        cases.append(CliTestRecord(input, output))
    return cases


basic_cases = generate_cases('tests/cli/data/download.txt')


def run_bash(input):
    return run(["bash"], stdout=PIPE, stderr=STDOUT, input=input,
               universal_newlines=True)


@pytest.mark.parametrize("input,output", basic_cases)
def test_cli_basic(input, output):
    p = run_bash(input)
    assert p.stdout == output
