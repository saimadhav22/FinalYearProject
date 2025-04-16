#Step-by-Step Instructions to Set Up AI Chat App
1. Download the Project Folder
   - Download the entire folder you uploaded to Google Drive.
   - Extract it to a directory of your choice, such as `C:\Projects\AIChatApp2`.

2. Set Up a Virtual Environment
   - Open Command Prompt (`Win + R`, type `cmd`).
   - Navigate to the project directory:
     cd C:\Projects\AIChatApp2
   - Create a virtual environment:
     python -m venv venv
   - Activate the virtual environment:
     venv\Scripts\activate
     
3. Upgrade pip
   - Upgrade `pip` inside the virtual environment:
     python -m pip install --upgrade pip

4. Install Dependencies
   - Install all required packages:
     pip install -r requirements.txt

6. Copy Mistral to Mistral directory  

7. Launch the Application
   - Run the application using Streamlit:
     streamlit run app.py
   - This will open the chat application in your default web browser.

