# HungerHeal - Food Waste Reduction Platform

HungerHeal is a web application that connects food donors (restaurants, bakeries, grocery stores) with food recipients (NGOs, shelters, individuals) to reduce food waste and help feed those in need.

## Features

- 🍲 **Food Posting**: Businesses can post surplus food with location, quantity, and expiry information
- 📍 **Interactive Map**: Real-time map showing available food locations
- 🔍 **Address Search**: Search for food by location
- ⏰ **Expiry Tracking**: Automatic removal of expired food posts
- 🛡️ **Safety Guidelines**: Built-in safety recommendations for donors and recipients
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### 1. Firebase Configuration

To use Firebase for data storage:

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Create a service account:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

4. Configure secrets in `.streamlit/secrets.toml`:
   ```toml
   [firebase]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
   ```

### 2. Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run project/app.py
   ```

### 3. Deployment

The app can be deployed on Streamlit Cloud:

1. Push your code to GitHub
2. Connect your repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your Firebase secrets in the Streamlit Cloud secrets management

## Development Mode

If Firebase is not configured, the app will automatically use in-memory storage with sample data for testing purposes. This allows you to explore the functionality without setting up Firebase.

## Technologies Used

- **Streamlit**: Web application framework
- **Firebase Firestore**: Database for storing food posts
- **Folium**: Interactive maps
- **OpenStreetMap Nominatim**: Geocoding service
- **Python**: Backend logic

## Safety Features

- Built-in safety guidelines for food donors and recipients
- Verification system for trusted users
- Expiry time tracking to ensure food safety
- Public meeting place recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue on the GitHub repository.