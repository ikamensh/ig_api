from ig_api.sim.sim_session import SimSession

from ig_api import markets

def test_cycle_costs(server):
    s = SimSession(server)
    balance = s.get_acc_details().balance

    pos  = s.open_position(markets.vix.code, 10)
    s.close_position(pos)

    assert balance > s.get_acc_details().balance
