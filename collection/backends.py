from registration.backends.simple.views import RegistrationView
from django.core.mail import EmailMultiAlternatives

class TOKRegistrationView(RegistrationView):
	def get_success_url(self, user):

		message = '''Hi ''' + user.username + ''',

Thank you for signing up to the Tree of Knowledge.'''
		email_message = EmailMultiAlternatives('Tree of Knowledge', message, 'noreply@treeofknowledge.ai', [user.email])
		email_message.send()

		return ('main_menu')