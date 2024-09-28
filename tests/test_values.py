import pytest
import pyparsing as pp
from crucible.parser.values import (
    label, boolean,  number, boolean, hex, string,
    labled_address, number_with_sci, value, array,
    struct
)

ParseException = pp.exceptions.ParseException


def test_label():
    label.parse_string("_test")
    label.parse_string("Test23")
    label.parse_string("rest23")
    label.parse_string("rest23_")
    label.parse_string("USD₮")

    with pytest.raises(ParseException):
        label.parse_string("012312")
    with pytest.raises(ParseException):
        label.parse_string("^asavx12")


def test_number_zero():
    val = number.parse_string("0")
    val.get_name() == "number"
    assert val.number == 0


def test_boolean():
    assert boolean.parse_string("true")[0] == True
    assert boolean.parse_string("false")[0] == False

    with pytest.raises(ParseException):
        boolean.parse_string("not-bool")


def test_number():
    assert number.parse_string("24")[0] == 24
    assert number.parse_string("1e3")[0] == 1000


def test_bytes():
    addr = hex.parse_string("0x434563B0604BE100F04B7Ae485BcafE3c9D8850E")
    assert addr.get_name() == "address"
    assert addr[0] == "0x434563B0604BE100F04B7Ae485BcafE3c9D8850E"

    b4 = hex.parse_string("0x434563B0")
    assert b4.get_name() == "bytes4"
    b4[0] == "0x434563B0"

    b8 = hex.parse_string("0x434563B0434563B0")
    assert b8.get_name() == "bytes8"
    b8[0] == "0x434563B0434563B0"

    b16 = hex.parse_string("0x434563B0434563B0434563B0434563B0")
    assert b16.get_name() == "bytes16"
    b16[0] == "0x434563B0434563B0434563B0434563B0"

    b32 = hex.parse_string(
        "0x434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0")
    assert b32.get_name() == "bytes32"
    b32[0] == "0x434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0"

    b_arb0 = hex.parse_string(
        "0x434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0" +
        "434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0"
    )
    assert b_arb0.get_name() == "bytes"
    assert b_arb0[0] == "0x434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0" + \
        "434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0434563B0"

    b_arb1 = hex.parse_string(
        "0x434563B04345"
    )
    assert b_arb1.get_name() == "bytes"
    assert b_arb1[0] == "0x434563B04345"


def test_string():
    str0 = string.parse_string('"hello"')
    assert (str0.get_name() == "string")
    assert str0[0] == "hello"


def test_labeled_address():
    la = labled_address.parse_string(
        "Broker: [0x434563B0604BE100F04B7Ae485BcafE3c9D8850E]")
    assert la.label == "Broker"
    assert la.address == "0x434563B0604BE100F04B7Ae485BcafE3c9D8850E"


def test_number_with_sci():
    nws = number_with_sci.parse_string("123 [1e23]")
    assert nws.number == 123


struct_array_fixture = "[Exchange({ exchangeId:0x3135b662c38265d0655177091f1b647b4fef511103d06c016efdf18b46930d2c, assets: [0x765DE816845861e75A25fCA122bb6898B8B1282a, 0x471EcE3750Da237f93B8E339c536989b8978a438] }), Exchange({ exchangeId: 0xb73ffc6b5123de3c8e460490543ab93a3be7d70824f1666343df49e219199b8c, assets: [0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73, 0x471EcE3750Da237f93B8E339c536989b8978a438] }), Exchange({ exchangeId: 0xed0528e42b9ecae538aab34b93813e08de03f8ac4a894b277ef193e67275bbae, assets: [0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787, 0x471EcE3750Da237f93B8E339c536989b8978a438] }), Exchange({ exchangeId: 0xe8693b17c0f002f6a2fe839525557cef10dfeacef9e16c9bbdcb01c57933ce58, assets: [0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787, 0xcebA9300f2b948710d2653dD7B07f33A8B32118C] }), Exchange({ exchangeId: 0xf418803158d881fda22694067bf6479476cec22ecfeeca2f6a65a6259bdbb9c0, assets: [0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73, 0xEB466342C4d449BC9f53A865D5Cb90586f405215] }), Exchange({ exchangeId: 0x40c8472edd23f2976b0503db2692e8f06f0eb52db690e84697cad36a6b44e2df, assets: [0xe8537a3d056DA446677B9E9d6c5dB704EaAb4787, 0xEB466342C4d449BC9f53A865D5Cb90586f405215] }), Exchange({ exchangeId: 0xfca6d94b46122eb9a4b86cf9d3e1e856fea8a826d0fc26c5baf17c43fbaf0f48, assets: [0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73, 0x061cc5a2C863E0C1Cb404006D559dB18A34C762d] }), Exchange({ exchangeId: 0x269dcbdbc07fff1a4aaab9c7c03b3f629cd9bbed49aa0efebab874e4da1ffd07, assets: [0x73F93dcc49cB8A239e2032663e9475dd5ef29A08, 0x471EcE3750Da237f93B8E339c536989b8978a438] }), Exchange({ exchangeId: 0xcc68743c58a31c4ec3c56bca3d579409b4e2424e5f37e54a85f917b22af74e7c, assets: [0x73F93dcc49cB8A239e2032663e9475dd5ef29A08, 0x061cc5a2C863E0C1Cb404006D559dB18A34C762d] }), Exchange({ exchangeId: 0x89de88b8eb790de26f4649f543cb6893d93635c728ac857f0926e842fb0d298b, assets: [0x765DE816845861e75A25fCA122bb6898B8B1282a, 0x456a3D042C0DbD3db53D5489e98dFb038553B0d0] }), Exchange({ exchangeId: 0x99be8b8341ba00914600cda701568ab27eea9aca7a32fa48c26e07b86841020c, assets: [0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73, 0xcebA9300f2b948710d2653dD7B07f33A8B32118C] }), Exchange({ exchangeId: 0xacc988382b66ee5456086643dcfd9a5ca43dd8f428f6ef22503d8b8013bcffd7, assets: [0x765DE816845861e75A25fCA122bb6898B8B1282a, 0xcebA9300f2b948710d2653dD7B07f33A8B32118C] }), Exchange({ exchangeId: 0x0d739efbfc30f303e8d1976c213b4040850d1af40f174f4169b846f6fd3d2f20, assets: [0x765DE816845861e75A25fCA122bb6898B8B1282a, 0xEB466342C4d449BC9f53A865D5Cb90586f405215] }), Exchange({ exchangeId: 0x773bcec109cee923b5e04706044fd9d6a5121b1a6a4c059c36fdbe5b845d4e9b, assets: [0x765DE816845861e75A25fCA122bb6898B8B1282a, 0x48065fbBE25f71C9282ddf5e1cD6D6A887483D5e] })]"


def test_array():
    empty_array = array.parse_string("[]")
    assert empty_array.get_name() == "array"
    assert len(empty_array.array) == 0

    array_of_addr = array.parse_string(
        "[0x434563B0604BE100F04B7Ae485BcafE3c9D8850E, 0x134563B0604BE100F04B7Ae485BcafE3c9D8850E]")
    assert array_of_addr.get_name() == "array"
    assert (len(array_of_addr.array)) == 2

    assert "address" in array_of_addr.array[0]
    assert array_of_addr.array[0]["address"] == "0x434563B0604BE100F04B7Ae485BcafE3c9D8850E"


def test_struct_array():
    struct_array = array.parse_string(struct_array_fixture)
    assert struct_array.get_name() == "array"
    assert len(struct_array.array) == 14
    assert struct_array[1].struct == 'Exchange'


def test_nested_array():
    nested_array = array.parse_string(
        "[[ 0x434563B0604BE100F04B7Ae485BcafE3c9D8850E ], [ 12 ]]")
    assert nested_array.get_name() == "array"
    assert len(nested_array.array) == 2
    assert len(nested_array.array[0].array) == 1
    assert "address" in nested_array[0][0]
    assert nested_array[0][0]["address"] == "0x434563B0604BE100F04B7Ae485BcafE3c9D8850E"
