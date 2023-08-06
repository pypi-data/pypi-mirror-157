from src.vyze import parse_space_token


def test_parse_space_token__1():
    token = parse_space_token('7e2a3bf22657aa37be2daa8868804d029966325641df7015831e85bf82ef0abbffffff010000000000000000eb5ae463000000001ca29c4747cb1ca50c3e4d2cd016053b91c6a7fb')
    assert token.user_id == '7e2a3bf22657aa37be2daa8868804d02'
    assert token.space_id == '9966325641df7015831e85bf82ef0abb'
    assert token.permissions[0] == 33554431
    assert token.permissions[1] == 0
    assert token.permissions[2] == 0
    assert token.expires.timestamp() == 1675909867
    assert token.token == '7e2a3bf22657aa37be2daa8868804d029966325641df7015831e85bf82ef0abbffffff010000000000000000eb5ae463000000001ca29c4747cb1ca50c3e4d2cd016053b91c6a7fb'
