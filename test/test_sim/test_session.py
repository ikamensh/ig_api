import pytest

from api.sim.sim_session import SimSession

import markets

def test_cycle_costs(server):
    s = SimSession(server)
    balance = s.get_acc_details().balance

    pos  = s.open_position(10, markets.vix.code)
    s.close_position(pos)

    assert balance > s.get_acc_details().balance
