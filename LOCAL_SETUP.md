# 🚀 Local Setup Guide

This guide helps you run the PRMES Evaluation System on your local machine.

## 🎯 Quick Start

### Method 1: Easy Launch (Recommended)
```bash
# Run the interactive launcher
python run_local.py
```

### Method 2: Batch File (Windows)
```bash
# Double-click or run from command line
run_local.bat
```

### Method 3: Direct Launch
```bash
# Standard Flask app launch
python app.py
```

## 🌐 Accessing the App

Once started, the app will be available at:
- **Local URL:** http://127.0.0.1:5000
- **Localhost:** http://localhost:5000

## 🔒 Security

The app is configured to run on localhost only (`127.0.0.1`) for security:
- ✅ Only accessible from your local machine
- ✅ No external network access
- ✅ Safe for development and local use

## 📁 Features

- Upload Excel files with student evaluation data
- Generate individual PDF reports
- Create comprehensive summary PDFs
- View students by group, guide, or individually
- Export data to CSV format

## 🛠️ Requirements

- Python 3.7+
- Flask and dependencies (see requirements if available)
- Modern web browser

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is busy, you can modify the port in:
- `app.py` (line 631): Change `port=5000` to another port
- `run_local.py` (line 54): Update the port number

### Database Issues
If you encounter database errors:
1. Delete `app.db` file
2. Restart the application (it will recreate the database)

### Missing Dependencies
Install required packages:
```bash
pip install flask sqlalchemy reportlab openpyxl python-dotenv pymysql
```

## 🚀 Getting Started

1. Start the application using one of the methods above
2. Upload your Excel file with student data
3. Navigate through different views (Individual, Group-wise, Guide-wise)
4. Generate and download PDF reports as needed

## 📞 Support

If you encounter any issues, check the console output for error messages and ensure all dependencies are installed.