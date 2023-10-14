# CASELAW Semantic Search Engine

---

## Installation
```bash
virtualenv -p python venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
streamlit run app.py
```

## Steps to set up Elasticsearch on Google Colab
```bash
!pip install pyngrok
```
```python
import os
from pyngrok import ngrok
from subprocess import Popen, PIPE, STDOUT
```
```python
def setup_elastic(version : str = "7.15.0") -> None:
    !wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-{version}-linux-x86_64.tar.gz -q
    !tar -xzf elasticsearch-{version}-linux-x86_64.tar.gz
    !rm elasticsearch-{version}-linux-x86_64.tar.gz
    !chown -R daemon:daemon elasticsearch-{version}

    Popen(
        [f'elasticsearch-{version}/bin/elasticsearch'],
        stdout=PIPE,
        stderr=STDOUT,
        preexec_fn=lambda: os.setuid(1)  # as daemon
        )

def setup_ngrok(port : int = 9200) -> None:
    ngrok.kill()
    ngrok.set_auth_token("<NGROK_AUTH_TOKEN>")
    print(ngrok.connect(port))
```

```python
setup_elastic()
setup_ngrok()
```