#Step-by-Step Instructions to Set Up AI Chat App

1. Set Up a Virtual Environment
   - Open Command Prompt (`Win + R`, type `cmd`).
   - Navigate to the project directory:
     cd C:\Projects\FinalYearProject
   - Create a virtual environment:
     python -m venv venv
   - Activate the virtual environment:
     venv\Scripts\activate
     
2. Upgrade pip
   - Upgrade `pip` inside the virtual environment:
     python -m pip install --upgrade pip

3. Install Dependencies
   - Install all required packages:
     pip install -r requirements.txt

4. Copy Mistral to Mistral directory  

5. Launch the Application
   - Run the application using Streamlit:
     streamlit run app.py
   - This will open the chat application in your default web browser.

