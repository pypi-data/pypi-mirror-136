### Installation

`pip install django-wspay`

### Set environment

WS_PAY_SHOP_ID =
WS_PAY_SECRET_KEY =
WS_PAY_SUCCESS_URL =
WS_PAY_CANCEL_URL =
WS_PAY_ERROR_URL =
WS_PAY_DEVELOPMENT = True

generate input_data
render_wspay_form
add to installed_apps
django-admin migrate
path('wspay/', include('wspay.urls', 'wspay')),

def success_url_resolver(\*\*kwargs):
cart_id = kwargs['cart_id']
return reverse_lazy('orders:payment-completed', kwargs={'pk': cart_id})

WS_PAY_SUCCESS_URL = success_url_resolver
WS_PAY_CANCEL_URL = reverse_lazy('orders:payment-canceled')
WS_PAY_ERROR_URL = reverse_lazy('orders:payment-failed')

signals
