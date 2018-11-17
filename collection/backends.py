from registration.backends.simple.views import RegistrationView

class TOKRegistrationView(RegistrationView):
	def get_success_url(self, user):
		return ('main_menu')