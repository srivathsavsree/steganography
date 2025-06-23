# Steganography Image Encoder/Decoder

This project implements a simple steganography tool that allows users to hide text messages within PNG images and extract those messages from the images.

## Project Structure

- **stego/image.py**: Contains the logic for encoding and decoding messages in PNG images.
  - `encode_image(image: Image, message: str) -> Image`: Embeds a text message into a PNG image.
  - `decode_image(image: Image) -> str`: Extracts the hidden message from a PNG image.

- **routes/encode.py**: Defines a FastAPI route `/encode/image`.
  - Accepts a PNG file upload and a text message via FormData.
  - Calls `stego.image.encode_image()` to embed the message.
  - Returns the resulting image file as a response.

- **routes/decode.py**: Defines a FastAPI route `/decode/image`.
  - Accepts a PNG image file.
  - Calls `stego.image.decode_image()` to extract the hidden message.
  - Returns the extracted text.

- **main.py**: The entry point of the FastAPI application.
  - Initializes the FastAPI app and includes the routes from the encode and decode modules.

- **requirements.txt**: Lists the dependencies required for the project, including FastAPI and any libraries needed for image processing (e.g., PIL or stepic).

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd backend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the FastAPI application:
   ```
   uvicorn main:app --reload
   ```

4. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Usage Examples

### Encode an Image

To encode a message into an image, send a POST request to `/encode/image` with the PNG file and the message.

### Decode an Image

To decode a message from an image, send a POST request to `/decode/image` with the PNG file. The response will contain the extracted message.