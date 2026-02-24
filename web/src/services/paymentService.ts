class CreditCard {
  process(): void {
    console.log("Processing card...");
  }
}

class PayPal {
  // UNUSED: This method is never called, but tools may think it is because 'process' is called on CreditCard.
  process(): void {
    console.log("Processing paypal...");
  }
}

// was: orchestrator for payment flow, never called from routes
export function runPayment(): void { // UNUSED (demo)
  const cc = new CreditCard();
  cc.process();
}
