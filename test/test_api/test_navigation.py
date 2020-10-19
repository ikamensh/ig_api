def test_root(ig_session):
    """Verifies that navigation can retrieve the root of the markets. """
    ids, epics = ig_session.market_navigation()
    assert ids


def test_get_positions(ig_session):
    """Tests that returned node ids can be used for further navigation. """
    ids, epics = ig_session.market_navigation()
    assert ids

    nxt = ids[0]
    ids, epics = ig_session.market_navigation(nxt)
    assert ids or epics

def test_gets_to_market(ig_session):
    """Tests that returned node ids can be used for further navigation. """
    ids, epics = ig_session.market_navigation()
    while ids:
        nxt = ids[0]
        ids, epics = ig_session.market_navigation(nxt)

    epic = epics[0]
    snap, instr = ig_session.market(epic)
    