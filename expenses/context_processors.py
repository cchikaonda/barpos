from .forms import AddExpenseForm

def expense_form_processor(request):
     form = AddExpenseForm()
     return {'form': form}