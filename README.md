# PaymentsProcessor
A dummy payment processing system that consists of the following components:
- Payment processor
- Transaction
- User

Payment processor types:
- Processing credit card payments
- Processing PayPal payments
- Processing bank account payments

Each payment processor should be able to:
- process one-time payments
- process subscription-based payments
- process refunds
- issue invoices

Transaction should have the following attributes:
- id
- confirmation code
- user
- amount
- status (pending, paid, cancelled)

User:
- id
- username
- first_name
- last_name
- full_name
- pending_transactions
- paid_transactions
- total_paid_amount
  
### Note 
Actual functionality of the mentioned payment processors are not implemented. Print statements are used to denote actions.
