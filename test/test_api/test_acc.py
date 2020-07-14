
def test_get_acc_detail(sess):
    acc_detail = sess.get_acc_details()
    assert acc_detail.balance > 0
    assert acc_detail.name
    assert acc_detail.id