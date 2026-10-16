#Start
app_root = None # used for communicating plugin --> app. In loaded app, contains all methods / classes and other from msgr.py, dynamically updated.
class Plugin:
    @staticmethod
    def give_data(v):
        global app_root
        app_root = v

    @staticmethod
    def execute():
        ... # you can write any code here

#End
