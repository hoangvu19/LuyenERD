import json
from http import HTTPStatus

def normalize(s):
    if not s: return ''
    try:
        s = s.lower()
    except Exception:
        pass
    return s

def token_score(ref, cand):
    rset = set([w for w in normalize(ref).split() if len(w)>2])
    cset = set([w for w in normalize(cand).split() if len(w)>2])
    if not rset and not cset: return 0
    inter = len(rset & cset)
    uni = len(rset | cset)
    return int(round(inter/uni*100))

def handler(req):
    # Vercel's Python runtime passes the raw request body as req.get_data()
    try:
        data = json.loads(req.get_data().decode('utf-8'))
    except Exception:
        return ({'error':'invalid json'}, HTTPStatus.BAD_REQUEST)
    ref = data.get('answer','') or ''
    cand = data.get('response','') or ''
    score = token_score(ref, cand)
    verdict = 'Đạt' if score>=70 else 'Chưa đạt'
    feedback = f'Điểm tương đồng: {score}%'
    tips = []
    if ref:
        kws = [w for w in ref.split() if len(w)>3][:6]
        if kws:
            tips.append('Học theo nhóm từ/ý: ' + ', '.join(kws))
    tips.append('Lặp lại theo phương pháp spaced repetition và viết lại các ý chính.')
    return ({'score':score,'verdict':verdict,'feedback':feedback,'tips':tips}, HTTPStatus.OK)

def main(request):
    body, status = handler(request)
    from flask import jsonify, make_response
    resp = make_response(jsonify(body), status)
    # allow CORS
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp
