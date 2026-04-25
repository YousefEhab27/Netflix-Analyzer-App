import requests # type: ignore
import tkinter as tk
import pandas as pd
import time
import json
import os

# =========================
# API KEY
# =========================
API_KEY = "b4f35527"
FAV_FILE = "favorites.json"

# =========================
# LOAD FAVORITES FROM FILE
# =========================
def load_favorites():
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    return []

def save_favorites():
    with open(FAV_FILE, "w") as f:
        json.dump(favorites, f)

favorites = load_favorites()

# =========================
# SPLASH SCREEN
# =========================
splash = tk.Tk()
splash.title("Loading...")
splash.geometry("350x200")
splash.configure(bg="black")

tk.Label(
    splash,
    text="NETFLIX ANALYZER",
    fg="#E50914",
    bg="black",
    font=("Helvetica", 16, "bold")
).pack(expand=True)

splash.update()
time.sleep(2)
splash.destroy()

# =========================
# DATA
# =========================
data = pd.read_csv("netflix_titles.csv")

# =========================
# FUNCTIONS
# =========================
def show_results(df):
    result.delete(1.0, tk.END)
    movie_listbox.delete(0, tk.END)

    if len(df) == 0:
        result.insert(tk.END, "No results found ❌")
        return

    for _, row in df.head(20).iterrows():
        movie_listbox.insert(tk.END, row["title"])


# =========================
# SEARCH
# =========================
def search_movie():
    name = search_entry.get().strip().lower()

    movie_listbox.delete(0, tk.END)

    if not name:
        result.insert(tk.END, "Enter movie name ❌")
        return

    url = f"http://www.omdbapi.com/?s={name}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data_api = response.json()

        if data_api.get("Response") == "False":
            result.insert(tk.END, "No movies found ❌")
            return

        for movie in data_api["Search"]:
            movie_listbox.insert(tk.END, movie["Title"])

    except Exception as e:
        result.insert(tk.END, f"Error ❌ {e}")


# =========================
# SHOW DETAILS
# =========================
def show_movie_details(event):
    try:
        selected = movie_listbox.get(movie_listbox.curselection())
    except:
        return

    url = f"http://www.omdbapi.com/?t={selected}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data_api = response.json()

        result.delete(1.0, tk.END)

        result.insert(tk.END,
            f"{data_api.get('Title')} 🎬\n"
            f"Year: {data_api.get('Year')}\n"
            f"Genre: {data_api.get('Genre')}\n"
            f"IMDb Rating: ⭐ {data_api.get('imdbRating')}\n"
        )

    except Exception as e:
        result.insert(tk.END, f"Error ❌ {e}")


# =========================
# FILTER
# =========================
def filter_movies():
    genre = selected_genre.get().lower()
    df = data.copy()

    genre_map = {
        "documentary": "documentaries",
        "romance": "romantic",
    }

    if genre != "all":
        genre = genre_map.get(genre, genre)

        df = df[
            df["listed_in"]
            .str.lower()
            .str.contains(genre, na=False)
        ]

    show_results(df)


# =========================
# FAVORITES (SELECT FROM LISTBOX)
# =========================
def add_favorite():
    try:
        selected = movie_listbox.get(movie_listbox.curselection())

        if selected not in favorites:
            favorites.append(selected)
            save_favorites()
            result.insert(tk.END, f"\n❤️ Added: {selected}\n")
        else:
            result.insert(tk.END, "\n⚠️ Already in favorites\n")

    except:
        result.insert(tk.END, "Select a movie first ❌\n")


def show_favorites():
    result.delete(1.0, tk.END)

    if not favorites:
        result.insert(tk.END, "No favorites yet ❌")
        return

    for f in favorites:
        result.insert(tk.END, f"❤️ {f}\n")


# =========================
# EXIT SAVE
# =========================
def on_close():
    save_favorites()
    app.destroy()


# =========================
# UI
# =========================
app = tk.Tk()
app.title("Netflix Pro Analyzer")
app.geometry("600x750")
app.configure(bg="#141414")

app.iconbitmap("netflix_43786.ico")

app.protocol("WM_DELETE_WINDOW", on_close)

# TITLE
tk.Label(
    app,
    text="Netflix Pro Analyzer",
    font=("Helvetica", 18, "bold"),
    fg="#E50914",
    bg="#141414"
).pack(pady=10)

# SEARCH
tk.Label(app, text="🔍 Search Movie", fg="white", bg="#141414").pack()

search_entry = tk.Entry(app, font=("Arial", 12), justify="center")
search_entry.pack(pady=5)

tk.Button(app, text="Search 🎬", command=search_movie,
          width=25, bg="#E50914", fg="white", bd=0).pack(pady=5)

# LISTBOX
tk.Label(app, text="🎬 Results", fg="white", bg="#141414").pack()

movie_listbox = tk.Listbox(app, width=50, height=10)
movie_listbox.pack(pady=5)

movie_listbox.bind("<<ListboxSelect>>", show_movie_details)

# GENRE
tk.Label(app, text="🎭 Select Genre", fg="white", bg="#141414").pack()

genres = ["All", "Action", "Comedy", "Drama", "Horror", "Documentary", "Romance", "Thriller"]

selected_genre = tk.StringVar()
selected_genre.set("All")

tk.OptionMenu(app, selected_genre, *genres).pack(pady=5)

tk.Button(app, text="Apply Filter 🎯", command=filter_movies,
          width=25, bg="#E50914", fg="white", bd=0).pack(pady=5)

# FAVORITES
tk.Button(app, text="Add Favorite ❤️", command=add_favorite,
          width=25, bg="#E50914", fg="white", bd=0).pack(pady=5)

tk.Button(app, text="Show Favorites ⭐", command=show_favorites,
          width=25, bg="#E50914", fg="white", bd=0).pack(pady=5)

# RESULT
result = tk.Text(app, height=18, width=60,
                 bg="#222222", fg="white",
                 font=("Arial", 11))
result.pack(pady=10)

app.mainloop()