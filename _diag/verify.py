import httpx
for r in ['nocodb/nocodb', 'expressjs/express']:
    d = httpx.post('https://hydrascan.shadrakbessanh.me/api/scan',
                   json={'repoUrl': 'https://github.com/' + r}, timeout=200).json()
    print("%-18s isCompromised=%s  malware=%d  vulnerable=%d  score=%d" % (
        r, d.get('isCompromised'), len(d.get('compromised', [])),
        len(d.get('vulnerable', [])), d.get('exposureScore', 0)))
