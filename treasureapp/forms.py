from django.forms import Form, ModelForm, DecimalField

from treasureapp.models import Account, Transaction, AccountGroup, Image

class AccountForm(ModelForm):
	"""
	A basic form for creating or updating an account.
	"""

	class Meta:
		model = Account
		# User cannot directly edit cached balance
		fields = ('name', 'description', 'accessors')

class TransactionForm(ModelForm):
	"""
	A basic form for creating or updating a transaction.
	"""

	# Force the decimal number to be positive
	amount = DecimalField(min_value=0, max_digits=10, decimal_places=2)

	class Meta:
		model = Transaction
		fields = ('to_acct', 'amount', 'description')

class AccountGroupForm(ModelForm):
	"""
	A form for creating and updating user groups.
	"""

	class Meta:
		model = AccountGroup

class ImageUploadForm(ModelForm):
	"""
	A form for uploading images (and only images, right now).
	"""

	class Meta:
		model = Image
		fields = ('upload_file',)
