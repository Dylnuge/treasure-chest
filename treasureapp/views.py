from django.shortcuts import render_to_response, get_object_or_404, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext

from treasureapp.models import Account, Transaction
from treasureapp.forms import AccountForm

# Basic content handlers

def index(request):
    """
    Render the main page of the Treasure Chest application.
    """

    context = RequestContext(request, {"section":"index"})
    return render_to_response("index.html", context)

def help(request):
    """
    Render the main page of the help contents.
    """

    context = RequestContext(request, {"section":"help"})
    return render_to_response("help/index.html", context)

# Account handlers

def account_list(request):
    """
    Render the listing of all accounts.

    On GET, it will return a listing of all accounts.
    """

    account_list = Account.objects.all()

    # TODO: Add signal logic on transaction create so we don't need to do this
    # Update cached values of accounts
    for account in account_list:
        account.update_balance()

    context = RequestContext(request, {"section":"accounts",
        "account_list":account_list})
    return render_to_response("accounts/list.html", context)

def account_detail(request):
    """
    Show details of a specific account.

    On GET, it will return details on the specific account.
    """

    context = RequestContext(request, {"section":"accounts"})
    return render_to_response("accounts/detail.html", context)

def account_create(request, *args, **kargs):
    """
    Allow the user to create a new account.

    On GET, it will return a form to create a new account.
    On POST, it will use the post data to add an account to the database.
    """

    if request.method == 'POST':
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            new_account = account_form.save(commit=False)
            # Add in an account balance of 0. Always. No exceptions.
            new_account.balance = 0
            new_account.save()
            return HttpResponseRedirect('/account')
    else:
        account_form = AccountForm()

    # Update the CSRF token
    kargs.update(csrf(request))
    context = RequestContext(request, dict(section="accounts",
        form=account_form, **kargs))
    return render_to_response("accounts/form.html", context)

def account_update(request):
    """
    Update an individual account.

    On GET, it will return a form to update the account.
    On POST, it will update information about the account.
    """

    context = RequestContext(request, {"section":"accounts"})
    return render_to_response("accounts/detail.html", context)

# Transaction handlers

def transaction_list(request):
    transaction_list = Transaction.objects.all()

    context = RequestContext(request, {"section":"transactions",
        "transaction_list":transaction_list})
    return render_to_response("transactions/list.html", context)

def transaction_detail(request):
    pass

def transaction_create(request):
    pass

def transaction_update(request):
    pass
