# AniList Web App
#### Video Demo: https://youtu.be/LcVp097ULek
#### Description:

The AniList Web App is a web application tailored for anime enthusiasts. It provides a platform for users to explore various anime, mark their favorites for easy access, and engage in lively discussions by sharing their thoughts through comments.

## Key Features

- **Anime Browsing**: Browse a vast collection of anime titles and view basic information, including title and images.

- **Adding to Favorites**: Easily mark anime as favorites for quick access and tracking.

- **Anime Discussions**: Engage with the community by leaving comments and participating in discussions regarding your favorite anime.

## Technical Details

- **Use of Flask and Python**: The application is built using Python with the Flask framework, providing power and efficiency for creating web applications.

- **Working with SQLite Database**: SQLite database is used to store data about anime and users, providing simplicity and convenience.

- **Integration with External API**: The application interacts with an external API to obtain important information about anime, such as title, images, and other details.

- **Client Interaction through AJAX**: To ensure dynamism and speed, comments on anime and adding to favorites are implemented using AJAX in JavaScript.

- **Usage of HTML, CSS, and Bootstrap**: HTML and CSS are used to create the web application's interface, and the Bootstrap framework is utilized to enhance the appearance and layout of elements.

### Utilizing an API to Fetch Anime Data

The application leverages an external API to fetch comprehensive anime-related data, including titles and images. This data is then used to display anime content on the homepage and other relevant pages.

### Comments Functionality via JavaScript

The commenting feature is seamlessly implemented using JavaScript, allowing users to leave comments without requiring a page reload. This significantly enhances the convenience and speed of interaction within the application.

## Setup Instructions

1. Open a terminal or command prompt and navigate to the project folder using the `cd /path_to_project_folder` command.

2. Run the Flask application using the following command:

    ```bash
    flask run
    ```