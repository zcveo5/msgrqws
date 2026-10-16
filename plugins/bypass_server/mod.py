#Start
app = None

class Main:
	@staticmethod
	def give_data(v):
		global app
		app = v

	@staticmethod
	def execute():
		(app.main.create('bypass_button', app.Button, text='server bypass', command=app.main.quit, font=('Consolas', 9), recreate_if_exists=True)
		 .build('place', x=10, y=400))

#End