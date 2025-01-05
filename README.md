# Gemini Dynamo

The Gemini Dynamo project integrates frontend and backend technologies to efficiently parse and organize lengthy YouTube transcripts, revolutionizing study processes and enhancing digital learning experiences.

The project uses **DynamoCards**, an open-source tool, to tackle the arduous task of parsing lengthy YouTube transcripts with its **Semantic Extraction Algorithm (SEA)**. The goal is to streamline the study process for students and educators by swiftly identifying and organizing key concepts and terms within university lectures and other lengthy video content. DynamoCards empowers users to distill hours of lecture material into concise, digestible insights, enhancing classroom instruction and improving study habits.

---

## Features

- Parse YouTube transcripts into meaningful summaries.
- Generate flashcards for quick learning and retention.
- Seamlessly integrates frontend and backend with Dockerized deployment.
- Optimized for educational and professional learning environments.

---

## How to Run This Project

### Prerequisites

1. **Install Docker**: Ensure Docker is installed on your system.
2. **Install Node.js and npm**: Required for the frontend.
3. **Install Python**: Required for the backend and package installation.

---

### Procedure

#### Step 1: Clone the Repository
```bash
git clone https://github.com/jayshrivastava0/Gemini_Dynamo.git
cd Gemini_Dynamo
```

---

#### Step 2: Create a Docker Image
1. Ensure you are in the project root directory.
2. Build the Docker image using the provided `Dockerfile`:
   ```bash
   docker build -t gemini_dynamo_image .
   ```
3. Start a Docker container:
   ```bash
   docker run -d -p 8000:8000 -p 5173:5173 --name gemini_dynamo_container gemini_dynamo_image
   ```

---

#### Step 3: Backend Setup
1. Access the container terminal:
   ```bash
   docker exec -it gemini_dynamo_container /bin/bash
   ```
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the backend:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

---

#### Step 4: Frontend Setup
1. In a new terminal, enter the container:
   ```bash
   docker exec -it gemini_dynamo_container /bin/bash
   ```
2. Navigate to the frontend directory:
   ```bash
   cd frontend/dynamocards
   ```
3. Start the frontend:
   ```bash
   npm run dev -- --host 0.0.0.0 --port 5173
   ```

---

#### Step 5: Access the Application
1. Open the following links in your browser:
   - **Backend**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Frontend**: [http://localhost:5173/](http://localhost:5173/)
   
2. Use the backend API to upload a YouTube link for parsing:
   - Navigate through the **backend documentation** ([http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)).
   - Replace the placeholder URL `https://example.com/` with any YouTube link (preferably with captions).
   - Click **Execute** to trigger the API call.
   - Check for a **Code 200** response indicating success.

3. Use the frontend interface to generate flashcards:
   - Input the same YouTube link used in the backend.
   - Click **Generate Flashcards** to create summaries.

---

## Screenshots

1. **Backend API Documentation**  
   ![Backend API](https://github.com/philliphjhuang/GeminiDynamo/assets/30792325/db3f5e52-9cdc-48d7-a262-1f458ee88604)

2. **Flashcard Interface**  
   ![Frontend Interface](https://github.com/philliphjhuang/GeminiDynamo/assets/30792325/3a0050cf-4e47-45db-960d-233e1c34aa83)

---

## Troubleshooting

1. **Error Code 500**: If the backend fails to parse the video, retry with a different YouTube link or re-execute the API call.
2. **Docker Issues**: Ensure Docker is running and the ports (8000, 5173) are not blocked.
3. **Package Installation Failures**: Verify the Python environment and npm installations are correct.

---

## Contributions

Contributions are welcome! Feel free to submit pull requests or raise issues for feature enhancements or bug fixes.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
