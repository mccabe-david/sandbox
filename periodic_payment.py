# This example is provided for informational purposes only and has not been audited for security.
# periodic_payment.py
# Adapted by David McCabe
# on 6/15/2021


from pyteal import *

"""Periodic Payment"""

tmpl_fee = Int(1000)
tmpl_period = Int(100)
tmpl_dur = Int(100)
tmpl_lease = Bytes("base64", "JC9xn+dcbJreefCH9kKcGxj1QONGiyRDKfE4FM52yhc=")
tmpl_amt = Int(1500)
tmpl_rcv = Addr("CK56G4VABSB6H7PYYWTEPCYLSY6M7AWKSXDFVHTTLDMLYJ57RC5U7PM5TA")
tmpl_timeout = Int(14850000)

def periodic_payment(tmpl_fee=tmpl_fee,
                     tmpl_period=tmpl_period,
                     tmpl_dur=tmpl_dur,
                     tmpl_lease=tmpl_lease,
                     tmpl_amt=tmpl_amt,
                     tmpl_rcv=tmpl_rcv,
                     tmpl_timeout=tmpl_timeout):

    periodic_pay_core = And(
        Txn.type_enum() == TxnType.Payment,
        Txn.fee() <= tmpl_fee,
        Txn.first_valid() % tmpl_period == Int(0),
        Txn.last_valid() == tmpl_dur + Txn.first_valid(),
        Txn.lease() == tmpl_lease
    )

    periodic_pay_transfer = And(
        Txn.close_remainder_to() == Global.zero_address(),
        Txn.rekey_to() == Global.zero_address(),
        Txn.receiver() == tmpl_rcv,
        Txn.amount() == tmpl_amt
    )

    periodic_pay_close = And(
        Txn.close_remainder_to() == tmpl_rcv,
        Txn.rekey_to() == Global.zero_address(),
        Txn.receiver() == Global.zero_address(),
        Txn.first_valid() == tmpl_timeout,
        Txn.amount() == Int(0)
    )

    periodic_pay_escrow = periodic_pay_core.And(periodic_pay_transfer.Or(periodic_pay_close))

    return periodic_pay_escrow

periodic_pay_escrow = periodic_payment()

if __name__ == "__main__":
    print(compileTeal(periodic_pay_escrow, mode=Mode.Signature, version=2))
