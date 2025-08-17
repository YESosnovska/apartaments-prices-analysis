import pandas as pd

flats = pd.read_csv("Ukraine.csv")

random_flats = flats.sample(n=50)
random_flats.to_csv("Random_flats.csv", index=False)
