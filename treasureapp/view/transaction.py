from django.shortcuts import render_to_response, get_object_or_404, HttpResponseRedirect
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from treasureapp.models import Account, Transaction, Image
from treasureapp.forms import TransactionForm, ImageUploadForm

from treasureapp.authenticators import authenticate_transaction

@login_required
def transaction_detail(request, transaction_id):
	"""
	Show details of a specific transaction.

	On GET, it will return details on the transaction with the given id.
	"""

	# Grab the transaction (or 404, of course)
	transaction = get_object_or_404(Transaction, pk=transaction_id)

	# Pass it back out to the renderer
	context = RequestContext(request, {"section":"accounts",
		"transaction":transaction})
	return render_to_response("transactions/detail.html", context)

@login_required
def transaction_create(request, account_id, *args, **kargs):
	"""
	Allow the user to create a new transaction.

	On GET, it will return a form to create a new transaction.
	On POST, it will use the post data to add a transaction to the database.
	"""

	# 404 on nonexistent from account
	from_acct = get_object_or_404(Account, pk=account_id)

	if request.method == 'POST':
		transaction_form = TransactionForm(request.POST)
		if transaction_form.is_valid():
			transaction = transaction_form.save(commit=False)

			# Populate the from_acct field
			transaction.from_acct = from_acct

			# Check that the user can make this transaction
			if not authenticate_transaction(request.user, transaction):
				raise PermissionDenied()

			transaction.save()

			return HttpResponseRedirect('/account/' + str(account_id))
	else:
		transaction_form = TransactionForm()

	# Update the CSRF token
	kargs.update(csrf(request))
	context = RequestContext(request, dict(section="accounts",
		account=from_acct,
		form=transaction_form,
		mode='create',
		**kargs))
	return render_to_response("transactions/form.html", context)

@login_required
def transaction_update(request, transaction_id, *args, **kargs):
	"""
	Update an individual transaction.

	On GET, it will return a form to update the transaction.
	On POST, it will update information about the transaction.
	"""

	# Grab the transaction (or 404, of course)
	transaction = get_object_or_404(Transaction, pk=transaction_id)

	# Check that the user can update both of the involved accounts
	if not authenticate_transaction(request.user, transaction):
		raise PermissionDenied()

	if request.method == 'POST':
		# Try to validate and update
		transaction_form = TransactionForm(request.POST, instance=transaction)
		if transaction_form.is_valid():
			transaction_form.save()
			return HttpResponseRedirect('/transaction/' + str(transaction_id))
	else:
		# Populate the form with the current transaction data
		transaction_form = TransactionForm(instance=transaction)

	# Pass back the form we have, after updating CSRF
	kargs.update(csrf(request))
	context = RequestContext(request, dict(section="accounts",
		account=transaction.from_acct,
		form=transaction_form,
		transaction=transaction,
		mode='update',
		**kargs))
	return render_to_response("transactions/form.html", context)

@login_required
def transaction_upload_file(request, transaction_id, *args, **kargs):
	"""
	Upload a file (currently, only images) to a transaction.

	On GET, it will return a form to upload an image.
	On POST, it will attach the image to the transaction.
	"""

	# As always, get transaction
	transaction = get_object_or_404(Transaction, pk=transaction_id)

	# Check that the user has permissions on this transaction.
	# For now, assume that a lack of account permissions means a lack of
	# any upload rights.
	if not authenticate_transaction(request.user, transaction):
		raise PermissionDenied()

	if request.method == 'POST':
		# Declare tautologies (just kidding, establish an image with this
		# as its parent transaction)
		image = Image(transaction=transaction)
		upload_form = ImageUploadForm(request.POST, request.FILES,
				instance=image)
		if upload_form.is_valid():
			upload_form.save()
			return HttpResponseRedirect('/transaction/' + str(transaction_id))
	else:
		upload_form = ImageUploadForm()

	# Pass back the upload form after updating CSRF token
	kargs.update(csrf(request))
	context = RequestContext(request, dict(transaction=transaction,
		form=upload_form, **kargs))
	return render_to_response("transactions/upload.html", context)
