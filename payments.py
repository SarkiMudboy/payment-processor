from dateutil.relativedelta import relativedelta
import datetime
import requests
import json
import uuid
import os

class Base:
	def __init__(self):
		self.id = ''
		self.dtype = ''

	def save_to_db(self, dtype):

		data_dict = {self.id: self.__dict__}
		db_entries = None
		try:
			with open(dtype + '.json', 'r') as entries:
				db_entries = json.loads(entries)
		except Exception as e:
			print(str(e))

		if db_entries:
			db_entries.update(data_dict)

		with open(dtype + '.json', 'w') as entries:
			json.dump(db_entries, entries, indent=4)

	def update_db(self, dtype):

		entry, entries = self.load_from_db(dtype)

		entry = {self.id: self.__dict__}
		entries[self.id] = entry

		with open(dtype + '.json', 'w') as db_entries:
			json.dump(entries, db_entries, indent=4)


	def load_from_db(self, dtype):

		data_dict = {self.id: self.__dict__}
		db_entries = None
		try:
			with open(dtype + '.json', 'r') as entries:
				db_entries = json.loads(entries)
		except Exception as e:
			print(str(e))

		ids = db_entries.keys()
		if self.id in keys:
			return db_entries[self.id], db_entries
		else:
			return None


class Transaction(Base):
	def __init__(self, amount):
		self.id = str(uuid.uuid4())
		self.confirmation_code = ''
		self.user = None
		self.amount = amount
		self.status = None

class User(Base):
	def __init__(self):
		self.id = str(uuid.uuid4())
		self.username = ''
		self.first_name = ''
		self.last_name = ''
		self.full_name = ''
		self.pending_transactions = []
		self.total_paid_amount = 0
		self.create_user()

	def create_user(self):
		self.full_name = self.first_name + " " + self.last_name
		self.save_to_db('user')

class PaymentProcessor:
	def __init__(self):
		self.payment_type = None

	def one_time_payment(self, amount, transaction):
		# process and return transaction
		# set status to whatever
		# add conf code
		# process and return transaction
		pass

	def subscription(amount, subscription, transaction):
		# process and return transaction
		# set status to whatever
		# add conf code
		# process and return transaction
		pass

	def refund(self, transaction):
		# process and return transaction
		# set status to whatever
		# add conf code
		# process and return transaction
		pass

	def process_payment(self, *args, **kwargs):

		if self.payment_type == 'one_time_payment':
			return self.one_time_payment(*args, **kwargs)

		if self.payment_type == 'subscription':
			return self.subscription(*args, **kwargs)

		if self.payment_type == 'refund':
			return self.refund(*args, **kwargs)


	def issue_invoice(self, transaction):
		invoice = f'''
		Name: {transaction.user.full_name}
		Transaction : {transaction.id}
		Invoice Number: {uuid.uuid4()}
		--------------------------------
		Amount: ${transaction.amount}
		Tax: %0.00
		Total: ${transaction.amount}
		Date: {datetime.datetime.now()}
		-------------------------------
		Transaction status : {transaction.status}
		Confirmation Code: {transaction.confirmation_code}
		'''
		return invoice

class Subscription:

	BILLING = dict()

	def __init__(self):
		self.user = None
		self.name = ''
		self.billing_period = None
		self.next_billing_date = None
		self.active = False
		self.plan = 0.0
		self.billed = 0.0
		self.set_billing()

	def verify_billing(self):
		'''verifies date and set next billing date and return true/false
		also verifies if subscription active'''

		now = datetime.datetime.now()
		if self.active and (now >= self.next_billing_date()):	
			return True

		return False

	def update_billing(self):
		# updates the billing information

		now = datetime.datetime.now()
		if BILLING:
			self.next_billing_date = now + relativedelta(**BILLING)
	
	def bill(self):
		self.billed += float(self.plan)
		self.update_billing()

	def set_billing(self):
		# sets the billing period i.e every week, month, year 
		if self.billing_period:
			BILLING = {
				self.billing_period: 1
				}


class CreditCardPayment(PaymentProcessor):
	def __init__(self, card):
		PaymentProcessor.__init__()
		self.card = card
	
	def one_time_payment(self, transaction):

		'''
		processes the payment
		'''
		print('submitting transaction: {} to {}'.format(transaction.id, card.issuing_bank))
		print("Verifying transaction...")
		print('Transaction approved, processing payment...')

		transaction.status = 'pending'
		transaction.confirmation_code = uuid.uuid4()

		# charge the card
		charged = card.charge(transaction.amount)

		if charged:
			print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
			transaction.status = 'paid'
		else:
			transaction.status = 'cancelled'
			print(card.message)

		invoice = self.issue_invoice()

		return invoice, transaction

	def subscription(subscription, transaction):

		# verify if billing is valid
		bill = subscription.verify_billing()

		if bill:

			# processes the payment
			print('submitting transaction: {} to {}'.format(transaction.id, card.issuing_bank))
			print("Verifying transaction..")
			print('Transaction approved, processing payment...')
			transaction.status = 'pending'

			transaction.confirmation_code = uuid.uuid4()

			charged = card.charge(subscription.plan)

			if charged:
				subscription.bill()
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
				print('You have renewed your {} subscription plan till {}'.format(subscription.name, subscription.next_billing_date))
				transaction.status = 'paid'
			else:
				transaction.status = 'cancelled'
				print(card.message)

		else:
			print('Transaction failed')

		# issues an invoice
		invoice = self.issue_invoice(transaction)
		print('_____Your invoice_____' + "\n", invoice)

		return invoice, transaction

	def refund(self, transaction, refund_transaction):

		# processes the payment

		rt = refund_transaction.load_from_db()

		if rt:

			print('submitting refund request for {}: {} to {}'.format(refund_transaction.id, transaction.id, card.issuing_bank))
			print("Verifying transaction..")
			print('Transaction approved, processing refund...')
			transaction.status = 'pending'

			transaction.confirmation_code = uuid.uuid4()

			# credits the card
			charged = card.credit(refund_transaction.amount)

			if charged:
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
				print('Refund request successful, You have been credited {}'.format(transaction.amount))
				transaction.status = 'paid'
				refund_transaction.status = 'cancelled'
				refund_transaction.save_to_db('transactions')
			else:
				transaction.status = 'cancelled'
				print(card.message)

			# issues an invoice
			invoice = self.issue_invoice(transaction)
			print('_____Your invoice_____' + "\n", invoice)

			return invoice, transaction
		else:
			print("Cannot find transaction")
			return False


class Card:
	def __init__(self, issuer, card_number, expiry_date, cvv):
		self.user = None
		self.issuer = issuer
		self.card_number = card_number
		self.expiry_date = expiry_date
		self.cvv = cvv
		self.balance = 0.0
		self.limit = 20000000 # This is just a dummy number I am not sure
		self.message = ''

	def charge(self, amount):

		# checks if card has expired
		if self.validate_expiry_date():

			amount_to_charge = float(amount)

			if self.balance >= amount_to_charge and amount_to_charge < self.limit:
				self.balance -= float(amount)
			else:
				return False

			return True

		# card has expired so transaction will fail
		self.message = 'Card invalid!'

		return False

	def credit(self, amount):
		self.balance += float(amount)
		return True


	def validate_expiry_date(self):

		now = datetime.datetime.now()
		valid = False if now > self.expiry_date else True:	
		return valid

	def save_to_db(self):
		# save card to json
		pass

	@property
	def issuing_bank(self):
		return self._issuer

class PayPalSubscription(Subscription):
	def __init__(self):
		Subscription.__init__()
		self.name = "regular payments"
		self.create_plan_endpoint = 'http://paypal/api/payment/subscription/create'
		self.create_plan()

	def create_plan(self):
		# set up parent class too
		created = request.get(self.create_plan_endpoint, headers=headers)


class PayPalClient:

	ENDPOINTS = {
		# dummy endpoints
		'create':'https://paypal/api/payment/create'
		'approve': 'https://paypal/api/payment/approve'
		'execute': 'https://paypal/api/payment/execute'
		'create_plan': ''
	}

	def __init__(self):
		self.user = None
		self.api_creds = []
		self.client_token = ''
		self.paypal_account_balance = 0.00



class PayPalPayment(PaymentProcessor):
	def __init__(self, paypal_client):
		self.paypal_client = paypal_client
		self.subscription = None

	def one_time_payment(self, transaction):

		'''
		processes the payment
		'''
		# charge the account
		charged = self.pay(transaction)

		if charged:
			transaction.confirmation_code = uuid.uuid4()
			print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
			transaction.status = 'paid'
		else:
			transaction.status = 'cancelled'
			print('Transaction failed, contact PayPal support')

		invoice = self.issue_invoice()

		return invoice, transaction

	def pay(self, transaction):

		header = {'transaction': transaction}
		headers = self.get_headers(header)

		paid = False

		print('Creating payment intent...')

		created_payment = self.request(ENDPOINTS['create'], headers=headers)
		transaction.id = created_payment.id
		transaction.status = 'pending'

		if created_payment.status == 'success':

			header = {'payment': created_payment}
			headers = self.get_headers(header)

			# this should handle checking client's balance
			allow_payment = self.authorize_payment(headers)

			if allow_payment:
				print('Transaction approved, processing payment...')
				payment = requests.post(ENDPOINTS['execute'], headers=headers)
				
				if payment:
					self.paypal_client.paypal_account_balance -= float(transaction.amount)
		
		return payment

	def subscription(self, transaction):
		# verify if billing is valid
		bill = self.subscription.verify_billing()

		if bill:

			# charge the account
			charged = self.pay(transaction)

			if charged:
				subscription.bill()
				transaction.confirmation_code = uuid.uuid4()
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
				self.paypal_client.paypal_account_balance -= float(transaction.amount)
				print('You have renewed your {} subscription plan till {}'.format(subscription.name, subscription.next_billing_date))
				transaction.status = 'paid'
			else:
				transaction.status = 'cancelled'
				print('Transaction failed, contact PayPal support')

			invoice = self.issue_invoice()

			return invoice, transaction

	def get_headers(self, data):

		token =  self.paypal_client.client_token
		# api_secret_key = self.paypal_client.api_creds[0]
		# api_auth_key = self.paypal_client.api_creds[1]

		headers = {
			'Authorization': 'Bearer {}'.format(token),
		}

		if data:
			headers.update(data)

		return headers

	def issue_invoice(self, transaction):
		header = {'transaction': transaction}
		headers = self.get_headers(header)
		invoice  = requests.get('https://paypal/api/invoices', headers=headers)

		if invoice:
			return invoice

		return False

	def refund(self, transaction, refund_transaction):

		'''processes the refund transaction'''

		# verifies if the payment exists from the json file
		rt = refund_transaction.load_from_db()

		if rt:

			header = {'payment': refund_transaction, 'transaction': transaction}
			headers = self.get_headers(header)

			print('submitting refund request for {} to PayPal'.format(refund_transaction.id))

			transaction.confirmation_code = uuid.uuid4()

			# credits the account
			credited = requests.post('https://paypal/api/refund', headers=headers)

			if charged:
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))

				self.client.paypal_account_balance += float(refund_transaction.amount)
				print('Refund request successful, You have been credited {}'.format(refund_transaction.amount))

				transaction.status = 'paid'
				refund_transaction.status = 'cancelled'
				refund_transaction.save_to_db('transactions')
			else:
				transaction.status = 'cancelled'
				print(card.message)

			# issues an invoice
			invoice = self.issue_invoice(transaction)
			print('_____Your invoice_____' + "\n", invoice)

			return invoice, transaction
		else:
			print("Cannot find transaction")
			return False
		pass

	def authorize_payment(self, headers):
		print("Verifying transaction...")
		verified = requests.get(ENDPOINTS['approve'], headers=headers)
		if verified:
			return True
		return False


class BanckAcc:
	def __init__(self):
		self.user = None
		self.account_holder = ''
		self.account_number = ''
		self.balance = 0.0
		self.bank_name = ''

	def debit(self, amount):
		if self.balance > amount:
			self.balance -= amount
		else:
			print("Insufficient Funds")
			return False
		return True

	def credit(self, amount):
		self.balance += amount

class BankAccountPayment(PaymentProcessor):
	def __init__(self):
		PaymentProcessor.__init__()
		self.bank_account = None

	def one_time_payment(self, transaction):
		'''
		processes the payment
		'''
		print('submitting transaction: {} to {}'.format(transaction.id, self.bank_account.bank_name))
		print("Verifying transaction...")
		print('Transaction approved, processing payment...')

		transaction.status = 'pending'
		transaction.confirmation_code = uuid.uuid4()

		# charge the card
		charged = self.bank_account.debit(transaction.amount)

		if charged:
			print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
			transaction.status = 'paid'
		else:
			transaction.status = 'cancelled'
			print('Transaction failed')

		invoice = self.issue_invoice()
		print('_____Your invoice_____' + "\n", invoice)

		return invoice, transaction

	def subscription(self, subscription):
		# verify if billing is valid
		bill = subscription.verify_billing()

		if bill:

			# processes the payment
			print('submitting transaction: {} to {}'.format(transaction.id, self.bank_account.bank_name))
			print("Verifying transaction..")
			print('Transaction approved, processing payment...')
			transaction.status = 'pending'

			transaction.confirmation_code = uuid.uuid4()

			charged = self.bank_account.debit(subscription.plan)

			if charged:
				subscription.bill()
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
				print('You have renewed your {} subscription plan till {}'.format(subscription.name, subscription.next_billing_date))
				transaction.status = 'paid'
			else:
				transaction.status = 'cancelled'
				print("Transaction failed")

		else:
			print('Transaction failed')

		# issues an invoice
		invoice = self.issue_invoice(transaction)
		print('_____Your invoice_____' + "\n", invoice)

		return invoice, transaction


	def refund(self, transaction, refund_transaction):

		# processes the payment

		rt = refund_transaction.load_from_db()

		if rt:

			print('submitting refund request for {}: {}'.format(refund_transaction.id, transaction.id))
			print("Verifying transaction..")
			print('Transaction approved, processing refund...')
			transaction.status = 'pending'

			transaction.confirmation_code = uuid.uuid4()

			# credits the card
			charged = self.bank_account.credit(refund_transaction.amount)

			if charged:
				print('Transaction complete, Success your confirmation code is {}'.format(transaction.confirmation_code))
				print('Refund request successful, You have been credited {}'.format(transaction.amount))
				transaction.status = 'paid'
				refund_transaction.status = 'cancelled'
				refund_transaction.save_to_db('transactions')
			else:
				transaction.status = 'cancelled'
				print("Transaction failed")

			# issues an invoice
			invoice = self.issue_invoice(transaction)
			print('_____Your invoice_____', invoice)

			return invoice, transaction
		else:
			print("Cannot find transaction")
			return False


	

