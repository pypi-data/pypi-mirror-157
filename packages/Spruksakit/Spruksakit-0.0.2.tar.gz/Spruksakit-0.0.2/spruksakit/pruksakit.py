class Spruksakit:
    """
    It's me Spruksakit

    <<<<<< My First Library >>>>>>
    oh = Spruksakit()
    oh.show_name()
    oh.show_page()
    oh.show_youtube()
    oh.about()
    oh.show_art()
    """

    def __init__(self):
        self.name = 'Spruksakit'
        self.page = 'https://www.facebook.com/pruksakit/'

    def show_name(self):
        print('Hi, I am {}' .format(self.name));

    def show_page(self):
        print('FB Page: {}' .format(self.page));

    def show_youtube(self):
        print('Youtube: https://www.youtube.com/c/SarunPruksakit');

    def about(self):
        text = """
         Hey, Nice to meet you here.
        """
        print(text)

    def show_art(self):
        text = """
_______________________________________________________________
|| | | ||| | ||| | | ||| | ||| | | ||| | ||| | | ||| | ||| | | ||
||_|_|_|||_|_|||_|_|_|||_|_|||_|_|_|||_|_|||_|_|_|||_|_|||_|_|_||
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |
|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|hjw
        """
        print(text)

if __name__ == '__main__':
    oh = Spruksakit()
    oh.show_name()
    oh.show_page()
    oh.show_youtube()
    oh.about()
    oh.show_art()