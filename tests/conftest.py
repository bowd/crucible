import pytest
import os

fixtures = os.listdir('./fixtures')

for fixture in fixtures:
    fixture_name = fixture.split('.')[0]
    exec(
        f"""
@pytest.fixture
def {fixture_name}():
    with open(f"./fixtures/{fixture}", "r") as f:
        return f.read()
"""
    )
