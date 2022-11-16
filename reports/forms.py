from crispy_forms.layout import Layout
from django.db.models import fields
from django.utils.safestring import mark_safe
from inventory.models import ItemCategory
from pos.models import Order, Customer
from inventory.models import ItemCategory, Item
from django import forms
from django.forms import ModelForm
from django.forms import widgets
from django.db import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row,Field
from crispy_forms.bootstrap import AppendedText, PrependedText, PrependedAppendedText


class SearchBetweenTwoDatesForm(forms.Form):
    start_date_time = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'],widget = forms.DateTimeInput(attrs={'class': 'form-control','type': 'datetime-local'}, format = '%Y-%m-%dT%H:%M'))
    end_date_time = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M'],widget = forms.DateTimeInput(attrs={'class': 'form-control','type': 'datetime-local'}, format = '%Y-%m-%dT%H:%M'))
class  FilterDatesForm(forms.Form):
    balancing_date = forms.DateField(input_formats=['%Y-%m-%d'],widget = forms.DateInput(attrs={'class': 'form-control','type': 'date'}, format = '%Y-%m-%d'))
CHOICES = [
        ('TDAY','Today'),
        ('YDAY', 'Yesterday'),
        ('Last7D','Last 7 Days'),
        ('Last30D','Last 30 Days'),
        ('ThisM','This Month'),
        ('LM','Last Month'),
    ]
class DefaultReportsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category = self.fields['category']
        category.choices = list(category.choices)
        category.choices.append(tuple(('all_catgories', 'All Categories')))

    # def __init__(self, *args, **kwargs):
    #     super(DefaultReportsForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.fields["category"].label_class =  "col-lg-12"
    #     self.helper.layout = Layout(PrependedText('Reporting Period', mark_safe('<i class="far fa-calendar-alt">')))
    #     self.helper.label_class = "col-lg-12"
    
    reporting_period = forms.ChoiceField(label = "Reporting Period", choices= CHOICES, widget=forms.Select(attrs={'class':'selector form-control'}), required= True)
    class Meta:
        model = Item
        fields = (
            'category', 'reporting_period')
    
        widgets = {
            'category': forms.Select(attrs={'class': 'js-max-length form-control','max-length': '70', 'id': 'example-max-length4','placeholder': '50 chars limit..', 'data-always-show': 'True',
                                                'data-pre-text': 'Used', 'data-separator': 'of',
                                                'data-post-text': 'characters'}),
            'reporting_period': forms.Select(attrs={'class': 'js-max-length form-control','max-length': '70', 'id': 'example-max-length4','placeholder': '50 chars limit..', 'data-always-show': 'True',
                                                'data-pre-text': 'Used', 'data-separator': 'of',
                                                'data-post-text': 'characters'})
        }
    
        


# class FilterForm(forms.Form):
#     reporting_period = forms.ChoiceField(label = "Reporting Period", choices=(), widget=forms.Select(attrs={'class':'selector'}))
#     EXTRA_CHOICES = [
#         ('TDAY','Today'),
#         ('YDAY', 'Yesterday'),
#     ]
#     def __init__(self, *args, **kwargs):
#         super(FilterForm, self).__init__(*args, **kwargs)
#         choices = [(pt.id, unicode(pt)) for pt in ItemCategory.objects.all()]
#         choices.extend(EXTRA_CHOICES)
#         self.fields['reporting_period'].choices = choices

class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone_number',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form'}),
            'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
        }