from huggingface_hub import HfApi
import os

TOKEN = os.environ.get("HF_TOKEN") or input("HF 토큰 입력: ")

api = HfApi()
api.upload_folder(
    folder_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "data"),
    repo_id="youheetae/quanta-data",
    repo_type="dataset",
    token=TOKEN,
)
print("업로드 완료!")
