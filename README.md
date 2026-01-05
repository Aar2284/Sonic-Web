
# 🕸️ Sonic Web 🎵

[![Python Badge](https://img.shields.io/badge/Python-3.11-lightgray?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB)](https://www.python.org/)
[![Flask Badge](https://img.shields.io/badge/Flask-3.1.2-lightgray?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000)](https://flask.palletsprojects.com/)
[![HTML5 Badge](https://img.shields.io/badge/HTML-5-lightgray?style=for-the-badge&logo=html5&logoColor=white&labelColor=E34F26)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS3 Badge](https://img.shields.io/badge/CSS-3-lightgray?style=for-the-badge&logo=css3&logoColor=white&labelColor=1572B6)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Spotify Badge](https://img.shields.io/badge/Spotify-API-lightgray?style=for-the-badge&logo=spotify&logoColor=white&labelColor=1DB954)](https://developer.spotify.com/)

Sonic Web is a dynamic web application that weaves a visual network of interconnected artists straight from the Spotify universe 🎶. Input an artist and watch as it maps out a graph of related musicians, offering a unique and interactive way to discover new music.

## ✨ Features

*   **Artist Search:** Easily search for any artist on Spotify.
*   **Interactive Network Graph:** Visualize the connections between an artist and their collaborators.
*   **Dynamic UI:** The graph is rendered dynamically and is fully interactive (zoom, pan, click).
*   **Artist Insights:** Click on a collaborator to see the tracks they've worked on together.
*   **Music Trend Charts:** View charts on an artist's track popularity and audio features over the years.
*   **Responsive Design:** A clean interface that works on different screen sizes.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   [Python 3.11](https://www.python.org/downloads/)
*   `pip` (Python package installer)

### ⚙️ Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/sonic-web.git
    cd sonic-web
    ```

2.  **Create and activate a virtual environment:**
    *   On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    *   Create a file named `.env` in the root of the project.
    *   You will need to get your own Spotify API credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    *   Add your credentials to the `.env` file like this:
        ```
        SPOTIPY_CLIENT_ID='Your_Spotify_Client_Id'
        SPOTIPY_CLIENT_SECRET='Your_Spotify_Client_Secret'
        ```

### ▶️ Running the Application

Once the setup is complete, you can run the application with the following command:

```sh
flask run
```

Open your web browser and navigate to `http://127.0.0.1:5000` to see the application in action!

## 🛠️ Technologies Used

*   **Backend:**
    *   [Flask](https://flask.palletsprojects.com/): A lightweight WSGI web application framework.
    *   [Spotipy](https://spotipy.readthedocs.io/): A lightweight Python library for the Spotify Web API.
    *   [NetworkX](https://networkx.org/): A Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
    *   [Pyvis](https://pyvis.readthedocs.io/): A Python library for creating interactive network visualizations.
    *   [Pandas](https://pandas.pydata.org/): A fast, powerful, flexible, and easy-to-use open-source data analysis and manipulation tool.

*   **Frontend:**
    *   HTML5
    *   CSS3
    *   JavaScript

## 📂 Project Structure

```
sonic-web/
├── .env                # Environment variables (Spotify credentials)
├── artist_network.py   # Main Flask application
├── requirements.txt    # Project dependencies
├── static/
│   └── artist_network.css  # Styles for the web page
├── templates/
│   └── artist_network.html # Main HTML template
└── README.md           # You are here!
```

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgements

*   [Spotify](https://www.spotify.com) for their amazing API.
*   The developers of the open-source libraries used in this project.
