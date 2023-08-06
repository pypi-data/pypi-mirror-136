from typing import List

class CaajJournal:
  def __init__(self, caaj: List):
    self.caaj = caaj

  def get_caaj(self) -> List:
    return self.caaj

  @classmethod
  def get_caaj_meta(cls, time:str, transaction_id:str, comment:str) -> dict:
    return {
      "time": time,
      "transaction_id": transaction_id,
      "comment": comment  
     }  

  @classmethod
  def get_caaj_destination(cls, debit_from:str, debit_to:str, credit_from:str, credit_to:str) -> dict:
    return {
      "debit_from": debit_from,
      "debit_to": debit_to,
      "credit_from": credit_from,
      "credit_to": credit_to
    }  

  @classmethod
  def get_caaj_value(cls, debit_title:str, debit_amount:dict, credit_title:str, credit_amount:dict) -> dict:
    return {  
      "debit_title": debit_title,
      "debit_amount": debit_amount,
      "credit_title": credit_title,
      "credit_amount": credit_amount
    }  