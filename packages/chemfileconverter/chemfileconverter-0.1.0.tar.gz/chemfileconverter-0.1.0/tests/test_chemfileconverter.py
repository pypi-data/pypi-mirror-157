import json

from chemfileconverter import load
from chemfileconverter.cli import main


def test_main():
    main([])


def test_simple_rxn_load():
    with open('tests/data/test_simple.rxn', 'r') as simple_rxn:
        chem_json = load(simple_rxn)
    with open('tests/data/test_simple.json', 'r') as simple_json:
        json_result = json.load(simple_json)

    assert chem_json == json_result


def test_simple_rxn_long_load():
    with open('tests/data/test_simple_long_aam.rxn', 'r') as simple_rxn:
        chem_json = load(simple_rxn)
    with open('tests/data/test_simple_long_aam.json', 'r') as simple_json:
        json_result = json.load(simple_json)

    assert chem_json == json_result
