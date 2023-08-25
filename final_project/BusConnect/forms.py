from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import    Article,Station,WorkingHour,UserProfile,Complain

from datetime import datetime


class ComplainForm(forms.ModelForm):
    class Meta:
        model = Complain
        fields = ('subject', 'description')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number',  'profile_picture', 'date_of_birth', 'state_of_origin', 'local_government', 'address', 'nin_number']





class TripForm(forms.Form):
    hour=WorkingHour.objects.all()
    origins = Station.objects.filter(station_name="na'ibawa").all()
    destinations = Station.objects.exclude(station_name="na'ibawa")
    origin = forms.ModelChoiceField(queryset=origins, empty_label='Select Origin', widget=forms.Select(attrs={'class': 'form-control'}))
    destination = forms.ModelChoiceField(queryset=destinations, empty_label='Select Destination', widget=forms.Select(attrs={'class': 'form-control'}))
    time =forms.ModelChoiceField(queryset=hour, empty_label='Select Time', widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control','type':'date'}))

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.now().date():
            raise forms.ValidationError("Date cannot be in the past.")
        return date

    def clean_time(self):
        date = self.cleaned_data.get('date')
        time = self.cleaned_data['time']
        now = datetime.now()
        if date == now.date() and time < now.time():
            raise forms.ValidationError("Time cannot be in the past.")
        return time
    

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'email']

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        css_classes = 'form-control'
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = css_classes

        
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder':'enter your  username','class':'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder':'enter your  password','class':'form-control'}))




class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        article = super().save(commit=False)
        if commit:
            article.save()
        return article


class Search_routeForm(forms.Form):
    origin = forms.CharField(label='origin',max_length=30)
    destination = forms.CharField(label='destination',max_length=30)
        
    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination  = cleaned_data.get('destination')


        if not origin:
            self.add_error('origin','you must type in something')
            
        
        if not destination:
            self.add_error('destination','destination  must contain somthing')
            
        return cleaned_data
            
        
       
    

    
    
