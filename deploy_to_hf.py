import os
from huggingface_hub import HfApi

# Leer el token directamente desde .env
token = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("HF_TOKEN="):
                token = line.strip().split("=")[1]
                break

if not token:
    print("Error: No se ha encontrado HF_TOKEN en el archivo .env")
    exit(1)

api = HfApi(token=token)
repo_id = "manteca24/beyond-lotka-volterra"

archivos_a_subir = [
    ("visualize.py", "visualize.py"),
    ("model.py", "model.py"),
    ("agent.py", "agent.py"),
    ("hf_space/Dockerfile", "Dockerfile"),
    ("hf_space/requirements.txt", "requirements.txt")
]

print(f"Subiendo archivos al Space {repo_id}...")
for local_path, hf_path in archivos_a_subir:
    if os.path.exists(local_path):
        print(f" -> Subiendo {local_path} como {hf_path}...")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=hf_path,
            repo_id=repo_id,
            repo_type="space"
        )
    else:
        print(f" -> Advertencia: No se encontró {local_path}")

print("¡Despliegue completado con éxito! Hugging Face está reconstruyendo el contenedor.")
