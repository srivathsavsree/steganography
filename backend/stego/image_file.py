import os
import uuid
import mimetypes

def encode_image_with_file(input_image_path: str, file_path: str, output_image_path: str) -> None:
    # Append file bytes after IEND chunk of PNG
    with open(input_image_path, 'rb') as img_f, open(file_path, 'rb') as file_f:
        img_data = img_f.read()
        file_data = file_f.read()
    # Find IEND chunk (last 12 bytes of PNG)
    iend = img_data.rfind(b'IEND')
    if iend == -1:
        raise ValueError('Invalid PNG file')
    # Insert file after IEND chunk
    new_img = img_data + b'FILESEP' + file_data
    with open(output_image_path, 'wb') as out_f:
        out_f.write(new_img)

def decode_file_from_image(stego_image_path: str, output_dir: str) -> str:
    with open(stego_image_path, 'rb') as f:
        data = f.read()
    sep = b'FILESEP'
    idx = data.find(sep)
    if idx == -1:
        raise ValueError('No file hidden in image')
    file_data = data[idx+len(sep):]
    # Guess file type
    ext = mimetypes.guess_extension(mimetypes.guess_type('file')[0] or '') or '.bin'
    output_path = os.path.join(output_dir, f"extracted_{uuid.uuid4()}{ext}")
    with open(output_path, 'wb') as out_f:
        out_f.write(file_data)
    return output_path
