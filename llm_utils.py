import json
from typing import List, Dict
import google.generativeai as genai

try:
    from openai import OpenAI as _OpenAI
    _OPENAI_NEW=True
except Exception:
    import openai as _openai_legacy
    _OPENAI_NEW=False


def pick_highlights(transcription: str, provider: str, api_key: str, max_clips: int, min_len: int, max_len: int) -> List[Dict]:
    sys = (
        f"You are an expert at finding viral video moments. Return up to {max_clips} segments between {min_len} and {max_len} seconds "
        "as JSON array with keys start,end,content. Only return JSON. If none, return []."
    )
    if provider == 'OpenAI':
        if _OPENAI_NEW:
            client = _OpenAI(api_key=api_key)
            r = client.chat.completions.create(
                model='gpt-4o-mini', temperature=0.5,
                messages=[{'role':'system','content':sys},{'role':'user','content':transcription}]
            )
            txt = r.choices[0].message.content
        else:
            _openai_legacy.api_key = api_key
            r = _openai_legacy.ChatCompletion.create(
                model='gpt-4o-2024-05-13', temperature=0.5,
                messages=[{'role':'system','content':sys},{'role':'user','content':transcription}]
            )
            txt = r.choices[0].message.content
    else:
        genai.configure(api_key=api_key)
        m = genai.GenerativeModel('gemini-2.5-flash')
        txt = m.generate_content(sys + '\n\n' + transcription).text
    txt = (txt or '').strip().replace('```','').replace('json','').strip()
    try:
        arr = json.loads(txt) if txt else []
    except Exception:
        arr = []
    out = []
    for h in arr:
        try:
            s = float(h.get('start', 0)); e = float(h.get('end', 0))
            if e > s and min_len <= e - s <= max_len:
                out.append({'start': s, 'end': e, 'content': h.get('content','')})
        except Exception:
            continue
    return out


def generate_titles_from_highlights(highs: List[Dict], provider: str, api_key: str) -> List[str]:
    if not highs:
        return []
    prompt = 'Create ultra-short (<=40 chars), high-energy titles with emojis for these clip summaries. Return JSON array of strings only.\n' + \
             json.dumps([h.get('content','') for h in highs])
    try:
        if provider == 'OpenAI':
            if _OPENAI_NEW:
                client = _OpenAI(api_key=api_key)
                r = client.chat.completions.create(model='gpt-4o-mini', temperature=0.7, messages=[{'role':'user','content':prompt}])
                txt = r.choices[0].message.content
            else:
                _openai_legacy.api_key = api_key
                r = _openai_legacy.ChatCompletion.create(model='gpt-4o-2024-05-13', temperature=0.7, messages=[{'role':'user','content':prompt}])
                txt = r.choices[0].message.content
        else:
            genai.configure(api_key=api_key)
            m = genai.GenerativeModel('gemini-2.5-flash')
            txt = m.generate_content(prompt).text
        txt = (txt or '').strip().replace('```','').replace('json','').strip()
        arr = json.loads(txt) if txt else []
        return [str(a)[:60] for a in arr]
    except Exception:
        return [h.get('content','Clip')[:40] for h in highs]
