# Counter Widget
Counter Widget is a simple widget made up of two buttons and a number input. Two buttons are used to increase and decrease the input value.

![](https://github.com/AbdullahSaquib/django-counter-widget/blob/master/docs/SimpleCounter.gif?raw=true)

## Installation
In terminal:

    pip install django-counter-widget

Add the app in your INSTALLED_APPS settings

    INSTALLED_APPS = [
        ...
        'counter_widgets',
    ]

## How To Use
You can use the CounterWidget for your forms IntegerField.

    from counter_widgets import CounterWidget

    class YourForm(forms.Form):
        counter_field = forms.IntegerField(widget=CounterWidget)

In the template where you are rendering YourForm, include the following line

    {{ form.media }}

where "form" is the name of the context variable that refers to the form containing the counter widget. If you do not include the above line in the template, the increase (+) and decrease (-) buttons will not work. 
{{form.media}} will add the following line in the rendered HTML

    <script src="/static/counter_widgets/js/counter.js"></script>

## Customising the Widget
You can create your own customized widget from Counterwidget. You can change increment text, decrement text, delta (increment/decrement amount default is 1), you can have different values ​​for increment and decrement.
In the following we have customized counter widget increment_text, decrement_text, increment_value, decrement_value
    
    class TestForm(forms.Form):
        count = forms.IntegerField(widget=CounterWidget(
            increment_text="Add 100",
            decrement_text="Subtract 50",
            increment_value=100,
            decrement_value=50))

![](https://github.com/AbdullahSaquib/django-counter-widget/blob/master/docs/CustomCounter.gif?raw=true)

Another example

    class TestForm(forms.Form):
        count = forms.IntegerField(widget=CounterWidget(delta=100))

![](https://github.com/AbdullahSaquib/django-counter-widget/blob/master/docs/Counter100.gif?raw=true)