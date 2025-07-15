# URLs
EID_START = "https://weryfikator.mobywatel.gov.pl/web/api/verifications"
EID_DATA_PULL = "https://weryfikator.mobywatel.gov.pl/web/api/verifications/{session_uuid}/data/encrypt-and-get"

# Browser headers
LEGIT_BROWSER_HEADERS = {
    "Host": "weryfikator.mobywatel.gov.pl",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "https://weryfikator.mobywatel.gov.pl",
    "Connection": "keep-alive",
    "Referer": "https://weryfikator.mobywatel.gov.pl/verification-process",
}
