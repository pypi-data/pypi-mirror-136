import unittest
from senkalib.caaj_journal import CaajJournal

class TestCaajJounal(unittest.TestCase):
  def test_get_caaj_meta(self):
    caaj_meta = CaajJournal.get_caaj_meta('2022-01-12 11:11:11', '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6', 'hello world')
    assert caaj_meta['time'] == '2022-01-12 11:11:11'
    assert caaj_meta['transaction_id'] == '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6'
    assert caaj_meta['comment'] == 'hello world'

  def test_get_caaj_destination(self):
    caaj_destination = CaajJournal.get_caaj_destination(
      '0x111111111111111111111', 
      '0x222222222222222222222', 
      '0x333333333333333333333', 
      '0x444444444444444444444')
    assert caaj_destination['debit_from'] == '0x111111111111111111111'
    assert caaj_destination['debit_to'] == '0x222222222222222222222'
    assert caaj_destination['credit_from'] == '0x333333333333333333333'
    assert caaj_destination['credit_to'] == '0x444444444444444444444'

  def test_get_caaj_value(self):
    caaj_value = CaajJournal.get_caaj_value('LEND', {'USDT': '1000'}, 'SPOT', {'USDT': '1000'})
    assert caaj_value['debit_title'] == 'LEND'
    assert caaj_value['debit_amount'] == {'USDT': '1000'}
    assert caaj_value['credit_title'] == 'SPOT'
    assert caaj_value['credit_amount'] == {'USDT': '1000'}

if __name__ == '__main__':
  unittest.main()