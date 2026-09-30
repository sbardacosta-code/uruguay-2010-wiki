"""Loopback-only Ollama client with explicit identity and measured call metadata."""
import json
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

class ModelError(RuntimeError):pass

def ollama_rss():
    try:
        output=subprocess.check_output(['ps','-axo','rss=,comm='],text=True,stderr=subprocess.DEVNULL)
        return sum(int(line.split(None,1)[0])*1024 for line in output.splitlines() if 'ollama' in line.split(None,1)[-1].lower())
    except (OSError,subprocess.SubprocessError,ValueError):return None

class LocalModel:
    def __init__(self,config):
        self.config=config;self.base=config['ollama_url'].rstrip('/')
        parsed=urllib.parse.urlparse(self.base)
        if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.username or parsed.password:
            raise ModelError('Only http://127.0.0.1 is allowed for the local runtime.')
        if 'cloud' in config['model'].lower():raise ModelError('Cloud models are not allowed.')
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def request(self,path,payload=None,timeout=300):
        request=urllib.request.Request(self.base+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(request,timeout=timeout) as response:return json.load(response)
        except urllib.error.HTTPError as exc:raise ModelError('Ollama error: '+exc.read().decode()[:600]) from exc
        except (urllib.error.URLError,TimeoutError,OSError) as exc:raise ModelError('Local Ollama unavailable. Run ./scripts/start_ollama.sh and download the configured model. '+str(exc)) from exc
    def identity(self):
        name=self.config['model'];show=self.request('/api/show',{'model':name})
        if show.get('remote_host') or show.get('remote_model'):raise ModelError('The selected model is a remote model; local weights are required.')
        tags=self.request('/api/tags');tag=next((m for m in tags['models'] if m['name']==name),None)
        if not tag:raise ModelError('Local model weights are missing: '+name)
        return dict(model=name,digest=tag['digest'],download_bytes=tag['size'],details=show.get('details'),runtime=self.request('/api/version'),model_info=show.get('model_info'),parameters=show.get('parameters'),local_endpoint=self.base)
    def chat(self,messages,schema=None,max_tokens=None):
        identity=self.identity();samples=[];stop=threading.Event()
        def sample():
            while not stop.is_set():
                value=ollama_rss()
                if value is not None:samples.append(value)
                stop.wait(.3)
        worker=threading.Thread(target=sample,daemon=True);worker.start();start=time.perf_counter()
        payload=dict(model=self.config['model'],messages=messages,stream=False,think=False,keep_alive='15m',options=dict(temperature=0,num_ctx=self.config['context_tokens'],num_predict=max_tokens or self.config['answer_tokens'],seed=42))
        if schema:payload['format']=schema
        try:result=self.request('/api/chat',payload)
        finally:stop.set();worker.join(timeout=1)
        stats={key:result.get(key) for key in ['total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration','done_reason']}
        stats.update(wall_seconds=round(time.perf_counter()-start,3),ollama_process_rss_peak_bytes=max(samples) if samples else None,context_tokens=self.config['context_tokens'])
        stats['loaded_models']=self.request('/api/ps').get('models',[])
        return result['message']['content'],dict(identity=identity,measurements=stats)
