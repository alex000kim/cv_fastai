import requests
import zipfile
from pathlib import Path
from tqdm import tqdm

DATASET_NAME2GDRIVE_ID = {
    'DEEP_GLOBE_LAND_COVER': '1Mk1q2XtgARVpamRxrjaNajMXsg2qHTkn',
    'DEEP_GLOBE_ROAD_EXTRACTION': '1WB3VZ8qwNaVTsAw7qcMBXUYN9Hb9BKKZ',
    'FISH': '1iZsnVTxc3jg-LChJr01nUTQOdrWok-th',
    'PLANET': '1k-13ankHH3hMdUPV3JvnEoPPXuQnZmBu'
    
}

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            with tqdm(unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        bar.update(CHUNK_SIZE)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    
    
    
def download_dataset(dataset_name, dest_dir):
    fpath = Path(dest_dir)/f'{dataset_name}.zip'
    if not fpath.exists():
        try:
            download_file_from_google_drive(DATASET_NAME2GDRIVE_ID[dataset_name], 
                                            fpath)
            return fpath
        except KeyError:
            raise Exception(f'The following sample datasets are available: {list(DATASET_NAME2GDRIVE_ID.keys())}')
    else:
        print(f'File exists: {fpath}')
        return fpath
        
        
def extract_zip(fpath, dir_path=None):
    dir_path = Path(fpath).parent/Path(fpath).stem
    if not dir_path.exists():
        with zipfile.ZipFile(fpath, 'r') as zip_ref:
            zip_ref.extractall(dir_path)
    else:
        print(f'Directory exists: {dir_path}')
    return dir_path
    
  