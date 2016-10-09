class Movie():
    """ Movie creates an object that contains information about the movie.

    Attributes
    ----------
        title (str) : Movie title
        trailer_youtube_url (str) : Youtube trailer url
        poster_image_url (str) : Poster image url
    """

    def __init__(self, title, trailer_youtube_url, poster_image_url):
        self.title = title
        self.trailer_youtube_url = trailer_youtube_url
        self.poster_image_url = poster_image_url
