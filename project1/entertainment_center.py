from fresh_tomatoes import open_movies_page
from media import Movie

# Create movie objects
the_birds = Movie("The Birds",
                  "https://www.youtube.com/watch?v=LrN_U830_Gc",
                  "https://upload.wikimedia.org/wikipedia/commons/c/c0/The_Birds_original_poster.jpg")

the_beyond = Movie("The Beyond",
                   "https://www.youtube.com/watch?v=ef0oH3ZizfI",
                   "https://upload.wikimedia.org/wikipedia/en/3/35/L%27aldil%C3%A0-poster.jpg")

fired_up = Movie("Fired Up",
                 "https://www.youtube.com/watch?v=8VZ7bKZ4FWE",
                 "https://upload.wikimedia.org/wikipedia/en/c/ce/Fired-up.jpg")

hocus_pocus = Movie("Hocus Pocus",
                    "https://www.youtube.com/watch?v=2UUMsInka2s",
                    "https://upload.wikimedia.org/wikipedia/en/c/c9/Hocuspocusposter.jpg")

nightmare = Movie("Nightmare on Elm Street",
                  "https://www.youtube.com/watch?v=dCVh4lBfW-c",
                  "https://upload.wikimedia.org/wikipedia/en/f/fa/A_Nightmare_on_Elm_Street_%281984%29_theatrical_poster.jpg")

violent_naples = Movie("Violent Naples",
                       "https://www.youtube.com/watch?v=asd-sjoN5h0",
                       "https://upload.wikimedia.org/wikipedia/en/8/83/Napoli-violenta.jpg")

# Store movie objects in a list
movie_list = [the_birds, hocus_pocus, nightmare,
              the_beyond, violent_naples, fired_up]

# Create and open the movie page
open_movies_page(movie_list)
