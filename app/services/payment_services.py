class CreditCard:
    def process(self):
        print("Processing card...")

class PayPal:
    # UNUSED: This method is never called, but Vulture will think it is
    # because 'process' is called on CreditCard.
    def process(self): 
        print("Processing paypal...")

def run_payment():
    cc = CreditCard()
    cc.process()