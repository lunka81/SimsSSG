from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="nguyenkhoa/celeba-spoof-for-face-antispoofing-test",
    repo_type="dataset",
    local_dir="data/celeba-spoof"
)

print("Downloaded to", path)