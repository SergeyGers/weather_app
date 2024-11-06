
# Weather App

A Flask-based weather application that allows users to search for a city and view weather forecasts. The app uses geolocation to find cities and provides a 7-day forecast, including daily temperature ranges, weather conditions, and average humidity. The app also includes caching to reduce API calls and stores a history of searched cities in a JSON file.

## Features

- **Search**: Get weather forecasts by city name.
- **Weather Forecast**: 7-day forecast with max/min temperatures, humidity, and weather conditions.
- **Caching**: Uses `requests_cache` to reduce API calls.
- **Retry Requests**: Automatically retries failed API requests for reliability.
- **Search History**: Saves a history of searches in a JSON file.
- **Customizable UI**: Background color can be set via environment variables.

## Technologies Used

- **Flask**: Web framework for handling routes and rendering templates.
- **Requests**: For handling HTTP requests to weather and geolocation APIs.
- **Requests Cache**: Caches API requests to reduce redundant calls.
- **Retry Requests**: Retries failed API requests.
- **dotenv**: Loads environment variables from a `.env` file.
- **JSON**: Saves search history in a local file (`search_history.json`).

## Setup and Installation

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Install dependencies**:
    Ensure you have Python 3.7+ and `pip` installed, then install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` file**:
    Add your environment variables. For example:
    ```
    BG_COLOR=#ADD8E6
    ```

4. **Run the app**:
    ```bash
    python web_app.py
    ```
   The app will run on `http://0.0.0.0:5005`.

## Usage

- **Home Page** (`/`): Enter a city name to get the weather forecast. Results include max and min temperatures, humidity, and a weather summary for each day.
- **History Page** (`/history`): Displays a history of previous searches with timestamps.

## File Structure

- `web_app.py`: Main application file.
- `templates/`: Contains HTML files for the app (e.g., `index.html`, `history.html`).
- `.env`: Stores environment variables for background color and other configurations.
- `search_history.json`: Stores search history data in JSON format.

## Dependencies

- **Flask**
- **requests**
- **requests-cache**
- **retry-requests**
- **dotenv**

## Environment Variables

- `BG_COLOR`: Set the background color for the application (e.g., `#FFFFFF` for white).

## Troubleshooting

- **Caching Issues**: If cached data is causing issues, delete the cache in `/tmp/.cache`.
- **History File**: If `search_history.json` becomes corrupted, you can delete it to start fresh.

## Future Improvements

- **User Authentication**: Add user accounts to store personal search history.
- **Extended Weather Data**: Provide more detailed hourly forecasts.
- **Database Support**: Move history from JSON to a database for scalability.

## License

This project is licensed under the MIT License.
